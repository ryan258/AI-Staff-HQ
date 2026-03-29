"""Tests for the real-brief capture workflow."""

from workflows.planning_swarm_capture import update_capture_cases
from workflows.planning_swarm_eval import build_snapshot_case


def test_update_capture_cases_only_rewrites_selected_cases():
    """Capture updates should respect explicit case selection."""
    payload = {
        "version": 1,
        "cases": [
            {"id": "keep-me", "brief": "Keep this as-is"},
            {"id": "refresh-me", "brief": "Refresh this case"},
        ],
    }

    updated = update_capture_cases(
        payload,
        case_ids={"refresh-me"},
        capture_fn=lambda case: {**case, "planner_response": "captured"},
    )

    assert updated["cases"][0] == payload["cases"][0]
    assert updated["cases"][1]["planner_response"] == "captured"


def test_build_snapshot_case_creates_eval_ready_expectations():
    """Captured planner responses should convert into a deterministic eval case."""
    planner_response = """
    [
      {
        "id": "task_1",
        "description": "Research the audience and competitor landscape.",
        "required_capabilities": ["market research", "competitive analysis"],
        "depends_on": [],
        "priority": 1
      },
      {
        "id": "task_2",
        "description": "Draft the launch messaging.",
        "required_capabilities": ["copywriting", "brand messaging"],
        "depends_on": ["task_1"],
        "priority": 1
      }
    ]
    """

    snapshot = build_snapshot_case(
        case_id="real-brief",
        brief="Turn this rough launch idea into a plan.",
        planner_response=planner_response,
        notes="Captured from a real brief",
    )

    assert snapshot["id"] == "real-brief"
    assert snapshot["expect"]["task_count"] == 2
    assert snapshot["expect"]["top_specialists"]["task_1"] == ["market-analyst"]
    assert snapshot["expect"]["top_specialists"]["task_2"] == ["copywriter"]
