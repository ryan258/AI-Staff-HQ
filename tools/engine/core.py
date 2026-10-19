"""Core agent factory and orchestration."""

from typing import Optional
from pathlib import Path
from dataclasses import asdict, is_dataclass
import fcntl
import json
import os
import re
import tempfile
import time
from datetime import datetime, timezone
import yaml
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.agents import create_agent

from .schemas import SpecialistSchema
from .prompt import PromptBuilder
from .llm import ModelRouter
from .state import ConversationState
from .capabilities import read_file, write_file, list_directory, run_command
from .config import get_config
from .utils import build_semantic_run_filename, normalize_slug


class SpecialistQueryError(RuntimeError):
    """Raised when a specialist fails to produce a model response.

    Orchestration layers rely on this propagating so they can fall back to an
    alternative specialist instead of treating a failed call as a valid answer.
    """


class AgentExecutionError(SpecialistQueryError):
    """Backward-compatible specific error for an AI model invocation failure."""
    pass


_PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN(?: [A-Z0-9]+)* PRIVATE KEY-----.*?"
    r"-----END(?: [A-Z0-9]+)* PRIVATE KEY-----",
    re.IGNORECASE | re.DOTALL,
)
_BEARER_TOKEN = re.compile(r"(\bBearer\s+)[^\s\r\n]+", re.IGNORECASE)
_SECRET_ASSIGNMENT = re.compile(
    r"(\b(?:password|passwd|secret|token|api[_ -]?key|authorization)\b\s*[:=]\s*)"
    r"([^\s,;\r\n]+)",
    re.IGNORECASE,
)
_OPENROUTER_KEY = re.compile(r"\bsk-or-v1-[A-Za-z0-9_-]{12,}\b")
_OPENAI_KEY = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")


def redact_sensitive_text(value: str) -> str:
    """Remove common credential and private-key forms before persistence."""
    text = str(value)
    text = _PRIVATE_KEY_BLOCK.sub("[REDACTED_PRIVATE_KEY]", text)
    text = _BEARER_TOKEN.sub(r"\1[REDACTED_TOKEN]", text)
    text = _SECRET_ASSIGNMENT.sub(r"\1[REDACTED_SECRET]", text)
    text = _OPENROUTER_KEY.sub("[REDACTED_API_KEY]", text)
    text = _OPENAI_KEY.sub("[REDACTED_API_KEY]", text)
    return text


def redact_log_value(value):
    """Recursively redact strings before a structured log is serialized."""
    if isinstance(value, str):
        return redact_sensitive_text(value)
    if is_dataclass(value):
        return redact_log_value(asdict(value))
    if isinstance(value, dict):
        return {key: redact_log_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact_log_value(item) for item in value]
    if isinstance(value, Path):
        return redact_sensitive_text(str(value))
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return redact_sensitive_text(str(value))


def _extract_usage(response) -> dict:
    """Return provider usage metadata in a small, stable shape when present."""
    usage = getattr(response, "usage_metadata", None)
    if not isinstance(usage, dict):
        metadata = getattr(response, "response_metadata", None)
        usage = metadata.get("token_usage") if isinstance(metadata, dict) else None
    if not isinstance(usage, dict):
        return {}

    def integer(*names: str) -> int:
        for name in names:
            value = usage.get(name)
            if isinstance(value, (int, float)) and value >= 0:
                return int(value)
        return 0

    prompt_tokens = integer("input_tokens", "prompt_tokens")
    completion_tokens = integer("output_tokens", "completion_tokens")
    total_tokens = integer("total_tokens") or prompt_tokens + completion_tokens
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def _require_text(content, usage: dict) -> None:
    """Fail on a blank reply instead of passing it downstream as an answer.

    Reasoning models can spend the whole max_tokens budget thinking and
    return no visible text.
    """
    if isinstance(content, str) and not content.strip():
        raise ValueError(
            f"Model returned an empty reply (usage: {usage or 'unknown'}); "
            "max_tokens may be too low for a reasoning model."
        )


