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


def test_execution_planner_rejects_invalid_inputs():
    """ExecutionPlanner must reject non-positive max_parallel, duplicates, and missing deps."""
    import pytest
    from orchestrator.execution_planner import ExecutionPlanner
    from orchestrator.task_analyzer import Task

    planner = ExecutionPlanner()

    # max_parallel = 0
    t1 = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    with pytest.raises(ValueError, match="max_parallel must be an integer >= 1"):
        planner.create_execution_plan([t1], max_parallel=0)

    with pytest.raises(ValueError, match="max_parallel must be an integer >= 1"):
        planner.create_execution_plan([t1], max_parallel=True)

    # Duplicate task IDs
    t2 = Task(id="t1", description="Task 2", required_capabilities=["cap"], depends_on=[], priority=1)
    with pytest.raises(ValueError, match="Duplicate task ID"):
        planner.create_execution_plan([t1, t2])

    # Self-dependency
    t3 = Task(id="t3", description="Task 3", required_capabilities=["cap"], depends_on=["t3"], priority=1)
    with pytest.raises(ValueError, match="cannot depend on itself"):
        planner.create_execution_plan([t3])

    # Missing dependency
    t4 = Task(id="t4", description="Task 4", required_capabilities=["cap"], depends_on=["non_existent"], priority=1)
    with pytest.raises(ValueError, match="depends on non-existent task"):
        planner.create_execution_plan([t4])

    malformed_dependencies = Task(
        id="t5",
        description="Malformed dependencies",
        required_capabilities=["cap"],
        depends_on=None,
        priority=1,
    )
    with pytest.raises(ValueError, match="dependencies must be a list"):
        planner.create_execution_plan([malformed_dependencies])

    unsafe = Task(id="task 1", description="Unsafe", required_capabilities=["cap"], depends_on=[], priority=1)
    with pytest.raises(ValueError, match="forbidden characters"):
        planner.create_execution_plan([unsafe])


def test_swarm_runner_approval_gate_blocks_wave_execution(tmp_path):
    """When auto_approve=False and require_approval=True, waves should be blocked."""
    from orchestrator.task_analyzer import Task
    from orchestrator.execution_planner import ExecutionPlan, ExecutionWave

    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(require_approval=True),
        auto_approve=False,
        log_dir=tmp_path / "logs",
    )

    t1 = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    wave = ExecutionWave(wave_id=1, tasks=[t1], parallel=False)
    plan = ExecutionPlan(waves=[wave], total_tasks=1, parallel_tasks=0, sequential_tasks=1)

    state = {
        "execution_plan": plan,
        "task_map": {"t1": t1},
        "require_approval": True,
        "failed_task_ids": [],
        "completed_waves": [],
    }

    res_state = runner._wave_execution_node(state)
    assert res_state.get("approval_required") is True
    assert res_state.get("approved") is False
    assert "t1" in res_state["failed_task_ids"]
    assert res_state["completed_waves"] == []


def test_swarm_runner_budget_limit_halts_tasks(tmp_path):
    """When token budget is exhausted, further execution halts."""
    from orchestrator.task_analyzer import Task

    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(max_budget_tokens=10),
        log_dir=tmp_path / "logs",
    )

    t1 = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    state = {
        "run_id": "test_run",
        "total_tokens_used": 15,  # Exceeded budget (15 >= 10)
        "failed_task_ids": [],
    }

    res = runner._execute_task_with_fallback(t1, "prompt", state)
    assert "[ERROR]" in res
    assert "budget exceeded" in res
    assert "t1" in state["failed_task_ids"]


def test_swarm_runner_persists_log_private_permissions(tmp_path):
    """Swarm logs must be created with strict 0600 permissions."""
    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(),
        log_dir=tmp_path / "logs",
    )

    state = {
        "run_id": "test_perm_run",
        "workflow_name": "perm-test",
        "log_title": "Test permissions",
        "steps": [],
    }

    log_path = runner._persist_log(state)
    assert log_path.exists()
    assert (log_path.stat().st_mode & 0o777) == 0o600


