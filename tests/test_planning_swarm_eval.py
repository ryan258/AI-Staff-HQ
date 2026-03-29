"""Tests for the deterministic planning swarm eval harness."""

from workflows.planning_swarm_eval import DEFAULT_CASES_PATH, evaluate_suite, load_eval_suite


def test_planning_swarm_eval_suite_definition_exists():
    """The planning swarm eval suite should load cleanly."""
    suite = load_eval_suite(DEFAULT_CASES_PATH)

    assert suite.version == 1
    assert len(suite.cases) == 5


def test_planning_swarm_eval_suite_passes():
    """The current active roster should satisfy the starter eval suite."""
    summary = evaluate_suite(DEFAULT_CASES_PATH)

    assert summary["total_cases"] == 5
    assert summary["passed_cases"] == 5
    assert summary["passed_checks"] == summary["total_checks"]
