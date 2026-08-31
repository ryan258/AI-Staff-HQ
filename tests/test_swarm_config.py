"""Tests for swarm configuration defaults and validation."""

from workflows.schemas.swarm import SwarmConfig
import pytest


def test_swarm_config_defaults_to_active_roster():
    """The flagship swarm should default to the active roster immediately."""
    config = SwarmConfig()

    assert config.roster_tiers == ["active"]
    assert config.validate() == []
    assert config.roster_tiers == ["active"]


def test_swarm_config_reports_invalid_roster_tiers():
    """Invalid tiers should surface as warnings without mutating the config."""
    config = SwarmConfig(roster_tiers=["active", "bogus"])

    warnings = config.validate()

    assert warnings == ["Invalid roster tiers: bogus"]
    assert config.roster_tiers == ["active", "bogus"]


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"max_budget_tokens": 0}, "max_budget_tokens"),
        ({"max_budget_tokens": -1}, "max_budget_tokens"),
        ({"budget_warning_threshold": 0}, "budget_warning_threshold"),
        ({"budget_warning_threshold": 1.1}, "budget_warning_threshold"),
        ({"max_retries": -1}, "max_retries"),
    ],
)
def test_swarm_config_rejects_invalid_budget_and_retry_values(kwargs, message):
    config = SwarmConfig(**kwargs)
    with pytest.raises(ValueError, match=message):
        config.validate()
