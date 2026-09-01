"""Swarm orchestration runner extending GraphRunner for dynamic multi-agent coordination."""

from __future__ import annotations

import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langgraph.graph import END, StateGraph

from orchestrator.capability_index import CapabilityIndex
from orchestrator.execution_planner import ExecutionPlanner, ExecutionWave
from orchestrator.graph_runner import GraphRunner, GraphState, build_state_graph
from tools.engine.core import write_private_json_atomic
from tools.engine.state import validate_identifier
from orchestrator.task_analyzer import Task, TaskAnalyzer, TaskBreakdown
from tools.engine.tokens import truncate_to_tokens
from tools.engine.utils import redact_secrets
from workflows.constants import GraphNodes, SpecialistSlugs
from workflows.schemas.swarm import SwarmConfig, SwarmMetrics, SwarmState


class BudgetExceededError(RuntimeError):
    """Raised before a provider call when the run cannot reserve its budget."""


@dataclass
class BudgetReservation:
    """Prompt and completion capacity held for one provider attempt."""

    prompt_tokens: int
    completion_tokens: int
    label: str


class SwarmRunner(GraphRunner):
    """Orchestrates swarm execution with dynamic specialist selection and parallel execution."""

    def __init__(
        self,
        staff_dir: Path,
        *,
        config: Optional[SwarmConfig] = None,
        verbose: bool = False,
        stream_output: bool = False,
        **kwargs,
    ):
        """
        Initialize SwarmRunner.

        Args:
            staff_dir: Path to specialist YAML directory
            config: Optional SwarmConfig
            verbose: Show detailed progress output
            stream_output: Stream task outputs as JSON events
            **kwargs: Passed to GraphRunner (model_override, temperature, auto_approve, etc.)
        """
        super().__init__(staff_dir, **kwargs)

        # Swarm-specific components
        self.config = config or SwarmConfig()
        self.verbose = verbose
        self.stream_output = stream_output
        self.capability_index = CapabilityIndex(
            staff_dir,
            allowed_tiers=self.config.roster_tiers,
        )
        self.task_analyzer = TaskAnalyzer(self)
        self.execution_planner = ExecutionPlanner()
        self.state_lock = Lock()

        # Validate configuration
        warnings = self.config.validate()
        if warnings:
            for warning in warnings:
                print(f"Config Warning: {warning}", file=sys.stderr)

        # Print index statistics
        stats = self.capability_index.get_statistics()
        print(f"Swarm initialized: {stats['total_specialists']} specialists, "
              f"{stats['total_capabilities']} capabilities indexed", file=sys.stderr)

    def run_swarm(
        self,
        user_brief: str,
        *,
        max_parallel: Optional[int] = None,
        enable_parallel: Optional[bool] = None,
        use_squad: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> SwarmState:
        """
        Execute swarm orchestration workflow.

        Args:
            user_brief: The user's request/brief
            max_parallel: Override config max_parallel
            enable_parallel: Override config enable_parallel
            use_squad: Optional squad name for backward compatibility

        Returns:
            SwarmState with execution results
        """
        # Override config if specified
        if max_parallel is not None:
            self.config.max_parallel = max_parallel
        if enable_parallel is not None:
            self.config.enable_parallel = enable_parallel
        if run_id is not None:
            validate_identifier(run_id, "run_id")

        # Handle backward compatibility with squad mode
        if use_squad:
            return self._run_squad_mode(user_brief, use_squad, run_id=run_id)

        # Build and execute swarm graph
        graph = self._build_swarm_graph()

        initial_state: SwarmState = {
            'user_brief': user_brief,
            'workflow_name': 'planning-swarm',
            'log_title': user_brief,
            'steps': [],
            'max_parallel': self.config.max_parallel,
            'enable_parallel': self.config.enable_parallel,
            'context_strategy': self.config.context_strategy,
            'verbose': self.verbose,
            'stream_output': self.stream_output,
            'max_budget_tokens': self.config.max_budget_tokens,
            'total_tokens_used': 0,
            'max_retries': self.config.max_retries,
            'enable_fallback': self.config.enable_fallback,
            'require_approval': self.config.require_approval,
            'fallback_count': 0,
            'completed_task_ids': [],
            'failed_task_ids': [],
            'blocked_task_ids': [],
            'status': 'RUNNING',
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'budget_exceeded': False,
        }
        if run_id is not None:
            initial_state['run_id'] = run_id

        return self.run_graph(graph, initial_state)

    def _build_swarm_graph(self) -> Any:
        """
        Build the swarm orchestration LangGraph.

        Flow:
        1. Planning (Chief of Staff breaks down brief)
        2. Capability matching (assign specialists to tasks)
        3. Execution planning (create waves)
        4. Wave execution (sequential/parallel based on plan)
        5. Synthesis (Chief of Staff compiles final output)
        """
        graph = StateGraph(SwarmState)

        # Node 1: Planning
        graph.add_node(GraphNodes.PLANNING, self._planning_node)

        # Node 2: Capability Matching
        graph.add_node(GraphNodes.CAPABILITY_MATCHING, self._capability_matching_node)

        # Node 3: Execution Planning
        graph.add_node(GraphNodes.EXECUTION_PLANNING, self._execution_planning_node)

        # Node 4: Wave Execution
        graph.add_node(GraphNodes.WAVE_EXECUTION, self._wave_execution_node)

        # Node 5: Synthesis
        graph.add_node(GraphNodes.SYNTHESIS, self._synthesis_node)

        # Connect nodes
        graph.add_edge(GraphNodes.PLANNING, GraphNodes.CAPABILITY_MATCHING)
        graph.add_edge(GraphNodes.CAPABILITY_MATCHING, GraphNodes.EXECUTION_PLANNING)
        graph.add_edge(GraphNodes.EXECUTION_PLANNING, GraphNodes.WAVE_EXECUTION)
        graph.add_edge(GraphNodes.WAVE_EXECUTION, GraphNodes.SYNTHESIS)
        graph.add_edge(GraphNodes.SYNTHESIS, END)

        graph.set_entry_point(GraphNodes.PLANNING)

        return graph.compile()

    def _planning_node(self, state: SwarmState) -> SwarmState:
        """Node 1: Use Chief of Staff to break down user brief into tasks."""
        start_time = time.time()

        # Get available specialists
        available_specialists = self.capability_index.list_all_specialists()

        # Analyze brief
        breakdown = self.task_analyzer.analyze_brief(
            state.get('user_brief', ''),
            session_id=state.get('run_id'),
            available_specialists=available_specialists,
            state=state,
        )

        # Validate breakdown
        warnings = self.task_analyzer.validate_task_breakdown(breakdown)
        if warnings:
            for warning in warnings:
                print(f"Task Breakdown Warning: {warning}", file=sys.stderr)

        # Log the planning step
        self.record_step(state, GraphNodes.PLANNING, {
            'brief': state.get('user_brief', ''),
            'task_count': len(breakdown.tasks),
            'parse_success': breakdown.parse_success,
            'warnings': warnings,
            'duration_seconds': time.time() - start_time,
        })

        # Create task map
        task_map = {task.id: task for task in breakdown.tasks}

        return {
            **state,
            'task_breakdown': breakdown,
            'task_map': task_map,
            'completed_task_ids': [],
            'failed_task_ids': [],
        }

    def _capability_matching_node(self, state: SwarmState) -> SwarmState:
        """Node 2: Match tasks to specialists based on required capabilities."""
        start_time = time.time()

        breakdown: TaskBreakdown = state['task_breakdown']
        task_map: Dict[str, Task] = state['task_map']

        match_scores = []
        unmatched_capabilities = []

        # Match each task to specialists
        for task in breakdown.tasks:
            matches = self.capability_index.match_specialists(
                task.required_capabilities,
                min_score=self.config.min_capability_match_score,
                max_results=3,  # Keep top 3 for fallback
            )

            if matches:
                # Assign top match
                task.assigned_specialist = matches[0][0]
                task.candidate_specialists = matches
                match_scores.append(matches[0][1])
            else:
                # Fallback to Chief of Staff
                task.assigned_specialist = SpecialistSlugs.CHIEF_OF_STAFF
                task.candidate_specialists = [(SpecialistSlugs.CHIEF_OF_STAFF, 0.5)]
                match_scores.append(0.0)
                unmatched_capabilities.extend(task.required_capabilities)

            # Update task_map
            task_map[task.id] = task

        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0

        self.record_step(state, GraphNodes.CAPABILITY_MATCHING, {
            'avg_match_score': avg_match_score,
            'unmatched_capabilities': unmatched_capabilities,
            'duration_seconds': time.time() - start_time,
        })

        return {
            **state,
            'task_map': task_map,
        }

    def _execution_planning_node(self, state: SwarmState) -> SwarmState:
        """Node 3: Create execution waves based on task dependencies."""
        start_time = time.time()

        breakdown: TaskBreakdown = state['task_breakdown']

        # Create execution plan
        execution_plan = self.execution_planner.create_execution_plan(
            breakdown.tasks,
            max_parallel=state.get('max_parallel', self.config.max_parallel),
        )

        # Log plan
        print("\n" + self.execution_planner.visualize_plan(execution_plan), file=sys.stderr)

        self.record_step(state, GraphNodes.EXECUTION_PLANNING, {
            'total_waves': len(execution_plan.waves),
            'total_tasks': execution_plan.total_tasks,
            'parallel_tasks': execution_plan.parallel_tasks,
            'sequential_tasks': execution_plan.sequential_tasks,
            'duration_seconds': time.time() - start_time,
        })

        return {
            **state,
            'execution_plan': execution_plan,
            'current_wave_id': 0,
            'completed_waves': [],
        }

    def _wave_execution_node(self, state: SwarmState) -> SwarmState:
        """Node 4: Execute all waves in the execution plan."""
        execution_plan: ExecutionPlan = state['execution_plan']
        task_map: Dict[str, Task] = state['task_map']

        total_waves = len(execution_plan.waves)

        # Only the explicit workflow configuration creates an approval gate.
        # ``--no-auto-approve`` must not invent a gate for a graph that did not
        # request one, while configured gates must use the shared handler.
        if self.config.require_approval:
            print("🛑 Swarm execution awaiting approval before wave execution", file=sys.stderr)
            state['approval_required'] = True
            approved = False
            if self.approval_handler is not None or not self.auto_approve:
                try:
                    approved = self.require_approval("swarm:wave_execution", state)
                except (EOFError, OSError, KeyboardInterrupt):
                    approved = False
                except RuntimeError:
                    # A configured gate without a handler cannot prompt from a
                    # non-interactive runner. Treat that unavailable approval
                    # as a safe blocked outcome; errors raised by an explicit
                    # handler still propagate through the handler branch above.
                    if self.approval_handler is not None:
                        raise
                    approved = False
            state['approved'] = approved
            self.record_step(state, "swarm:wave_execution", {"approved": approved})
            if not approved:
                state['status'] = "BLOCKED"
                for wave in execution_plan.waves:
                    for task in wave.tasks:
                        task.result = "[BLOCKED] Execution approval required"
                        state.setdefault('blocked_task_ids', []).append(task.id)
                        # Keep the historical list populated for callers that
                        # use it as "not completed"; the authoritative run
                        # status and blocked_task_ids distinguish this case.
                        if task.id not in state.setdefault('failed_task_ids', []):
                            state['failed_task_ids'].append(task.id)
                        if state.get('stream_output', False):
                            self._stream_task_output(task, task.result, 0.0)
                return state
            state.setdefault('approvals', []).append("swarm:wave_execution")

        # Execute each wave
        for wave_idx, wave in enumerate(execution_plan.waves, 1):
            specialist_count = len(wave.tasks)
            mode_str = "parallel" if wave.parallel else "sequential"

            # Enhanced wave header
            print(
                f"\n>>> Wave {wave_idx}/{total_waves}: "
                f"Running {specialist_count} specialist{'s' if specialist_count > 1 else ''} "
                f"in {mode_str}...",
                file=sys.stderr
            )

            if wave.parallel and state.get('enable_parallel', self.config.enable_parallel):
                # Parallel execution
                self._execute_parallel_wave(wave, state, task_map)
            else:
                # Sequential execution
                self._execute_sequential_wave(wave, state, task_map)

            state['completed_waves'].append(wave.wave_id)

        return state

    def _execute_sequential_wave(
        self,
        wave: ExecutionWave,
        state: SwarmState,
        task_map: Dict[str, Task],
    ) -> None:
        """Execute wave tasks sequentially."""
        for task in wave.tasks:
            self._execute_single_task(task, state, task_map)

    def _execute_parallel_wave(
        self,
        wave: ExecutionWave,
        state: SwarmState,
        task_map: Dict[str, Task],
    ) -> None:
        """
        Execute wave tasks in parallel using ThreadPoolExecutor.

        Each task gets a unique session_id for thread safety.
        """
        def execute_task_wrapper(task: Task) -> Tuple[Task, str, float]:
            """Wrapper for parallel execution that returns (task, result, duration)."""
            start_time = time.time()

            # Build prompt with context
            # Accessing shared state (read-only here usually, but good to be safe if strict)
            # _build_task_prompt reads from task_map and state.
            # Since other threads might be writing to task_map, we should lock reading if we want strict consistency,
            # but usually appending to logs implies we only care about completed tasks.
            # Dependencies are from PREVIOUS waves (sequential), so they are stable. 
            # So reading is likely safe without lock if waves are barriers.
            # However, let's keep it simple.
            
            prompt = self._build_task_prompt(task, state, task_map)

            # Execute with fallback
            result = self._execute_task_with_fallback(task, prompt, state)

            duration = time.time() - start_time

            # Log execution
            # record_step appends to state['steps'], so it needs lock.
            with self.state_lock:
                self.record_step(state, f"task_{task.id}", {
                    'task_id': task.id,
                    'description': task.description,
                    'assigned_specialist': task.assigned_specialist,
                    'duration_seconds': duration,
                    'result_length': len(result),
                    'parallel': True,
                })

            return (task, result, duration)

        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=len(wave.tasks)) as executor:
            # Submit all tasks
            futures = {
                executor.submit(execute_task_wrapper, task): task
                for task in wave.tasks
            }

            # Collect results as they complete
            for future in as_completed(futures):
                task = futures[future]
                try:
                    completed_task, result, duration = future.result()

                    with self.state_lock:
                        # Update task and map
                        completed_task.result = result
                        task_map[completed_task.id] = completed_task
                        if result.startswith("[ERROR]") or completed_task.id in state.get('failed_task_ids', []):
                            if completed_task.id not in state['failed_task_ids']:
                                state['failed_task_ids'].append(completed_task.id)
                        else:
                            state['completed_task_ids'].append(completed_task.id)

                    # Stream task output if enabled
                    if state.get('stream_output', False):
                        self._stream_task_output(completed_task, result, duration)

                    # Typed task outcome message
                    is_failed = completed_task.id in state.get('failed_task_ids', []) or result.startswith("[ERROR]") or result.startswith("[BLOCKED]")
                    if is_failed:
                        if state.get('verbose', False):
                            print(
                                f"  ✗ Failed {completed_task.id} "
                                f"({completed_task.assigned_specialist}, {duration:.1f}s)",
                                file=sys.stderr
                            )
                        else:
                            print(f"  ✗ Failed {completed_task.id}", file=sys.stderr)
                    else:
                        if state.get('verbose', False):
                            print(
                                f"  ✓ Completed {completed_task.id} "
                                f"({completed_task.assigned_specialist}, {duration:.1f}s)",
                                file=sys.stderr
                            )
                        else:
                            print(f"  ✓ Completed {completed_task.id}", file=sys.stderr)

                except Exception as exc:
                    error_msg = f"Task {task.id} generated exception: {exc}"

                    # Stream error event if enabled
                    if state.get('stream_output', False):
                        error_event = {
                            "event": "task_failed",
                            "task_id": task.id,
                            "specialist": task.assigned_specialist,
                            "error": str(exc),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                        print(f"STREAM: {json.dumps(error_event)}", file=sys.stderr)

                    print(f"ERROR: {error_msg}", file=sys.stderr)

                    with self.state_lock:
                        # Mark as failed
                        task.result = f"[ERROR] {error_msg}"
                        task_map[task.id] = task
                        state['failed_task_ids'].append(task.id)

    def _execute_single_task(
        self,
        task: Task,
        state: SwarmState,
        task_map: Dict[str, Task],
    ) -> None:
        """
        Execute a single task with error handling and fallback.

        Args:
            task: Task to execute
            state: Current swarm state
            task_map: Mutable task map to update with results
        """
        start_time = time.time()

        # Build prompt with context from dependencies
        prompt = self._build_task_prompt(task, state, task_map)

        # Execute with fallback
        result = self._execute_task_with_fallback(task, prompt, state)

        duration = time.time() - start_time

        # Store result
        task.result = result
        task_map[task.id] = task
        if result.startswith("[ERROR]") or task.id in state.get('failed_task_ids', []):
            if task.id not in state['failed_task_ids']:
                state['failed_task_ids'].append(task.id)
        else:
            state['completed_task_ids'].append(task.id)

        # Stream task output if enabled
        if state.get('stream_output', False):
            self._stream_task_output(task, result, duration)

        # Typed task outcome message
        is_failed = task.id in state.get('failed_task_ids', []) or result.startswith("[ERROR]") or result.startswith("[BLOCKED]")
        if is_failed:
            if state.get('verbose', False):
                print(
                    f"  ✗ Failed {task.id} "
                    f"({task.assigned_specialist}, {duration:.1f}s)",
                    file=sys.stderr
                )
            else:
                print(f"  ✗ Failed {task.id}", file=sys.stderr)
        else:
            if state.get('verbose', False):
                print(
                    f"  ✓ Completed {task.id} "
                    f"({task.assigned_specialist}, {duration:.1f}s)",
                    file=sys.stderr
                )
            else:
                print(f"  ✓ Completed {task.id}", file=sys.stderr)

        # Log execution
        self.record_step(state, f"task_{task.id}", {
            'task_id': task.id,
            'description': task.description,
            'assigned_specialist': task.assigned_specialist,
            'duration_seconds': duration,
            'result_length': len(result),
        })

    def _stream_task_output(
        self,
        task: Task,
        result: str,
        duration: float,
    ) -> None:
        """
        Stream task output to stderr in structured format.

        Output format (JSON Lines):
        {
            "event": "task_completed",
            "task_id": "task_1",
            "specialist": "market-analyst",
            "duration_seconds": 4.2,
            "result_preview": "First 500 chars...",
            "result_length": 2048
        }
        """
        # Truncate result for preview
        max_preview = 500
        preview = result[:max_preview]
        if len(result) > max_preview:
            preview += "... [truncated]"

        if result.startswith("[BLOCKED]"):
            event_type = "task_blocked"
        elif result.startswith("[ERROR]"):
            event_type = "task_failed"
        else:
            event_type = "task_completed"

        event = {
            "event": event_type,
            "task_id": task.id,
            "specialist": task.assigned_specialist,
            "duration_seconds": round(duration, 2),
            "result_preview": preview,
            "result_length": len(result),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Output as JSON line to stderr
        print(f"STREAM: {json.dumps(event)}", file=sys.stderr)

    def _build_task_prompt(
        self,
        task: Task,
        state: SwarmState,
        task_map: Dict[str, Task],
    ) -> str:
        """Build prompt for task execution with context from dependencies."""
        # Gather context from dependency tasks
        dependency_context = ""

        if task.depends_on:
            dependency_context = "\n\n--- CONTEXT FROM PREVIOUS TASKS ---\n"

            for dep_id in task.depends_on:
                dep_task = task_map.get(dep_id)
                if dep_task and dep_task.result:
                    # Truncate by actual token count (not characters).
                    result = truncate_to_tokens(
                        dep_task.result, self.config.max_context_tokens
                    )

                    dependency_context += f"\n### Output from {dep_id} ({dep_task.assigned_specialist}):\n"
                    dependency_context += f"{result}\n"

            dependency_context += "\n--- END CONTEXT ---\n\n"

        # Build full prompt
        prompt = f"""TASK: {task.description}

ORIGINAL USER BRIEF: {state.get('user_brief', '')}
{dependency_context}
Please complete this task. Be thorough and specific in your response.
        """
        return prompt

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Use a conservative, deterministic estimate when providers give no usage."""
        return max(1, (len(str(text)) + 3) // 4)

    def _budget_limit(self, state: SwarmState) -> Optional[int]:
        """Resolve a limit without treating an explicit zero as unlimited."""
        if self.config.max_budget_tokens is not None:
            return self.config.max_budget_tokens
        return state.get("max_budget_tokens")

    def _ensure_budget_ledger(self, state: SwarmState) -> Dict[str, Any]:
        """Create the per-run ledger and mirror it into durable state."""
        raw_ledger = state.get("budget_ledger")
        ledger = raw_ledger if isinstance(raw_ledger, dict) else {}
        limit = self._budget_limit(state)
        used = max(
            int(ledger.get("used", 0) or 0),
            int(state.get("total_tokens_used", 0) or 0),
        )
        prompt_tokens = max(
            int(ledger.get("prompt_tokens", 0) or 0),
            int(state.get("total_prompt_tokens", 0) or 0),
        )
        completion_tokens = max(
            int(ledger.get("completion_tokens", 0) or 0),
            int(state.get("total_completion_tokens", 0) or 0),
        )
        ledger.update(
            {
                "limit": limit,
                "used": used,
                "reserved": max(0, int(ledger.get("reserved", 0) or 0)),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "calls": max(0, int(ledger.get("calls", 0) or 0)),
                "failed_calls": max(0, int(ledger.get("failed_calls", 0) or 0)),
                "overrun_calls": max(0, int(ledger.get("overrun_calls", 0) or 0)),
            }
        )
        state["budget_ledger"] = ledger
        state["total_tokens_used"] = used
        state["total_prompt_tokens"] = prompt_tokens
        state["total_completion_tokens"] = completion_tokens
        state["budget_reserved_tokens"] = ledger["reserved"]
        if limit is not None and used >= limit:
            state["budget_exceeded"] = True
        return ledger

    def _reserve_budget(
        self,
        state: SwarmState,
        prompt: str,
        label: str,
    ) -> BudgetReservation:
        """Reserve prompt plus completion capacity under the run lock."""
        prompt_tokens = self._estimate_tokens(prompt)
        with self.state_lock:
            ledger = self._ensure_budget_ledger(state)
            limit = ledger["limit"]
            if limit is not None:
                available = int(limit) - ledger["used"] - ledger["reserved"]
                if available <= prompt_tokens:
                    state["budget_exceeded"] = True
                    raise BudgetExceededError(
                        "Task halted: token budget exceeded before execution "
                        f"({ledger['used'] + ledger['reserved'] + prompt_tokens + 1} > {limit})"
                    )
                completion_tokens = min(
                    self.config.max_completion_tokens_per_call,
                    available - prompt_tokens,
                )
                if completion_tokens < 1:
                    state["budget_exceeded"] = True
                    raise BudgetExceededError(
                        f"Task halted: token budget exhausted before {label}"
                    )
            else:
                completion_tokens = self.config.max_completion_tokens_per_call

            reservation = BudgetReservation(prompt_tokens, completion_tokens, label)
            ledger["reserved"] += prompt_tokens + completion_tokens
            ledger["calls"] += 1
            state["budget_reserved_tokens"] = ledger["reserved"]
            return reservation

    def _assert_budget_capacity(
        self,
        state: SwarmState,
        prompt: str,
        label: str,
    ) -> None:
        """Reject work before constructing an agent when no call can fit."""
        prompt_tokens = self._estimate_tokens(prompt)
        with self.state_lock:
            ledger = self._ensure_budget_ledger(state)
            limit = ledger["limit"]
            if limit is None:
                return
            available = int(limit) - ledger["used"] - ledger["reserved"]
            if available <= prompt_tokens:
                state["budget_exceeded"] = True
                raise BudgetExceededError(
                    "Task halted: token budget exceeded before execution "
                    f"({ledger['used'] + ledger['reserved'] + prompt_tokens + 1} > {limit})"
                )

    def _settle_budget(
        self,
        state: SwarmState,
        reservation: BudgetReservation,
        agent: Any,
        response: str,
        *,
        failed: bool = False,
    ) -> None:
        """Release a reservation and account one provider attempt exactly once."""
        usage = getattr(agent, "last_usage", None) if agent is not None else None
        if not isinstance(usage, dict):
            usage = {}
        observed_prompt = usage.get("prompt_tokens") or usage.get("input_tokens")
        observed_completion = usage.get("completion_tokens") or usage.get("output_tokens")
        prompt_tokens = (
            int(observed_prompt)
            if isinstance(observed_prompt, (int, float)) and observed_prompt >= 0
            else reservation.prompt_tokens
        )
        completion_tokens = (
            int(observed_completion)
            if isinstance(observed_completion, (int, float)) and observed_completion >= 0
            else (0 if failed else self._estimate_tokens(response))
        )

        with self.state_lock:
            ledger = self._ensure_budget_ledger(state)
            reservation_total = reservation.prompt_tokens + reservation.completion_tokens
            ledger["reserved"] = max(0, ledger["reserved"] - reservation_total)
            if failed:
                ledger["failed_calls"] += 1

            # The provider receives max_tokens for bounded calls.  Clamp the
            # ledger to the reservation as a second line of defense when a
            # provider lies about usage or a fake/test provider ignores it.
            if prompt_tokens > reservation.prompt_tokens or completion_tokens > reservation.completion_tokens:
                ledger["overrun_calls"] += 1
            prompt_tokens = min(prompt_tokens, reservation.prompt_tokens)
            completion_tokens = min(completion_tokens, reservation.completion_tokens)

            limit = ledger["limit"]
            if limit is not None:
                remaining = max(0, int(limit) - ledger["used"])
                prompt_tokens = min(prompt_tokens, remaining)
                completion_tokens = min(completion_tokens, max(0, remaining - prompt_tokens))

            ledger["prompt_tokens"] += prompt_tokens
            ledger["completion_tokens"] += completion_tokens
            ledger["used"] += prompt_tokens + completion_tokens
            state["total_prompt_tokens"] = ledger["prompt_tokens"]
            state["total_completion_tokens"] = ledger["completion_tokens"]
            state["total_tokens_used"] = ledger["used"]
            state["budget_reserved_tokens"] = ledger["reserved"]
            if limit is not None:
                threshold = int(limit * self.config.budget_warning_threshold)
                if ledger["used"] >= threshold and not state.get("budget_warning_emitted", False):
                    state["budget_warning_emitted"] = True
                    print(
                        f"WARNING: Swarm budget threshold reached ({ledger['used']}/{limit} tokens)",
                        file=sys.stderr,
                    )
                if ledger["used"] >= limit:
                    state["budget_exceeded"] = True

    def query_agent_with_budget(
        self,
        agent: Any,
        prompt: str,
        state: Optional[SwarmState] = None,
        *,
        label: str = "provider call",
    ) -> str:
        """Query an agent through the shared per-run budget ledger."""
        if state is None:
            return agent.query(prompt)

        reservation = self._reserve_budget(state, prompt, label)
        try:
            if self._budget_limit(state) is None:
                response = agent.query(prompt)
            else:
                response = agent.query(prompt, max_tokens=reservation.completion_tokens)
            response_text = response if isinstance(response, str) else str(response)
            if len(response_text) > reservation.completion_tokens * 4:
                response_text = response_text[: reservation.completion_tokens * 4]
            self._settle_budget(state, reservation, agent, response_text)
            return response_text
        except Exception:
            self._settle_budget(state, reservation, agent, "", failed=True)
            raise

    def _account_unstarted_attempt(self, state: SwarmState, prompt: str, label: str) -> None:
        """Count a failed agent construction/dispatch attempt without a provider call."""
        try:
            reservation = self._reserve_budget(state, prompt, label)
        except BudgetExceededError:
            return
        self._settle_budget(state, reservation, None, "", failed=True)

    def _mark_task_budget_failure(self, task: Task, state: SwarmState, error: Exception) -> str:
        """Make budget exhaustion visible as a failed task and durable state."""
        message = str(error)
        with self.state_lock:
            state["budget_exceeded"] = True
            if task.id not in state.setdefault("failed_task_ids", []):
                state["failed_task_ids"].append(task.id)
        print(f"ERROR: Task {task.id} - {message}", file=sys.stderr)
        return f"[ERROR] {message}"

    def _execute_task_with_fallback(
        self,
        task: Task,
        prompt: str,
        state: SwarmState,
    ) -> str:
        """
        Execute task with multi-level fallback, retries, and budget controls.

        Fallback chain:
        1. Primary specialist (with retries)
        2. Alternative specialist (if available and fallback enabled)
        3. Chief of Staff (if fallback enabled)
        4. Error message
        """
        session_id = state.get('run_id')

        def execute_attempt(agent_slug: str, attempt_prompt: str, suffix: str) -> str:
            self._assert_budget_capacity(
                state,
                attempt_prompt,
                f"{agent_slug} task {task.id}",
            )
            try:
                agent = self.get_agent(agent_slug, session_id=f"{session_id}_{task.id}{suffix}")
            except Exception:
                self._account_unstarted_attempt(state, attempt_prompt, f"{agent_slug} construction")
                raise
            return self.query_agent_with_budget(
                agent,
                attempt_prompt,
                state,
                label=f"{agent_slug} task {task.id}",
            )

        # Every retry is a fresh reservation.  A failed provider attempt still
        # consumes its prompt reservation, so retries and fallbacks cannot
        # silently exceed the run's ledger.
        total_attempts = 1 + self.config.max_retries
        last_error: Optional[Exception] = None
        budget_error: Optional[BudgetExceededError] = None
        for attempt in range(total_attempts):
            try:
                return execute_attempt(task.assigned_specialist, prompt, "")
            except BudgetExceededError as exc:
                budget_error = exc
                last_error = exc
                break
            except Exception as exc:
                last_error = exc
                print(
                    f"ERROR: Task {task.id} - Attempt {attempt + 1}/{total_attempts} "
                    f"failed with {task.assigned_specialist}: {exc}",
                    file=sys.stderr,
                )

        if budget_error is not None:
            return self._mark_task_budget_failure(task, state, budget_error)

        # If fallback is disabled, halt here.
        if not self.config.enable_fallback:
            with self.state_lock:
                if task.id not in state.setdefault('failed_task_ids', []):
                    state['failed_task_ids'].append(task.id)
            return f"[ERROR] Task failed (fallback disabled): {last_error}"

        # Try an alternative specialist only while a complete reservation is
        # available.  BudgetExceededError deliberately stops the chain.
        if task.candidate_specialists and len(task.candidate_specialists) > 1:
            fallback_slug = task.candidate_specialists[1][0]
            try:
                result = execute_attempt(fallback_slug, prompt, "_alt")
                with self.state_lock:
                    state['fallback_count'] = state.get('fallback_count', 0) + 1
                return f"[Fallback: {fallback_slug}]\n{result}"
            except BudgetExceededError as exc:
                return self._mark_task_budget_failure(task, state, exc)
            except Exception as alt_error:
                last_error = alt_error
                print(
                    f"ERROR: Alternative specialist {fallback_slug} also failed: {alt_error}",
                    file=sys.stderr,
                )

        # Try Chief of Staff fallback only while budget remains.
        if task.assigned_specialist != SpecialistSlugs.CHIEF_OF_STAFF:
            cos_prompt = f"Task failed. Please handle:\n{prompt}"
            try:
                result = execute_attempt(
                    SpecialistSlugs.CHIEF_OF_STAFF,
                    cos_prompt,
                    "_cos",
                )
                with self.state_lock:
                    state['fallback_count'] = state.get('fallback_count', 0) + 1
                return f"[CoS Fallback]\n{result}"
            except BudgetExceededError as exc:
                return self._mark_task_budget_failure(task, state, exc)
            except Exception as cos_error:
                last_error = cos_error
                print(f"ERROR: Chief of Staff fallback failed: {cos_error}", file=sys.stderr)

        # Final fallback: return an explicit failed task result.
        with self.state_lock:
            if task.id not in state.setdefault('failed_task_ids', []):
                state['failed_task_ids'].append(task.id)
        return f"[ERROR] Task failed: {last_error}"

    def _synthesis_failure(
        self,
        state: SwarmState,
        start_time: float,
        message: str,
        reason: str,
    ) -> SwarmState:
        """Return an explicit failed result when synthesis cannot run."""
        final_output = f"[ERROR] {message}"
        state['status'] = "FAILED"
        state['error'] = message
        self.record_step(state, GraphNodes.SYNTHESIS, {
            'duration_seconds': time.time() - start_time,
            'final_output_length': len(final_output),
            'failed': True,
            'reason': reason,
        })
        metrics = self._calculate_metrics(state, start_time)
        return {
            **state,
            'final_output': final_output,
            'metrics': metrics.to_dict(),
        }

    def _synthesis_node(self, state: SwarmState) -> SwarmState:
        """Node 5: Chief of Staff synthesizes final output from all task results."""
        start_time = time.time()

        # If execution was blocked by approval gate
        if state.get('approval_required') and not state.get('approved', False):
            final_output = "[BLOCKED] Execution approval required"
            state['status'] = "BLOCKED"
            metrics = self._calculate_metrics(state, start_time)
            return {
                **state,
                'final_output': final_output,
                'metrics': metrics.to_dict(),
            }

        with self.state_lock:
            ledger = self._ensure_budget_ledger(state)
            if ledger["limit"] is not None and ledger["used"] + ledger["reserved"] >= ledger["limit"]:
                state['budget_exceeded'] = True
                state['status'] = "FAILED"
                final_output = "[ERROR] Token budget exhausted before synthesis"
                self.record_step(state, GraphNodes.SYNTHESIS, {
                    'duration_seconds': time.time() - start_time,
                    'final_output_length': len(final_output),
                    'skipped': True,
                    'reason': 'budget_exhausted',
                })
                metrics = self._calculate_metrics(state, start_time)
                return {
                    **state,
                    'final_output': final_output,
                    'metrics': metrics.to_dict(),
                }

        task_map: Dict[str, Task] = state['task_map']

        # Compile all task results
        results_text = ""
        for task_id, task in task_map.items():
            if task.result:
                results_text += f"\n### {task_id}: {task.description}\n"
                results_text += f"Specialist: {task.assigned_specialist}\n"
                results_text += f"Output:\n{task.result}\n"
                results_text += "\n" + "="*60 + "\n"

        # Build synthesis prompt
        prompt = f"""You are the Chief of Staff reviewing the completed work from your swarm of specialists.

ORIGINAL USER BRIEF:
{state.get('user_brief', '')}

SPECIALIST OUTPUTS:
{results_text}

TASK:
Review all the specialist outputs above and synthesize them into a final, cohesive deliverable that fully addresses the user's brief.

Ensure:
1. All task outputs are integrated logically
2. The final output is complete and actionable
3. Quality standards are met
4. The response directly addresses the user's original request

Return the final synthesized output.
"""

        # Query Chief of Staff.  Provider construction and budget refusal are
        # terminal run outcomes, not graph exceptions that erase the final
        # status and output from the caller's result.
        try:
            agent = self.get_agent(SpecialistSlugs.CHIEF_OF_STAFF, session_id=state.get('run_id'))
        except Exception as exc:
            self._account_unstarted_attempt(state, prompt, "chief-of-staff synthesis construction")
            return self._synthesis_failure(
                state,
                start_time,
                f"Synthesis agent could not be created: {exc}",
                "agent_construction_failed",
            )

        try:
            final_output = self.query_agent_with_budget(
                agent,
                prompt,
                state,
                label="chief-of-staff synthesis",
            )
        except BudgetExceededError as exc:
            state['budget_exceeded'] = True
            return self._synthesis_failure(
                state,
                start_time,
                str(exc),
                "budget_exhausted",
            )
        except Exception as exc:
            return self._synthesis_failure(
                state,
                start_time,
                f"Synthesis provider call failed: {exc}",
                "provider_failed",
            )

        if state.get('failed_task_ids'):
            state['status'] = "FAILED"
            final_output = f"[PARTIAL]\n{final_output}"
        else:
            state['status'] = "COMPLETED"

        # Calculate metrics
        metrics = self._calculate_metrics(state, start_time)

        self.record_step(state, GraphNodes.SYNTHESIS, {
            'duration_seconds': time.time() - start_time,
            'final_output_length': len(final_output),
        })

        return {
            **state,
            'final_output': final_output,
            'metrics': metrics.to_dict(),
        }

    def _calculate_metrics(self, state: SwarmState, synthesis_start: float) -> SwarmMetrics:
        """Calculate execution metrics."""
        from orchestrator.execution_planner import ExecutionPlan

        execution_plan = state.get('execution_plan')
        task_map: Dict[str, Task] = state.get('task_map', {})

        # Count unique specialists used
        specialists_used = {}
        for task in task_map.values():
            if task.assigned_specialist:
                specialists_used[task.assigned_specialist] = specialists_used.get(task.assigned_specialist, 0) + 1

        # Calculate avg match score
        match_scores = []
        for task in task_map.values():
            if task.candidate_specialists:
                match_scores.append(task.candidate_specialists[0][1])
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0

        # Extract unmatched capabilities from logs
        unmatched = []
        for step in state.get('steps', []):
            if step.get('step') == GraphNodes.CAPABILITY_MATCHING:
                unmatched = step.get('unmatched_capabilities', [])

        # Calculate total duration
        total_duration = 0.0
        for step in state.get('steps', []):
            total_duration += step.get('duration_seconds', 0.0)

        # Estimate theoretical sequential time
        task_durations = [step.get('duration_seconds', 0) for step in state.get('steps', []) if step.get('step', '').startswith('task_')]
        theoretical_sequential = sum(task_durations)
        speedup_factor = theoretical_sequential / total_duration if total_duration > 0 else 1.0

        # Handle execution_plan (might be None or object)
        total_tasks = 0
        parallel_tasks = 0
        sequential_tasks = 0

        if execution_plan:
            if hasattr(execution_plan, 'total_tasks'):
                total_tasks = execution_plan.total_tasks
                parallel_tasks = execution_plan.parallel_tasks
                sequential_tasks = execution_plan.sequential_tasks
            else:
                # Fallback: count from task_map
                total_tasks = len(task_map)

        return SwarmMetrics(
            total_tasks=total_tasks,
            parallel_tasks=parallel_tasks,
            sequential_tasks=sequential_tasks,
            total_duration_seconds=total_duration,
            avg_task_duration_seconds=sum(task_durations) / len(task_durations) if task_durations else 0.0,
            specialists_used=specialists_used,
            unique_specialists=len(specialists_used),
            avg_match_score=avg_match_score,
            unmatched_capabilities=unmatched,
            speedup_factor=speedup_factor,
            parallelization_efficiency=speedup_factor / parallel_tasks if parallel_tasks > 0 else 0.0,
            total_prompt_tokens=state.get('total_prompt_tokens', 0),
            total_completion_tokens=state.get('total_completion_tokens', 0),
            total_tokens=state.get('total_tokens_used', 0),
            failed_tasks=len(state.get('failed_task_ids', [])),
            fallback_count=state.get('fallback_count', 0),
        )

    def _run_squad_mode(
        self,
        user_brief: str,
        squad_name: str,
        *,
        run_id: Optional[str] = None,
    ) -> SwarmState:
        """Backward compatibility: run in squad mode."""
        print(f"WARNING: Squad mode '{squad_name}' is deprecated. Upgrading to Swarm execution.", file=sys.stderr)
        
        # Load squads config to find preferred specialists
        squads_path = self.staff_dir.parent / "squads.json"
        
        prefix = f"[Context: You are operating as the '{squad_name}' squad] "
        
        if squads_path.exists():
            try:
                with open(squads_path) as f:
                    data = json.load(f)
                    if squad_name in data:
                        # Extract specialist names
                        staff_paths = data[squad_name].get("staff", [])
                        specialists = [Path(p).stem for p in staff_paths]
                        if specialists:
                            prefix += f"\nPreferred Specialists: {', '.join(specialists)}\n"
            except Exception as e:
                print(f"Warning: Could not load squad config: {e}", file=sys.stderr)

        # Combine with brief
        enhanced_brief = f"{prefix}\n\n{user_brief}"
        
        # Run standard swarm (disable recursion)
        return self.run_swarm(enhanced_brief, use_squad=None, run_id=run_id)

    def _persist_log(self, state: SwarmState) -> Path:
        """Write run metadata and steps to disk, handling dataclass serialization."""
        run_id = state.get("run_id", "unknown")
        log_path = self._resolve_log_path(state)
        state["log_path"] = str(log_path)

        # Create serializable state
        serializable_state = {}
        for k, v in state.items():
            if k == "steps":
                continue
            
            # recursive conversion for specific keys
            if k in ["task_breakdown", "execution_plan"]:
                serializable_state[k] = v
            elif k == "task_map":
                # Convert Dict[str, Task] -> Dict[str, dict]
                serializable_state[k] = {
                    tid: task
                    for tid, task in v.items()
                }
            else:
                serializable_state[k] = v

        log = {
            "run_id": run_id,
            "status": state.get("status", "UNKNOWN"),
            "log_path": str(log_path),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "steps": state.get("steps", []),
            "state": serializable_state,
        }
        
        write_private_json_atomic(log_path, log)
        return log_path
