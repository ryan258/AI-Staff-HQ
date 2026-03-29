"""Tests for specialist roster tiers."""

from pathlib import Path

from tools.engine.roster import iter_specialist_records, list_specialists_by_department, load_roster_config


def test_repo_roster_config_covers_all_staff():
    """The repo roster should classify every specialist exactly once."""
    project_root = Path(__file__).resolve().parents[1]
    staff_dir = project_root / "staff"

    records = iter_specialist_records(staff_dir, tiers=("active", "experimental", "archived"))
    tiers = {record.tier for record in records}

    assert len(records) == 68
    assert tiers == {"active", "experimental", "archived"}
    assert len([record for record in records if record.tier == "active"]) == 12


def test_active_roster_groups_are_flagship_friendly():
    """Active roster should stay small and grouped for the flagship planner."""
    project_root = Path(__file__).resolve().parents[1]
    staff_dir = project_root / "staff"

    grouped = list_specialists_by_department(staff_dir, tiers=("active",))

    assert set(grouped) == {"producers", "strategy", "tech"}
    assert "chief-of-staff" in grouped["strategy"]
    assert "software-architect" in grouped["tech"]


def test_roster_config_has_single_flagship():
    """Roster config should declare the flagship workflow name."""
    roster = load_roster_config()

    assert roster.flagship_workflow == "planning-swarm"
