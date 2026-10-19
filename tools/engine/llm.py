"""OpenRouter integration and model routing."""

from typing import Optional
from pathlib import Path
import yaml
from langchain_openai import ChatOpenAI

from .config import Config, get_config


class ModelRouter:
    """Routes specialists to optimal models via OpenRouter."""

    def __init__(self, routing_config_path: Optional[Path] = None, config: Optional[Config] = None):
        self.config = config or get_config()

        # Load routing configuration
        if routing_config_path is None:
            # Try typical locations (prefer package-local over CWD)
            candidates = [
                Path(__file__).parent.parent.parent / "config" / "model_routing.yaml",  # Package relative
                Path("config/model_routing.yaml"),  # CWD
            ]
            for candidate in candidates:
                if candidate.exists():
                    routing_config_path = candidate
                    break
        
        self.routing = {}
        if routing_config_path and routing_config_path.exists():
            with open(routing_config_path) as f:
                self.routing = yaml.safe_load(f) or {}

    def select_model(
        self,
        role: str,
        department: Optional[str] = None,
        override: Optional[str] = None
    ) -> str:
        """Select optimal model for specialist.

        Priority:
        1. User override (--model flag)
        2. Budget mode override
        3. Role-based routing
        4. Department fallback
        5. Default model from environment/config
        """

        # 1. User override takes precedence
        if override:
            return override

        # 2. Budget mode is an explicit force-all setting.
        budget_cfg = self.routing.get('budget_mode', {})
        if budget_cfg.get('enabled', False):
            budget_model = str(budget_cfg.get('model', "")).strip()
            if budget_model:
                return budget_model

        # 3. Role-based routing
        role_routing = self.routing.get('role_routing', {})
        if role in role_routing:
            return role_routing[role]

        # 4. Department-based fallback
        dept_routing = self.routing.get('department_routing', {})
        if department and department in dept_routing:
            return dept_routing[department]

        # 5. Final fallback default model
        return self.config.default_model

    def create_llm(
        self,
        model: str,
        temperature: Optional[float] = None
    ) -> ChatOpenAI:
        """Create LangChain LLM client for OpenRouter or direct provider."""
        if not model or not isinstance(model, str) or not model.strip():
            raise ValueError("Model name must be a non-empty string.")

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
            if "/" in model and not model.startswith("openai/"):
                raise ValueError(
                    f"Model '{model}' appears to require OpenRouter (provider-namespaced), "
                    "but only OPENAI_API_KEY is configured. Set OPENROUTER_API_KEY to use this model."
                )

        if not api_key:
            if self.config.anthropic_api_key:
                raise ValueError(
                    "Anthropic provider is configured but not supported by ModelRouter. "
                    "Set OPENROUTER_API_KEY or OPENAI_API_KEY, or implement the Anthropic client."
                )
            raise ValueError(
                "No API keys found. Please set OPENROUTER_API_KEY (recommended) "
                "or OPENAI_API_KEY in your .env file."
            )

        # OpenRouter retries the next model when the primary is down,
        # rate-limited, or retired (free models disappear without notice).
        extra_body = None
        fallbacks = [m for m in self.routing.get('fallback_models') or [] if m and m != model]
        if base_url and fallbacks:
            extra_body = {"models": [model, *fallbacks]}

        resolved_temp = self.config.default_temperature if temperature is None else float(temperature)
        if not (0.0 <= resolved_temp <= 2.0):
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got {resolved_temp}")

        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=resolved_temp,
            default_headers=default_headers,
            timeout=self.config.request_timeout_seconds,
            max_retries=self.config.max_retries,
            extra_body=extra_body,
        )

    def get_model_info(self, model_id: str) -> Optional[dict]:
        """Get metadata for a model."""
        for model in self.routing.get('available_models', []):
            if model['id'] == model_id:
                return model
        return None
