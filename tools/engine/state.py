"""Conversation state management and persistence."""

import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

from langchain_core.messages import (
    BaseMessage, 
    HumanMessage, 
    AIMessage, 
    SystemMessage, 
    messages_to_dict, 
    messages_from_dict
)

from .config import get_config


class ConversationState:
    """Manages conversation history and persistence."""

    def __init__(
        self, 
        specialist_slug: str, 
        session_id: Optional[str] = None
    ):
        self.config = get_config()
        self.specialist_slug = specialist_slug
        if session_id:
            self.session_id = session_id
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
        
        # Ensure session directory exists
        self.session_dir = self.config.session_dir / self.specialist_slug
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.session_dir / f"{self.session_id}.json"

    def add_message(self, message: BaseMessage) -> None:
        """Add message to history and update timestamp."""
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        self._trim_history()
        
    def _trim_history(self) -> None:
        """Trim history to configured limits."""
        # Always keep SystemMessage (index 0)
        if not self.messages:
            return
            
        system_msg = self.messages[0]
        history = self.messages[1:]
        
        # Trim by turn count if configured
        max_turns = self.config.max_history_turns
        if max_turns and len(history) > max_turns * 2:  # *2 because Human+AI = 1 turn
            # Keep the last N turns
            history = history[-(max_turns * 2):]
            self.messages = [system_msg] + history

    def save(self) -> None:
        """Save session to disk."""
        if not self.config.save_sessions:
            return

        data = {
            "session_id": self.session_id,
            "specialist": self.specialist_slug,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": messages_to_dict(self.messages)
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self) -> bool:
        """Load session from disk. Returns True if successful."""
        if not self.session_file.exists():
            return False

        try:
            with open(self.session_file) as f:
                data = json.load(f)
                
            self.session_id = data["session_id"]
            self.created_at = data["created_at"]
            self.updated_at = data.get("updated_at", self.created_at)
            
            # Restore messages
            if "messages" in data:
                self.messages = messages_from_dict(data["messages"])
                
            return True
        except Exception as e:
            print(f"Error loading session {self.session_id}: {e}")
            return False

    @staticmethod
    def list_sessions(specialist_slug: str) -> List[Dict[str, Any]]:
        """List available sessions for a specialist."""
        config = get_config()
        session_dir = config.session_dir / specialist_slug
        
        if not session_dir.exists():
            return []
            
        sessions = []
        for f in session_dir.glob("*.json"):
            try:
                # Basic info from filename/stat without full load
                stat = f.stat()
                sessions.append({
                    "id": f.stem,
                    "path": f,
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })
            except Exception:
                continue
                
        # Sort by modified desc
        return sorted(sessions, key=lambda x: x["modified"], reverse=True)
