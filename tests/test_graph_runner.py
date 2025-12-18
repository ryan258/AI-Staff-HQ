"""Tests for LangGraph runner utilities."""

import json
from pathlib import Path

from langgraph.graph import END

from orchestrator.graph_runner import GraphRunner, build_state_graph


class DummyAgent:
    def __init__(self, name: str):
        self.name = name

    def query(self, prompt: str) -> str:
        return f"{self.name} response to: {prompt}"


def test_graph_runner_executes_and_logs(tmp_path, mock_env):
    """Graph runner should execute nodes, mutate state, and persist logs."""

    def loader(slug: str, *_args, **_kwargs):
        return DummyAgent(slug)

    runner = GraphRunner(
        staff_dir=tmp_path,
        agent_loader=loader,
        log_dir=tmp_path / "logs",
    )

    graph = build_state_graph()

    analysis = runner.make_agent_node(
        specialist_slug="market-analyst",
        state_key="analysis",
        prompt_builder=lambda state: f"Topic: {state['topic']}",
        step_name="analysis",
    )
    tech = runner.make_agent_node(
        specialist_slug="software-architect",
        state_key="technical_plan",
        prompt_builder=lambda state: f"Analysis: {state['analysis']}",
        step_name="tech",
    )

    graph.add_node("analysis", analysis)
    graph.add_node("tech", tech)
    graph.add_edge("analysis", "tech")
    graph.add_edge("tech", END)
    graph.set_entry_point("analysis")

    compiled = graph.compile()
    result = runner.run_graph(compiled, {"topic": "demo"})

    assert "run_id" in result
    assert result["analysis"].startswith("market-analyst response")
    assert result["technical_plan"].startswith("software-architect response")
    assert len(result.get("steps", [])) == 2

    log_path = Path(tmp_path / "logs" / f"{result['run_id']}.json")
    assert log_path.exists()
    log_data = json.loads(log_path.read_text())
    assert log_data["run_id"] == result["run_id"]
    assert len(log_data["steps"]) == 2
