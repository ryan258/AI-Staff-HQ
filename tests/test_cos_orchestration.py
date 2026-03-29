"""Tests for dynamic CoS orchestration workflow."""

from pathlib import Path

from orchestrator.graph_runner import GraphRunner
from workflows.constants import SpecialistSlugs
from workflows.graphs.cos_orchestration import build_graph, get_available_specialists


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


def test_get_available_specialists_defaults_to_active(monkeypatch):
    """CoS orchestration should default to the active roster."""
    captured = {}

    def fake_list_specialists_by_department(_staff_dir, *, tiers):
        captured["tiers"] = tiers
        return {"strategy": ["chief-of-staff"]}

    monkeypatch.setattr(
        "workflows.graphs.cos_orchestration.list_specialists_by_department",
        fake_list_specialists_by_department,
    )

    result = get_available_specialists(Path("staff"))

    assert result == {"strategy": ["chief-of-staff"]}
    assert captured["tiers"] == ("active",)


def test_get_available_specialists_can_include_experimental(monkeypatch):
    """CoS orchestration should support the experimental roster tier when requested."""
    captured = {}

    def fake_list_specialists_by_department(_staff_dir, *, tiers):
        captured["tiers"] = tiers
        return {"strategy": ["chief-of-staff", "irony-detector"]}

    monkeypatch.setattr(
        "workflows.graphs.cos_orchestration.list_specialists_by_department",
        fake_list_specialists_by_department,
    )

    result = get_available_specialists(Path("staff"), include_experimental=True)

    assert result == {"strategy": ["chief-of-staff", "irony-detector"]}
    assert captured["tiers"] == ("active", "experimental")
