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