def _append_private_log(path: Path, header: str, entry: str) -> None:
    """Append a redacted log entry through one locked, mode-0600 replacement."""
    if path.parent.is_symlink():
        raise PermissionError(f"Refusing to write inside log symlink: {path.parent}")
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    lock_path = path.with_name(f".{path.name}.lock")
    if lock_path.is_symlink():
        raise PermissionError(f"Refusing to write through log lock symlink: {lock_path}")
    lock_flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    lock_fd = os.open(lock_path, lock_flags, 0o600)
    temp_path: Optional[Path] = None
    try:
        os.chmod(lock_path, 0o600)
        with os.fdopen(lock_fd, "r+", encoding="utf-8") as lock_file:
            lock_fd = -1
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            if path.is_symlink():
                raise PermissionError(f"Refusing to write through log symlink: {path}")
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            content = existing + (header if not existing else "") + entry
            fd, temp_name = tempfile.mkstemp(
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
            )
            temp_path = Path(temp_name)
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp_path, path)
            temp_path = None
            os.chmod(path, 0o600)
    finally:
        if lock_fd >= 0:
            os.close(lock_fd)
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def write_private_json_atomic(path: Path, payload) -> None:
    """Write redacted structured log data atomically with private permissions."""
    if path.parent.is_symlink():
        raise PermissionError(f"Refusing to write inside log symlink: {path.parent}")
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)

    lock_path = path.with_name(f".{path.name}.lock")
    if lock_path.is_symlink():
        raise PermissionError(f"Refusing to write through log lock symlink: {lock_path}")
    lock_flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    lock_fd = os.open(lock_path, lock_flags, 0o600)
    temp_path: Optional[Path] = None
    try:
        os.chmod(lock_path, 0o600)
        with os.fdopen(lock_fd, "r+", encoding="utf-8") as lock_file:
            lock_fd = -1
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            if path.is_symlink():
                raise PermissionError(f"Refusing to replace log symlink: {path}")
            fd, temp_name = tempfile.mkstemp(
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
            )
            temp_path = Path(temp_name)
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                json.dump(redact_log_value(payload), output, indent=2, default=str)
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp_path, path)
            temp_path = None
            os.chmod(path, 0o600)
    finally:
        if lock_fd >= 0:
            os.close(lock_fd)
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


