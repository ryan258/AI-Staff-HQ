"""Tests for LLMRouter in tools.engine.llm."""

import pytest
from pathlib import Path
import yaml
from tools.engine.config import Config
from tools.engine.llm import ModelRouter


def test_create_llm_preserves_zero_temperature(monkeypatch):
    """temperature=0.0 must be preserved rather than falling back to default."""
    config = Config(openrouter_api_key="test-key")
    router = ModelRouter(config=config)

    llm = router.create_llm("nvidia/nemotron-3-super-120b-a12b:free", temperature=0.0)
    assert llm.temperature == 0.0


def test_create_llm_uses_default_temperature_when_none():
    config = Config(openrouter_api_key="test-key", default_temperature=0.7)
    router = ModelRouter(config=config)

    llm = router.create_llm("nvidia/nemotron-3-super-120b-a12b:free", temperature=None)
    assert llm.temperature == 0.7


def test_create_llm_rejects_empty_model():
    config = Config(openrouter_api_key="test-key")
    router = ModelRouter(config=config)

    with pytest.raises(ValueError, match="Model name must be a non-empty string"):
        router.create_llm("")


def test_create_llm_rejects_out_of_range_temperature():
    config = Config(openrouter_api_key="test-key")
    router = ModelRouter(config=config)

    with pytest.raises(ValueError, match="Temperature must be between 0.0 and 2.0"):
        router.create_llm("nvidia/nemotron-3-super-120b-a12b:free", temperature=3.5)


def test_create_llm_rejects_openrouter_model_when_only_openai_key():
    config = Config(openrouter_api_key="", openai_api_key="sk-openai-key")
    router = ModelRouter(config=config)

    with pytest.raises(ValueError, match="appears to require OpenRouter"):
        router.create_llm("anthropic/claude-sonnet-5.5")


def test_model_router_defaults_when_missing_routing(mock_env):
    """Falls back to the configured default when no routing file exists."""
    router = ModelRouter(routing_config_path=Path("/nonexistent/path.yaml"))

    assert router.routing == {}
    assert router.select_model(role="Unknown Role", department="tech") == "mock/model"


def test_model_router_routing_precedence(tmp_path, mock_env):
    """Override, budget, role, department, and default precedence remains stable."""
    routing_yaml = tmp_path / "routing.yaml"
    routing_yaml.write_text(
        """
budget_mode:
  enabled: true
  model: budget-model
role_routing:
  Specialist Role: role-model
department_routing:
  tech: dept-model
"""
    )
    router = ModelRouter(routing_config_path=routing_yaml)

    assert router.select_model(role="Specialist Role", department="tech") == "budget-model"
    assert router.select_model(role="Specialist Role", department="tech", override="user-model") == "user-model"

    routing_yaml.write_text(
        """
budget_mode:
  enabled: false
role_routing:
  Specialist Role: role-model
department_routing:
  tech: dept-model
"""
    )
    router = ModelRouter(routing_config_path=routing_yaml)
    assert router.select_model(role="Specialist Role", department="tech") == "role-model"
    assert router.select_model(role="Unknown Role", department="tech") == "dept-model"


def test_repo_budget_mode_is_disabled_without_budget_model():
    """The bundled routing file must not silently force an empty model."""
    routing_path = Path(__file__).resolve().parents[1] / "config" / "model_routing.yaml"
    budget_mode = yaml.safe_load(routing_path.read_text(encoding="utf-8"))["budget_mode"]
    assert budget_mode["enabled"] is False
    assert budget_mode["model"] == ""


def test_anthropic_only_configuration_is_rejected_explicitly(monkeypatch):
    """A configured but unsupported provider must not pass key validation."""
    # This test exercises explicit constructor values, not the developer's
    # local credentials.  Disable both process-environment and dotenv
    # sources so a sibling checkout .env cannot make the test pass falsely.
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = Config(anthropic_api_key="anthropic-key", _env_file=None)
    assert config.validate_api_keys() is False
    with pytest.raises(ValueError, match="Anthropic.*not supported"):
        ModelRouter(config=config).create_llm("claude-sonnet-5.5")


def test_create_llm_bounds_requests_and_sends_openrouter_fallbacks(tmp_path):
    routing_yaml = tmp_path / "routing.yaml"
    routing_yaml.write_text("fallback_models:\n  - primary/model\n  - backup/model\n")
    config = Config(openrouter_api_key="test-key", request_timeout_seconds=30, max_retries=1)
    llm = ModelRouter(routing_config_path=routing_yaml, config=config).create_llm("primary/model")

    assert llm.request_timeout == 30
    assert llm.max_retries == 1
    assert llm.extra_body == {"models": ["primary/model", "backup/model"]}


def test_create_llm_skips_fallbacks_for_direct_openai(tmp_path):
    routing_yaml = tmp_path / "routing.yaml"
    routing_yaml.write_text("fallback_models:\n  - backup/model\n")
    config = Config(openrouter_api_key="", openai_api_key="sk-openai-key", _env_file=None)
    llm = ModelRouter(routing_config_path=routing_yaml, config=config).create_llm("gpt-test")

    assert llm.extra_body is None
