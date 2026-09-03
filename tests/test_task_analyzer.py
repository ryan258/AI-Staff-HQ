"""Tests for TaskAnalyzer strict JSON parsing and validation."""

import json
from unittest.mock import MagicMock

import pytest

from orchestrator.task_analyzer import TaskAnalyzer, TaskAnalysisError


def test_task_analyzer_parses_valid_json():
    """TaskAnalyzer should parse well-formed task JSON."""
    runner = MagicMock()
    analyzer = TaskAnalyzer(runner)

    valid_json = json.dumps([
        {
            "id": "t1",
            "description": "Research topic",
            "required_capabilities": ["research"],
            "depends_on": [],
            "priority": 1,
        },
        {
            "id": "t2",
            "description": "Write summary",
            "required_capabilities": ["copywriting"],
            "depends_on": ["t1"],
            "priority": 2,
        },
    ])

    tasks = analyzer._parse_task_json(valid_json)
    assert len(tasks) == 2
    assert tasks[0].id == "t1"
    assert tasks[1].id == "t2"
    assert tasks[1].depends_on == ["t1"]


def test_task_analyzer_rejects_duplicates():
    """TaskAnalyzer should reject JSON with duplicate task IDs."""
    runner = MagicMock()
    analyzer = TaskAnalyzer(runner)

    dup_json = json.dumps([
        {"id": "t1", "description": "Task 1", "required_capabilities": ["c1"], "depends_on": []},
        {"id": "t1", "description": "Task 2", "required_capabilities": ["c2"], "depends_on": []},
    ])

    tasks = analyzer._parse_task_json(dup_json)
    assert tasks == []


def test_task_analyzer_rejects_self_dependency():
    """TaskAnalyzer should reject self-dependent tasks."""
    runner = MagicMock()
    analyzer = TaskAnalyzer(runner)

    self_dep_json = json.dumps([
        {"id": "t1", "description": "Task 1", "required_capabilities": ["c1"], "depends_on": ["t1"]},
    ])

    tasks = analyzer._parse_task_json(self_dep_json)
    assert tasks == []


def test_task_analyzer_rejects_missing_dependency():
    """TaskAnalyzer should reject tasks depending on non-existent tasks."""
    runner = MagicMock()
    analyzer = TaskAnalyzer(runner)

    missing_dep_json = json.dumps([
        {"id": "t1", "description": "Task 1", "required_capabilities": ["c1"], "depends_on": ["non_existent"]},
    ])

    tasks = analyzer._parse_task_json(missing_dep_json)
    assert tasks == []


def test_task_analyzer_fallback_on_invalid_response():
    """Malformed planning output must fail the planning phase explicitly."""
    runner = MagicMock()
    mock_agent = MagicMock()
    mock_agent.query.return_value = "Not valid JSON at all"
    runner.get_agent.return_value = mock_agent

    analyzer = TaskAnalyzer(runner)
    with pytest.raises(TaskAnalysisError, match="could not be parsed"):
        analyzer.analyze_brief("Create a marketing plan")


def test_task_analyzer_rejects_unsafe_task_identifier():
    """Task IDs must use the same path-safe grammar as session IDs."""
    analyzer = TaskAnalyzer(MagicMock())
    tasks = analyzer._parse_task_json(
        json.dumps([
            {
                "id": "task 1",
                "description": "Unsafe task",
                "required_capabilities": ["research"],
                "depends_on": [],
                "priority": 1,
            }
        ])
    )
    assert tasks == []


def test_task_analyzer_normalizes_numeric_task_ids():
    """Numeric IDs like '1' should normalize to 'task_1' and match dependencies."""
    analyzer = TaskAnalyzer(MagicMock())
    tasks = analyzer._parse_task_json(
        json.dumps([
            {
                "id": "1",
                "description": "Step one",
                "required_capabilities": ["research"],
                "depends_on": [],
                "priority": 1,
            },
            {
                "id": "2",
                "description": "Step two",
                "required_capabilities": ["copywriting"],
                "depends_on": ["1"],
                "priority": 2,
            },
        ])
    )
    assert len(tasks) == 2
    assert tasks[0].id == "task_1"
    assert tasks[1].id == "task_2"
    assert tasks[1].depends_on == ["task_1"]


def test_task_analyzer_prefers_structured_output():
    """When agent LLM supports with_structured_output, analyze_brief should use it."""
    from orchestrator.task_analyzer import TaskItem, TaskPlan

    from orchestrator.swarm_runner import SwarmRunner
    runner = MagicMock(spec=SwarmRunner)
    runner.query_agent_with_budget.side_effect = lambda agent, prompt, state=None, label="", invoker=None: (
        invoker(prompt, None) if invoker else agent.query(prompt)
    )
    mock_agent = MagicMock()
    mock_structured_llm = MagicMock()

    mock_plan = TaskPlan(
        tasks=[
            TaskItem(
                id="task_1",
                description="Structured task description",
                required_capabilities=["analysis"],
                depends_on=[],
                priority=1,
            )
        ]
    )
    mock_structured_llm.invoke.return_value = mock_plan
    mock_agent.llm.with_structured_output.return_value = mock_structured_llm
    runner.get_agent.return_value = mock_agent

    analyzer = TaskAnalyzer(runner)
    breakdown = analyzer.analyze_brief("Perform structured analysis")

    assert breakdown.parse_success is True
    assert len(breakdown.tasks) == 1
    assert breakdown.tasks[0].id == "task_1"
    assert breakdown.tasks[0].description == "Structured task description"
    mock_agent.llm.with_structured_output.assert_called_once_with(TaskPlan)
    runner.query_agent_with_budget.assert_called_once()


def test_task_analyzer_falls_back_when_structured_output_fails():
    """When structured output fails, analyze_brief should fall back to JSON text parsing."""
    runner = MagicMock()
    mock_agent = MagicMock()
    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.side_effect = RuntimeError("Provider does not support tools")
    mock_agent.llm.with_structured_output.return_value = mock_structured_llm

    valid_json = json.dumps([
        {
            "id": "task_1",
            "description": "Fallback parsed task",
            "required_capabilities": ["writing"],
            "depends_on": [],
            "priority": 1,
        }
    ])
    mock_agent.query.return_value = valid_json
    runner.get_agent.return_value = mock_agent

    analyzer = TaskAnalyzer(runner)
    breakdown = analyzer.analyze_brief("Perform fallback analysis")

    assert breakdown.parse_success is True
    assert len(breakdown.tasks) == 1
    assert breakdown.tasks[0].id == "task_1"
    assert breakdown.tasks[0].description == "Fallback parsed task"