class SpecialistAgent:
    """Executable agent from specialist YAML."""

    def __init__(
        self,
        yaml_path: Path,
        model_override: Optional[str] = None,
        temperature: Optional[float] = None,
        session_id: Optional[str] = None,
        tools: Optional[list] = None,
    ):
        # Load and validate YAML
        self.yaml_path = Path(yaml_path)
        with open(self.yaml_path) as f:
            data = yaml.safe_load(f)

        self.schema = SpecialistSchema(**data)
        self.config = get_config()
        self.session_id = session_id
        self.tools = tools
        self._log_file_path: Optional[Path] = None
        self.last_usage: dict = {}

        # Extract department from path
        self.department = self.yaml_path.parent.name if self.yaml_path.parent.name != 'staff' else None

        # Build system prompt
        prompt_builder = PromptBuilder(self.schema)
        self.system_prompt = prompt_builder.build_system_prompt()

        # Initialize model router
        router = ModelRouter()
        model = router.select_model(
            role=self.schema.core_identity.role,
            department=self.department,
            override=model_override
        )
        self.llm = router.create_llm(model, temperature)
        self.model_name = model

        # Initialize conversation state
        self.state = ConversationState(
            specialist_slug=self._get_specialist_slug(),
            session_id=session_id
        )

        # Initialize tool-calling agent if tools are provided
        self.agent_executor = None
        if self.tools:
            self.agent_executor = create_agent(self.llm, tools=self.tools)

        # Load existing session or start new
        if session_id:
            if not self.state.load():
                self.state.add_message(SystemMessage(content=self.system_prompt))
        else:
            self.state.add_message(SystemMessage(content=self.system_prompt))

    def _get_specialist_slug(self) -> str:
        """Get slug for this specialist (filename without .yaml)."""
        return self.yaml_path.stem

    def query(
        self,
        user_input: str,
        raise_errors: bool = True,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Execute single query."""
        # Add user message to conversation
        self.state.add_message(HumanMessage(content=user_input))

        start_time = time.time()
        response_text = ""
        
        try:
            if self.agent_executor:
                # Use ReAct agent with tools
                messages = list(self.state.messages)
                if not isinstance(messages[0], SystemMessage):
                     messages.insert(0, SystemMessage(content=self.system_prompt))
                elif messages[0].content != self.system_prompt:
                     # Ensure system prompt is current
                     messages[0] = SystemMessage(content=self.system_prompt)
                
                executor = self.agent_executor
                if max_tokens is not None:
                    executor = create_agent(
                        self.llm.model_copy(update={"max_tokens": max_tokens}),
                        tools=self.tools or [],
                    )
                result = executor.invoke({"messages": messages})
                
                # extracting the last message content
                last_message = result["messages"][-1]
                response_text = last_message.content
                self.last_usage = _extract_usage(last_message)
                _require_text(response_text, self.last_usage)
                
                # Update state with the NEW messages generated by the agent (skip what we sent)
                new_messages = result["messages"][len(messages):]
                for msg in new_messages:
                    self.state.add_message(msg)
                    
            else:
                # Invoke LLM with full conversation history
                if max_tokens is None:
                    response = self.llm.invoke(self.state.messages)
                else:
                    response = self.llm.invoke(self.state.messages, max_tokens=max_tokens)
                response_text = response.content
                self.last_usage = _extract_usage(response)
                _require_text(response_text, self.last_usage)
                # Extract and store response
                self.state.add_message(AIMessage(content=response_text))
                
        except Exception as e:
            error_msg = f"Failed to get response from AI model. Details: {str(e)}"
            if raise_errors:
                raise AgentExecutionError(error_msg) from e
            return f"⚠️ Error: {error_msg}"
        end_time = time.time()
        latency = end_time - start_time

        # Log interaction
        if self.config.enable_logging:
            self._log_interaction(user_input, response_text, latency)

        # Save state
        self.state.save()

        return response_text

    def _resolve_log_file_path(self, user_input: str) -> Path:
        """Resolve a stable, semantic markdown log path for this agent session."""
        if self._log_file_path is not None:
            return self._log_file_path

        session_id = self.state.session_id or "unknown_session"
        semantic_candidates = sorted(self.config.log_dir.glob(f"*__{session_id}.md"))
        if semantic_candidates:
            self._log_file_path = semantic_candidates[0]
            return self._log_file_path

        legacy_path = self.config.log_dir / f"{session_id}.md"
        if legacy_path.exists():
            self._log_file_path = legacy_path
            return self._log_file_path

        filename = build_semantic_run_filename(
            run_id=session_id,
            subject=redact_sensitive_text(user_input),
            workflow_name=self._get_specialist_slug(),
            extension=".md",
        )
        self._log_file_path = self.config.log_dir / filename
        return self._log_file_path

    def _log_interaction(self, user_input: str, response: str, latency: float):
        """Log API interaction to Markdown file."""
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.config.log_dir, 0o700)
        session_id = self.state.session_id or "unknown_session"
        log_file = self._resolve_log_file_path(user_input)
        timestamp = datetime.now(timezone.utc).isoformat()
        header = (
            f"# Session Log: {session_id}\n"
            f"**Specialist:** {redact_sensitive_text(self.schema.specialist)}\n"
            f"**Model:** {redact_sensitive_text(self.model_name)}\n"
            f"**Started:** {timestamp}\n"
            "---\n\n"
        )
        entry = (
            f"## Interaction @ {timestamp}\n"
            f"**Latency:** {latency:.2f}s\n\n"
            "### User\n"
            f"{redact_sensitive_text(user_input)}\n\n"
            "### Assistant\n"
            f"{redact_sensitive_text(response)}\n\n"
            "---\n\n"
        )
        _append_private_log(log_file, header, entry)

    def get_info(self) -> dict:
        """Get agent metadata."""
        return {
            "specialist": self.schema.specialist,
            "role": self.schema.core_identity.role,
            "department": self.department,
            "model": self.model_name,
            "motto": self.schema.motto,
            "slug": self._get_specialist_slug(),
            "session_id": self.state.session_id,
        }

    def get_conversation_length(self) -> int:
        """Get number of messages in conversation."""
        return len(self.state.messages)


def load_specialist(
    specialist_identifier: str,
    staff_dir: Path,
    **kwargs
) -> SpecialistAgent:
    """Load specialist by name or path.

    Args:
        specialist_identifier: Specialist slug (e.g. 'chief-of-staff') or full path
        staff_dir: Path to staff/ directory
        **kwargs: Additional arguments for SpecialistAgent

    Returns:
        Initialized SpecialistAgent

    Raises:
        FileNotFoundError: If specialist not found
    """

    # If it's a path, use directly
    specialist_path = Path(specialist_identifier)
    if specialist_path.exists():
        allow_external = kwargs.pop("allow_external_path", False)
        if not allow_external:
            try:
                specialist_path.resolve().relative_to(staff_dir.resolve())
            except ValueError:
                raise PermissionError(
                    f"Specialist path '{specialist_path}' must be inside staff directory '{staff_dir}'"
                )
        return SpecialistAgent(specialist_path, **kwargs)

    # Otherwise, search in staff directory
    slug = normalize_slug(specialist_identifier)

    # 2. Search by name (stem) in staff directory recursively
    # We prioritize exact name matches
    # 2. Search by name (stem) in staff directory recursively
    # We prioritize exact name matches
    for yaml_file in staff_dir.rglob("*.yaml"):
        if yaml_file.stem == slug:
            # Special case: Enable tools for Morphling
            tools = None
            if slug == "morphling":
                tools = [read_file, write_file, list_directory, run_command]
                
            return SpecialistAgent(yaml_file, tools=tools, **kwargs)

    # 3. Not found
    raise FileNotFoundError(
        f"Specialist '{specialist_identifier}' not found in {staff_dir}. "
        f"Use 'activate --list' to see available specialists."
    )
