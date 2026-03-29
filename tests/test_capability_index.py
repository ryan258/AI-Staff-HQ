"""Tests for capability index tier filtering."""

from pathlib import Path

from orchestrator.capability_index import CapabilityIndex


def test_capability_index_defaults_to_active_roster():
    """Capability matching should use the active roster by default."""
    project_root = Path(__file__).resolve().parents[1]
    staff_dir = project_root / "staff"

    index = CapabilityIndex(staff_dir)
    specialists = set(index.list_all_specialists())

    assert "chief-of-staff" in specialists
    assert "copywriter" in specialists
    assert "irony-detector" not in specialists
    assert len(specialists) == 12


def test_capability_index_can_include_experimental_roles():
    """Experimental specialists should be opt-in."""
    project_root = Path(__file__).resolve().parents[1]
    staff_dir = project_root / "staff"

    index = CapabilityIndex(staff_dir, allowed_tiers=("active", "experimental"))
    specialists = set(index.list_all_specialists())

    assert "habit-architect" in specialists
    assert "irony-detector" not in specialists
