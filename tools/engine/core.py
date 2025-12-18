"""Core agent factory and orchestration."""

from typing import Optional
from pathlib import Path
import json
import time
from datetime import datetime, timezone
import yaml
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from .schemas import SpecialistSchema
from .prompt import PromptBuilder
from .llm import ModelRouter
from .state import ConversationState
from .config import get_config


class SpecialistAgent:
    """Executable agent from specialist YAML."""

    def __init__(
        self,
        yaml_path: Path,
        model_override: Optional[str] = None,
        temperature: Optional[float] = None,
        session_id: Optional[str] = None,
    ):
        # Load and validate YAML
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        self.schema = SpecialistSchema(**data)
        self.yaml_path = yaml_path
        self.config = get_config()

        # Extract department from path
        self.department = yaml_path.parent.name if yaml_path.parent.name != 'staff' else None

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
        
        # Load existing session or start new
        if session_id:
            if not self.state.load():
                # Fallback if session not found, but we keep the ID for new file
                self.state.add_message(SystemMessage(content=self.system_prompt))
        else:
            self.state.add_message(SystemMessage(content=self.system_prompt))

    def _get_specialist_slug(self) -> str:
        """Get specialist slug from filename."""
        return self.yaml_path.stem

    def query(self, user_input: str) -> str:
        """Execute single query."""
        # Add user message to conversation
        self.state.add_message(HumanMessage(content=user_input))

        start_time = time.time()
        try:
            # Invoke LLM with full conversation history
            response = self.llm.invoke(self.state.messages)
            response_text = response.content
        except Exception as e:
            # Basic error handling for now - could be enhanced with specific API error checking
            error_msg = f"Error: Failed to get response from AI model. Details: {str(e)}"
            # We don't append the error to history, just return it so UI can display it
            # But maybe we should return it as a system message? 
            # For now, simply returning the strings.
            return f"⚠️ {error_msg}"
        
        end_time = time.time()
        latency = end_time - start_time

        # Extract and store response
        self.state.add_message(AIMessage(content=response_text))
        
        # Log interaction
        if self.config.enable_logging:
            self._log_interaction(user_input, response_text, latency)

        # Save state
        self.state.save()

        return response_text

    def _log_interaction(self, user_input: str, response: str, latency: float):
        """Log API interaction to Markdown file."""
        if not self.config.log_dir.exists():
            self.config.log_dir.mkdir(parents=True, exist_ok=True)
            
        session_id = self.state.session_id or "unknown_session"
        log_file = self.config.log_dir / f"{session_id}.md"
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create header if new file
        if not log_file.exists():
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"# Session Log: {session_id}\n")
                f.write(f"**Specialist:** {self.schema.specialist}\n")
                f.write(f"**Model:** {self.model_name}\n")
                f.write(f"**Started:** {timestamp}\n")
                f.write("---\n\n")

        # Append interaction
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"## Interaction @ {timestamp}\n")
            f.write(f"**Latency:** {latency:.2f}s\n\n")
            f.write("### User\n")
            f.write(f"{user_input}\n\n")
            f.write("### Assistant\n")
            f.write(f"{response}\n\n")
            f.write("---\n\n")

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
        return SpecialistAgent(specialist_path, **kwargs)

    # Otherwise, search in staff directory
    slug = specialist_identifier.lower().replace(' ', '-')

    # 2. Search by name (stem) in staff directory recursively
    # We prioritize exact name matches
    for yaml_file in staff_dir.rglob("*.yaml"):
        if yaml_file.stem == slug:
            return SpecialistAgent(yaml_file, **kwargs)

    # 3. Not found
    raise FileNotFoundError(
        f"Specialist '{specialist_identifier}' not found in {staff_dir}. "
        f"Use 'activate --list' to see available specialists."
    )
