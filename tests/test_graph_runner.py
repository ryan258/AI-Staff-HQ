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
    result = runner.run_graph(
        compiled,
        {
            "topic": "demo graph topic",
            "workflow_name": "test-graph",
        },
    )

    assert "run_id" in result
    assert "log_path" in result
    assert result["analysis"].startswith("market-analyst response")
    assert result["technical_plan"].startswith("software-architect response")
    assert len(result.get("steps", [])) == 2

    log_path = Path(result["log_path"])
    assert log_path.exists()
    assert log_path.parent == tmp_path / "logs"
    assert log_path.name.startswith("test-graph__demo-graph-topic__")
    assert log_path.name.endswith(".json")
    log_data = json.loads(log_path.read_text())
    assert log_data["run_id"] == result["run_id"]
    assert log_data["log_path"] == str(log_path)
    assert len(log_data["steps"]) == 2


def test_graph_runner_persists_log_on_failure(tmp_path, mock_env):
    """When a node raises an exception, runner must still write a durable failure log."""
    import pytest

    def failing_node(state):
        raise RuntimeError("Catastrophic node failure")

    runner = GraphRunner(
        staff_dir=tmp_path,
        log_dir=tmp_path / "logs",
    )

    graph = build_state_graph()
    graph.add_node("fail", failing_node)
    graph.set_entry_point("fail")
    compiled = graph.compile()

    with pytest.raises(RuntimeError, match="Catastrophic node failure"):
        runner.run_graph(
            compiled,
            {
                "topic": "failure test topic",
                "workflow_name": "fail-graph",
            },
        )

    # Check that failure log was written
    logs = list((tmp_path / "logs").glob("*.json"))
    assert len(logs) == 1
    log_data = json.loads(logs[0].read_text())
    assert log_data["status"] == "FAILED"
    assert "Catastrophic node failure" in log_data["state"]["error"]


def test_graph_runner_redacts_sensitive_log_values(tmp_path, mock_env):
    """Structured workflow logs must not retain credential-shaped strings."""
    runner = GraphRunner(staff_dir=tmp_path, log_dir=tmp_path / "logs")
    state = {
        "run_id": "20260831_120000_deadbeef",
        "workflow_name": "privacy-test",
        "topic": "password: graph-secret-value",
        "steps": [{"prompt": "Bearer graph-token-value", "output": "safe"}],
        "final_output": "-----BEGIN PRIVATE KEY-----\nkey-body\n-----END PRIVATE KEY-----",
        "status": "COMPLETED",
    }

    log_path = runner._persist_log(state)
    log_data = log_path.read_text(encoding="utf-8")

    assert "graph-secret-value" not in log_data
    assert "graph-token-value" not in log_data
    assert "key-body" not in log_data
    assert "[REDACTED_PRIVATE_KEY]" in log_data


def test_graph_runner_preserves_explicit_terminal_status(tmp_path, mock_env):
    """A node's BLOCKED/FAILED status must not be rewritten as COMPLETED."""
    runner = GraphRunner(staff_dir=tmp_path, log_dir=tmp_path / "logs")
    graph = build_state_graph()

    def blocked_node(state):
        return {**state, "status": "BLOCKED", "final_output": "[BLOCKED]"}

    graph.add_node("blocked", blocked_node)
    graph.set_entry_point("blocked")
    graph.add_edge("blocked", END)

    result = runner.run_graph(graph.compile(), {"topic": "blocked", "workflow_name": "blocked-graph"})
    assert result["status"] == "BLOCKED"
    log_data = json.loads(Path(result["log_path"]).read_text())
    assert log_data["status"] == "BLOCKED"
