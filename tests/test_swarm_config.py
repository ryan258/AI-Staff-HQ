"""Tests for swarm configuration defaults and validation."""

from workflows.schemas.swarm import SwarmConfig


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
