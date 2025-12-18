"""Core agent factory and orchestration."""

from typing import Optional
from pathlib import Path
import yaml
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from .schemas import SpecialistSchema
from .schemas import SpecialistSchema
from .prompt import PromptBuilder
from .llm import ModelRouter
from .state import ConversationState


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

        # Extract and store response
        self.state.add_message(AIMessage(content=response_text))
        
        # Save state
        self.state.save()

        return response_text

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
        if yaml_file.stem == specialist_identifier:
            return SpecialistAgent(yaml_file, **kwargs)

    # 3. Not found
    raise FileNotFoundError(
        f"Specialist '{specialist_identifier}' not found in {staff_dir}. "
        f"Use 'activate --list' to see available specialists."
    )
