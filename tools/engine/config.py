"""Configuration management for AI Staff HQ."""

import os
from pathlib import Path
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration from environment variables."""

    # OpenRouter Configuration
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "moonshotai/kimi-k2:free"

    # Direct Provider Keys (Fallback/Optional)
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Agent Configuration
    max_history_turns: int = 20
    max_context_tokens: int = 32000
    default_temperature: float = 0.7

    # Session Storage
    # Session Storage
    # We use a factory or validator to allow dynamic Home resolution
    session_dir: Path = None  # type: ignore
    save_sessions: bool = True

    # ...
    
    @field_validator("session_dir", mode="before")
    @classmethod
    def set_session_dir(cls, v: Optional[Path]) -> Path:
        if v is not None:
            return Path(v)
        return Path.home() / ".ai-staff-hq" / "sessions"

    # CLI Preferences
    rich_output: bool = True
    debug: bool = False

    # Logging
    log_dir: Path = Path("logs")
    enable_logging: bool = True

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def validate_api_keys(self) -> bool:
        """Check if at least one API key is configured."""
        return bool(self.openrouter_api_key or self.openai_api_key or self.anthropic_api_key)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset global configuration (mainly for testing)."""
    global _config
    _config = None