def test_swarm_runner_config_approval_cannot_be_bypassed_by_auto_approve(tmp_path):
    """Configured require_approval cannot be bypassed by CLI auto_approve flag."""
    from orchestrator.task_analyzer import Task
    from orchestrator.execution_planner import ExecutionPlan, ExecutionWave

    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(require_approval=True),
        auto_approve=True,  # Attempting to bypass
        log_dir=tmp_path / "logs",
    )

    t1 = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    wave = ExecutionWave(wave_id=1, tasks=[t1], parallel=False)
    plan = ExecutionPlan(waves=[wave], total_tasks=1, parallel_tasks=0, sequential_tasks=1)

    state = {
        "execution_plan": plan,
        "task_map": {"t1": t1},
        "require_approval": True,
        "failed_task_ids": [],
        "completed_waves": [],
    }

    res_state = runner._wave_execution_node(state)
    assert res_state.get("approval_required") is True
    assert res_state.get("approved") is False
    assert "t1" in res_state["failed_task_ids"]


def test_swarm_runner_budget_reservation_prevents_overrun(tmp_path):
    """Estimated prompt tokens that exceed remaining budget halt before execution."""
    from orchestrator.task_analyzer import Task

    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(max_budget_tokens=20),
        log_dir=tmp_path / "logs",
    )

    t1 = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    # 15 tokens used, 5 remaining. A 40-char prompt = 10 estimated tokens (> 5 remaining).
    state = {
        "run_id": "test_run",
        "total_tokens_used": 15,
        "failed_task_ids": [],
    }

    res = runner._execute_task_with_fallback(t1, "x" * 40, state)
    assert "[ERROR]" in res
    assert "budget exceeded before execution" in res
    assert "t1" in state["failed_task_ids"]


def test_swarm_budget_passes_remaining_completion_capacity_and_caps_response(tmp_path):
    """A model call must receive the reserved completion limit and stay within budget."""
    from orchestrator.task_analyzer import Task

    class FakeAgent:
        def __init__(self):
            self.max_tokens = None

        def query(self, prompt, *, max_tokens=None):
            self.max_tokens = max_tokens
            return "x" * 200

    agent = FakeAgent()
    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(max_budget_tokens=5, max_completion_tokens_per_call=256),
        log_dir=tmp_path / "logs",
    )
    runner.get_agent = lambda *_args, **_kwargs: agent
    task = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    state = {"run_id": "test_run", "total_tokens_used": 0, "failed_task_ids": []}

    result = runner._execute_task_with_fallback(task, "prompt", state)

    assert agent.max_tokens == 3
    assert len(result) <= 12
    assert state["total_tokens_used"] <= 5
    assert state["total_completion_tokens"] <= 3


def test_swarm_synthesis_stops_when_budget_is_exhausted(tmp_path):
    """Synthesis must not make a new provider call after the ledger is exhausted."""
    from orchestrator.task_analyzer import Task

    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(max_budget_tokens=5),
        log_dir=tmp_path / "logs",
    )
    runner.get_agent = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected call"))
    task = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1, result="done")
    state = {
        "run_id": "test_run",
        "total_tokens_used": 5,
        "task_map": {"t1": task},
        "failed_task_ids": [],
        "steps": [],
    }

    result = runner._synthesis_node(state)

    assert result["status"] == "FAILED"
    assert "budget" in result["final_output"].lower()


def test_swarm_synthesis_budget_refusal_returns_failed_result(tmp_path):
    """A synthesis prompt that cannot fit must not escape as an unstructured exception."""
    from orchestrator.task_analyzer import Task

    class FakeAgent:
        def query(self, prompt, *, max_tokens=None):
            raise AssertionError("provider must not be called after budget refusal")

    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(max_budget_tokens=20),
        log_dir=tmp_path / "logs",
    )
    runner.get_agent = lambda *_args, **_kwargs: FakeAgent()
    task = Task(
        id="t1",
        description="Task 1",
        required_capabilities=["cap"],
        depends_on=[],
        priority=1,
        result="x" * 400,
    )
    state = {
        "run_id": "test_run",
        "user_brief": "brief",
        "task_map": {"t1": task},
        "failed_task_ids": [],
        "steps": [],
        "total_tokens_used": 0,
    }

    result = runner._synthesis_node(state)

    assert result["status"] == "FAILED"
    assert result["final_output"].startswith("[ERROR]")
    assert "budget" in result["final_output"].lower()
    assert result["steps"][-1]["reason"] == "budget_exhausted"


