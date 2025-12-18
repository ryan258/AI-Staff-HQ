"""Tests for configuration management."""

import pytest
from pathlib import Path
from tools.engine.config import Config, get_config, reset_config

def test_config_defaults():
    """Test default configuration values."""
    reset_config()
    config = Config()
    
    # Defaults
    assert config.max_history_turns == 20
    assert config.default_temperature == 0.7
    assert config.save_sessions is True
    assert config.openrouter_base_url == "https://openrouter.ai/api/v1"

def test_config_from_env(mock_env):
    """Test loading configuration from environment variables."""
    reset_config()
    config = get_config()
    
    assert config.openrouter_api_key == "sk-mock-key"
    assert config.default_model == "mock/model"
    assert config.session_dir == mock_env / ".ai-staff-hq" / "sessions"

def test_api_key_validation(monkeypatch):
    """Test API key validation logic."""
    reset_config()
    
    # No keys
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    
    config = Config()
    assert config.validate_api_keys() is False
    
    # One key
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    config = Config()
    assert config.validate_api_keys() is True
