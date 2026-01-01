"""Tests for dynamic CoS orchestration workflow."""

from pathlib import Path

from orchestrator.graph_runner import GraphRunner
from workflows.constants import SpecialistSlugs
from workflows.graphs.cos_orchestration import build_graph


class DummyAgent:
    def __init__(self, response: str):
        self.response = response

    def query(self, _prompt: str) -> str:
        return self.response


def test_cos_orchestration_handles_invalid_tasks(tmp_path):
    def loader(slug: str, *_args, **_kwargs):
        if slug == SpecialistSlugs.CHIEF_OF_STAFF:
            return DummyAgent('["oops", {"specialist": "nonexistent", "task": "Do thing"}]')
        return DummyAgent(f"{slug} ok")

    runner = GraphRunner(
        staff_dir=Path("staff"),
        agent_loader=loader,
        log_dir=tmp_path / "logs",
    )

    graph = build_graph(runner)
    result = runner.run_graph(
        graph,
        {
            "topic": "demo",
            "steps": [],
            "queue": [],
            "results": [],
        },
    )

    assert result.get("results")
    assert any(item.get("specialist") == SpecialistSlugs.CHIEF_OF_STAFF for item in result["results"])