def test_swarm_approval_handler_is_used_for_configured_gate(tmp_path):
    """Configured approval must invoke the handler instead of unconditionally blocking."""
    from orchestrator.task_analyzer import Task
    from orchestrator.execution_planner import ExecutionPlan, ExecutionWave

    calls = []
    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(require_approval=True),
        auto_approve=False,
        approval_handler=lambda gate, state: calls.append(gate) or True,
        log_dir=tmp_path / "logs",
    )
    runner._execute_sequential_wave = lambda wave, state, task_map: None
    task = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    state = {
        "execution_plan": ExecutionPlan(
            waves=[ExecutionWave(wave_id=1, tasks=[task], parallel=False)],
            total_tasks=1,
            parallel_tasks=0,
            sequential_tasks=1,
        ),
        "task_map": {"t1": task},
        "failed_task_ids": [],
        "blocked_task_ids": [],
        "completed_waves": [],
    }

    result = runner._wave_execution_node(state)

    assert calls == ["swarm:wave_execution"]
    assert result["approved"] is True
    assert result.get("status") != "BLOCKED"


def test_swarm_auto_approve_false_does_not_create_an_implicit_gate(tmp_path):
    """Without configured approval, --no-auto-approve must not block the graph."""
    from orchestrator.task_analyzer import Task
    from orchestrator.execution_planner import ExecutionPlan, ExecutionWave

    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(require_approval=False),
        auto_approve=False,
        log_dir=tmp_path / "logs",
    )
    runner._execute_sequential_wave = lambda wave, state, task_map: None
    task = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    state = {
        "execution_plan": ExecutionPlan(
            waves=[ExecutionWave(wave_id=1, tasks=[task], parallel=False)],
            total_tasks=1,
            parallel_tasks=0,
            sequential_tasks=1,
        ),
        "task_map": {"t1": task},
        "failed_task_ids": [],
        "completed_waves": [],
    }

    result = runner._wave_execution_node(state)
    assert result.get("status") != "BLOCKED"


def test_swarm_stream_event_type_reflects_task_failure(tmp_path, capsys):
    from orchestrator.task_analyzer import Task

    runner = SwarmRunner(staff_dir=Path("staff"), config=SwarmConfig(), log_dir=tmp_path / "logs")
    task = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    runner._stream_task_output(task, "[ERROR] failed", 0.1)
    assert '"event": "task_failed"' in capsys.readouterr().err


def test_swarm_approval_block_emits_blocked_task_event(tmp_path, capsys):
    """A blocked wave must use a blocked event rather than a completion event."""
    from orchestrator.task_analyzer import Task
    from orchestrator.execution_planner import ExecutionPlan, ExecutionWave

    task = Task(id="t1", description="Task 1", required_capabilities=["cap"], depends_on=[], priority=1)
    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(require_approval=True),
        auto_approve=False,
        approval_handler=lambda _gate, _state: False,
        stream_output=True,
        log_dir=tmp_path / "logs",
    )

    result = runner._wave_execution_node({
        "execution_plan": ExecutionPlan(
            waves=[ExecutionWave(wave_id=1, tasks=[task], parallel=False)],
            total_tasks=1,
            parallel_tasks=0,
            sequential_tasks=1,
        ),
        "task_map": {"t1": task},
        "failed_task_ids": [],
        "blocked_task_ids": [],
        "completed_waves": [],
        "stream_output": True,
    })

    assert result["status"] == "BLOCKED"
    assert '"event": "task_blocked"' in capsys.readouterr().err


def test_planning_swarm_cli_exposes_budget_and_approval_controls():
    """The flagship command must expose the controls enforced by the runner."""
    from workflows.planning_swarm import build_parser

    args = build_parser().parse_args([
        "brief",
        "--budget",
        "25",
        "--require-approval",
        "--no-auto-approve",
    ])

    assert args.budget == 25
    assert args.require_approval is True
    assert args.no_auto_approve is True


def test_swarm_propagates_caller_run_id_into_initial_state(tmp_path):
    """A dispatcher-provided correlation ID must reach the nested run state."""
    runner = SwarmRunner(
        staff_dir=Path("staff"),
        config=SwarmConfig(),
        log_dir=tmp_path / "logs",
    )
    runner.run_graph = lambda _graph, state: state

    result = runner.run_swarm("brief", run_id="20260831_120000_deadbeef")

    assert result["run_id"] == "20260831_120000_deadbeef"
