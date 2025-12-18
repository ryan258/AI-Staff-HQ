"""OpenRouter integration and model routing."""

from typing import Optional
from pathlib import Path
import yaml
from langchain_openai import ChatOpenAI

from .config import get_config


class ModelRouter:
    """Routes specialists to optimal models via OpenRouter."""

    def __init__(self, routing_config_path: Optional[Path] = None):
        self.config = get_config()

        # Load routing configuration
        if routing_config_path is None:
            routing_config_path = Path(__file__).parent.parent.parent / "config" / "model_routing.yaml"

        with open(routing_config_path) as f:
            self.routing = yaml.safe_load(f)

    def select_model(
        self,
        role: str,
        department: Optional[str] = None,
        override: Optional[str] = None
    ) -> str:
        """Select optimal model for specialist.

        Priority:
        1. User override (--model flag)
        2. Role-based routing
        3. Department fallback
        4. Default model
        """

        # 1. User override takes precedence
        if override:
            return override

        # 2. Budget mode overrides everything except user override
        if self.routing.get('budget_mode', {}).get('enabled', False):
            return self.routing['budget_mode']['model']

        # 3. Role-based routing
        if role in self.routing['role_routing']:
            return self.routing['role_routing'][role]

        # 4. Department-based fallback
        if department and department in self.routing['department_routing']:
            return self.routing['department_routing'][department]

        # 5. Default model
        return self.config.default_model

    def create_llm(
        self,
        model: str,
        temperature: Optional[float] = None
    ) -> ChatOpenAI:
        """Create LangChain LLM client for OpenRouter."""

        # Check API keys
        api_key = self.config.openrouter_api_key
        base_url = self.config.openrouter_base_url
        default_headers = {
            "HTTP-Referer": "https://github.com/ai-staff-hq",
            "X-Title": "AI-Staff-HQ Executable Engine"
        }

        # Fallback to direct OpenAI if configured and OpenRouter missing
        if not api_key and self.config.openai_api_key:
            api_key = self.config.openai_api_key
            base_url = None  # Use default OpenAI URL
            default_headers = None

        if not api_key:
            raise ValueError(
                "No API keys found. Please set OPENROUTER_API_KEY (recommended) "
                "or OPENAI_API_KEY in your .env file."
            )

        # "headers" works if passed as default_headers to httpx client or similar
        # But for ChatOpenAI, standard way to pass headers is via default_headers kwarg
        # or it might need to be in model_kwargs depending on version.
        # Let's try passing it directly as default_headers which langchain support usually.
        
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=temperature or self.config.default_temperature,
            default_headers=default_headers
        )

    def get_model_info(self, model_id: str) -> Optional[dict]:
        """Get metadata for a model."""
        for model in self.routing.get('available_models', []):
            if model['id'] == model_id:
                return model
        return None
