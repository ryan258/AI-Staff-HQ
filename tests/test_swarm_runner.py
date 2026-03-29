"""Tests for swarm runner log persistence."""

from pathlib import Path

from orchestrator.swarm_runner import SwarmRunner
from workflows.schemas.swarm import SwarmConfig


def test_swarm_runner_persists_semantic_log_path(tmp_path):
    """Swarm logs should use semantic filenames derived from the brief."""
    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(),
        log_dir=tmp_path / "logs",
    )

    state = {
        "run_id": "20260329_123000_deadbeef",
        "workflow_name": "planning-swarm",
        "log_title": "Develop new horror concepts for Blackwood Manor",
        "steps": [],
    }

    log_path = runner._persist_log(state)

    assert log_path.exists()
    assert log_path.parent == tmp_path / "logs"
    assert log_path.name.startswith(
        "planning-swarm__develop-new-horror-concepts-for-blackwood-manor__20260329_123000_deadbeef"
    )
    assert state["log_path"] == str(log_path)
