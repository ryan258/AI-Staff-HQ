"""Pytest configuration and fixtures."""

import os
import shutil
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.engine.config import Config, get_config


@pytest.fixture
def mock_env(monkeypatch, tmp_path):
    """Mock environment variables and config."""
    # Set up temp directories
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    session_dir = home_dir / ".ai-staff-hq" / "sessions"
    
    # Patch HOME so Path.home() returns our temp dir
    # Note: Path.home() uses os.environ['HOME'] on Unix
    monkeypatch.setenv("HOME", str(home_dir))
    
    # Set default keys to avoid validation errors in general tests
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-mock-key")
    monkeypatch.setenv("DEFAULT_MODEL", "mock/model")
    
    # Reset config singleton
    from tools.engine import config
    
    # Patch the env_file in SettingsConfigDict to point to nothing
    # access the class attribute model_config
    config.Config.model_config['env_file'] = tmp_path / "nonexistent.env"
    
    config._config = None
    
    return home_dir


@pytest.fixture
def mock_llm(mocker):
    """Mock the LLM to avoid real API calls."""
    mock_chat = mocker.patch("tools.engine.llm.ChatOpenAI")
    mock_instance = mock_chat.return_value
    
    # Mock invoke response
    mock_response = MagicMock()
    mock_response.content = "Mock AI response"
    mock_instance.invoke.return_value = mock_response
    
    return mock_instance
