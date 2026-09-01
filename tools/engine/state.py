"""Conversation state management and persistence."""

import json
import uuid
import shutil
import fcntl
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from langchain_core.messages import (
    BaseMessage, 
    HumanMessage, 
    AIMessage, 
    SystemMessage, 
    messages_to_dict, 
    messages_from_dict
)

import os
import re
import tempfile

from .config import get_config


def validate_identifier(identifier: str, name: str = "identifier") -> str:
    """Validate that identifier contains only alphanumeric characters, dashes, and underscores."""
    if not identifier or not isinstance(identifier, str):
        raise ValueError(f"Invalid {name}: must be a non-empty string")
    if not re.match(r"^[a-zA-Z0-9_-]+$", identifier):
        raise ValueError(f"Invalid {name} '{identifier}': contains forbidden characters or path separators")
    return identifier


class SessionLoadError(RuntimeError):
    """Base class for durable session load failures."""


class SessionCorruptError(SessionLoadError):
    """Raised when a session file cannot be safely parsed or validated."""


class SessionIdentityMismatchError(SessionLoadError):
    """Raised when a path contains a different session or specialist identity."""


class ConversationState:
    """Manages conversation history and persistence."""

    def __init__(
        self, 
        specialist_slug: str, 
        session_id: Optional[str] = None
    ):
        self.config = get_config()
        self.specialist_slug = validate_identifier(specialist_slug, "specialist_slug")
        if session_id:
            self.session_id = validate_identifier(session_id, "session_id")
        else:
            # Consistent format with GraphRunner: YYYYMMDD_HHMMSS_hex8
            # Use UTC to align with logs
            from datetime import timezone
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            short_uuid = uuid.uuid4().hex[:8]
            self.session_id = f"{timestamp}_{short_uuid}"
        self.messages: List[BaseMessage] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        # Snapshot used to merge appends made by another state instance while
        # this instance was working.  A process-wide lock alone prevents
        # torn replacements; the snapshot prevents lost messages.
        self._base_message_dicts: List[dict] = []
        
        # Ensure session directory exists and is contained within config.session_dir
        base_dir = self.config.session_dir.resolve()
        self.session_dir = (base_dir / self.specialist_slug).resolve()
        try:
            self.session_dir.relative_to(base_dir)
        except ValueError:
            raise ValueError(f"Specialist directory escapes session root: {self.specialist_slug}")

        self.session_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self.session_dir, 0o700)
        self.session_file = (self.session_dir / f"{self.session_id}.json").resolve()
        try:
            self.session_file.relative_to(self.session_dir)
        except ValueError:
            raise ValueError(f"Session file escapes session directory: {self.session_id}")

    def add_message(self, message: BaseMessage) -> None:
        """Add message to history and update timestamp."""
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        self._trim_history()
        
    def _trim_history(self) -> None:
        """Trim history to configured limits (by turn count and token budget)."""
        # Always keep SystemMessage (index 0)
        if not self.messages:
            return

        system_msg = self.messages[0]
        history = self.messages[1:]

        # 1. Trim by turn count if configured
        max_turns = self.config.max_history_turns
        if max_turns and len(history) > max_turns * 2:  # *2 because Human+AI = 1 turn
            history = history[-(max_turns * 2):]

        # 2. Trim by token budget so max_context_tokens is actually enforced.
        max_tokens = self.config.max_context_tokens
        if max_tokens:
            from .tokens import message_tokens

            system_tokens = message_tokens(system_msg)
            budget = max(0, max_tokens - system_tokens)
            # Walk newest -> oldest, keeping as much recent history as fits.
            kept_reversed: List[BaseMessage] = []
            used = 0
            for msg in reversed(history):
                cost = message_tokens(msg)
                if used + cost > budget and kept_reversed:
                    break
                kept_reversed.append(msg)
                used += cost
            history = list(reversed(kept_reversed))

        self.messages = [system_msg] + history

    def save(self) -> None:
        """Save session to disk atomically with private permissions."""
        if not self.config.save_sessions:
            return

        current_messages = messages_to_dict(self.messages)
        temp_file: Optional[Path] = None
        with self._session_lock():
            existing_data = None
            existing_messages: List[dict] = []
            if self.session_file.exists() or self.session_file.is_symlink():
                if self.session_file.is_symlink():
                    raise SessionCorruptError(
                        f"Session file is a symlink and cannot be safely loaded: {self.session_file}"
                    )
                existing_data, existing_messages = self._read_payload_locked()

            if existing_data is None:
                merged_messages = current_messages
            elif self._base_message_dicts and current_messages[: len(self._base_message_dicts)] == self._base_message_dicts:
                # This instance loaded a snapshot and only appended messages.
                # Preserve anything another instance committed in the meantime.
                delta = current_messages[len(self._base_message_dicts) :]
                merged_messages = existing_messages + delta
            elif current_messages == existing_messages:
                merged_messages = existing_messages
            else:
                # A trimmed or independently-created state has no safe common
                # prefix.  Preserve the durable file and append only messages
                # not already present verbatim.
                merged_messages = existing_messages + [
                    message for message in current_messages if message not in existing_messages
                ]

            now = datetime.now().isoformat()
            data = {
                "session_id": self.session_id,
                "specialist": self.specialist_slug,
                "created_at": (existing_data or {}).get("created_at", self.created_at),
                "updated_at": now,
                "messages": merged_messages,
            }

            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    dir=self.session_dir,
                    delete=False,
                    prefix=f".{self.session_id}_",
                    suffix=".tmp",
                    encoding="utf-8",
                ) as output:
                    temp_file = Path(output.name)
                    os.chmod(temp_file, 0o600)
                    json.dump(data, output, indent=2)
                    output.flush()
                    os.fsync(output.fileno())

                os.replace(temp_file, self.session_file)
                temp_file = None
                os.chmod(self.session_file, 0o600)
                self.created_at = data["created_at"]
                self.updated_at = now
                self.messages = messages_from_dict(merged_messages)
                self._base_message_dicts = merged_messages
            finally:
                if temp_file is not None:
                    temp_file.unlink(missing_ok=True)

    def load(self) -> bool:
        """Load a session, distinguishing a miss from corrupt evidence."""
        with self._session_lock():
            if not self.session_file.exists():
                return False
            if self.session_file.is_symlink():
                raise SessionCorruptError(
                    f"Session file is a symlink and cannot be safely loaded: {self.session_file}"
                )

            data, restored_message_dicts = self._read_payload_locked()
            self.created_at = data["created_at"]
            self.updated_at = data.get("updated_at", self.created_at)
            self.messages = messages_from_dict(restored_message_dicts)
            self._base_message_dicts = messages_to_dict(self.messages)
            return True

    @contextmanager
    def _session_lock(self):
        """Serialize reads and replacements for this exact session file."""
        lock_path = self.session_dir / f".{self.session_id}.lock"
        lock_flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        try:
            lock_fd = os.open(lock_path, lock_flags, 0o600)
        except OSError as exc:
            raise SessionCorruptError(
                f"Session lock cannot be safely opened for {self.session_id}: {exc}"
            ) from exc
        try:
            os.fchmod(lock_fd, 0o600)
            with os.fdopen(lock_fd, "r+", encoding="utf-8") as lock_file:
                lock_fd = -1
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                yield
        finally:
            if lock_fd >= 0:
                os.close(lock_fd)

    def _read_payload_locked(self) -> tuple[dict, List[dict]]:
        """Read and validate session JSON while the caller holds the lock."""
        try:
            with self.session_file.open("r", encoding="utf-8") as session_file:
                data = json.load(session_file)
        except (OSError, json.JSONDecodeError) as exc:
            raise SessionCorruptError(
                f"Session {self.session_id} is corrupt: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise SessionCorruptError(f"Session {self.session_id} is corrupt: root is not an object")
        if data.get("session_id") != self.session_id:
            raise SessionIdentityMismatchError(
                f"Session identity mismatch: expected session_id {self.session_id!r}"
            )
        if data.get("specialist") != self.specialist_slug:
            raise SessionIdentityMismatchError(
                f"Session identity mismatch: expected specialist {self.specialist_slug!r}"
            )
        if not isinstance(data.get("created_at"), str):
            raise SessionCorruptError(f"Session {self.session_id} is corrupt: missing created_at")
        if "updated_at" in data and not isinstance(data["updated_at"], str):
            raise SessionCorruptError(f"Session {self.session_id} is corrupt: invalid updated_at")
        if not isinstance(data.get("messages"), list):
            raise SessionCorruptError(f"Session {self.session_id} is corrupt: messages is not a list")

        try:
            restored_messages = messages_from_dict(data["messages"])
        except Exception as exc:
            raise SessionCorruptError(
                f"Session {self.session_id} is corrupt: invalid messages ({exc})"
            ) from exc
        return data, data["messages"]

    def clear(self) -> str:
        """Clear conversation history and start fresh session.

        Returns:
            New session ID
        """
        # Generate new session ID
        from datetime import timezone
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        short_uuid = uuid.uuid4().hex[:8]
        self.session_id = f"{timestamp}_{short_uuid}"

        # Reset messages but keep system message if exists
        system_msg = None
        if self.messages and isinstance(self.messages[0], SystemMessage):
            system_msg = self.messages[0]

        self.messages = [system_msg] if system_msg else []

        # Update timestamps
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self._base_message_dicts = []

        # Update session file path
        self.session_file = (self.session_dir / f"{self.session_id}.json").resolve()

        # Save new session
        self.save()

        return self.session_id

    @staticmethod
    def list_sessions(specialist_slug: str) -> List[Dict[str, Any]]:
        """List available sessions for a specialist."""
        config = get_config()
        specialist_slug = validate_identifier(specialist_slug, "specialist_slug")
        base_dir = config.session_dir.resolve()
        session_dir = (base_dir / specialist_slug).resolve()
        try:
            session_dir.relative_to(base_dir)
        except ValueError as exc:
            raise ValueError("Specialist directory escapes session root") from exc
        
        if not session_dir.exists():
            return []
            
        sessions = []
        for f in session_dir.glob("*.json"):
            try:
                if not f.is_file() or f.is_symlink():
                    continue
                resolved = f.resolve()
                resolved.relative_to(session_dir)
                validate_identifier(f.stem, "session_id")
                # Basic info from filename/stat without full load
                stat = resolved.stat()
                sessions.append({
                    "id": f.stem,
                    "path": resolved,
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })
            except Exception:
                continue
                
        # Sort by modified desc
        return sorted(sessions, key=lambda x: x["modified"], reverse=True)
