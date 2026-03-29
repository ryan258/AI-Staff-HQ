"""Tests for model routing and resilience."""

from pathlib import Path

import yaml

from tools.engine.llm import ModelRouter
from tools.engine.config import get_config


def test_model_router_defaults_when_missing_routing(mock_env):
    """Falls back to default model when no routing file exists."""
    router = ModelRouter(routing_config_path=Path("/nonexistent/path.yaml"))

    assert isinstance(router.routing, dict)
    assert router.routing == {}
    model = router.select_model(role="Unknown Role", department="tech")
    assert model == get_config().default_model


def test_model_router_routing_precedence(tmp_path, mock_env):
    """Validate budget, role, department precedence and override handling."""
    routing_yaml = tmp_path / "routing.yaml"
    routing_yaml.write_text(
        """
budget_mode:
  enabled: true
  model: budget-model
role_routing:
  "Specialist Role": role-model
department_routing:
  tech: dept-model
"""
    )

    router = ModelRouter(routing_config_path=routing_yaml)

    # Budget mode overrides role/department
    assert router.select_model(role="Specialist Role", department="tech") == "budget-model"

    # User override beats budget mode
    assert router.select_model(role="Specialist Role", department="tech", override="user-override") == "user-override"

    # Disable budget mode to test role/department fallbacks
    routing_yaml.write_text(
        """
budget_mode:
  enabled: false
role_routing:
  "Specialist Role": role-model
department_routing:
  tech: dept-model
"""
    )
    router = ModelRouter(routing_config_path=routing_yaml)

    # Role routing takes precedence over department
    assert router.select_model(role="Specialist Role", department="tech") == "role-model"
    # Department routing used when role not present
    assert router.select_model(role="Unknown Role", department="tech") == "dept-model"


def test_repo_budget_mode_is_disabled_without_budget_model():
    """Bundled routing config should not advertise budget mode without a model."""
    routing_path = Path(__file__).resolve().parents[1] / "config" / "model_routing.yaml"
    payload = yaml.safe_load(routing_path.read_text(encoding="utf-8"))

    budget_mode = payload["budget_mode"]

    assert budget_mode["enabled"] is False
    assert budget_mode["model"] == ""
