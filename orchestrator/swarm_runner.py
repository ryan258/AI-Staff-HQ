"""Swarm orchestration runner extending GraphRunner for dynamic multi-agent coordination."""

from __future__ import annotations

import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langgraph.graph import END, StateGraph

from orchestrator.capability_index import CapabilityIndex
from orchestrator.execution_planner import ExecutionPlanner, ExecutionWave
from orchestrator.graph_runner import GraphRunner, GraphState, build_state_graph
from orchestrator.task_analyzer import Task, TaskAnalyzer, TaskBreakdown
from workflows.constants import GraphNodes, SpecialistSlugs
from workflows.schemas.swarm import SwarmConfig, SwarmMetrics, SwarmState


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
        self.capability_index = CapabilityIndex(staff_dir)
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

        # Handle backward compatibility with squad mode
        if use_squad:
            return self._run_squad_mode(user_brief, use_squad)

        # Build and execute swarm graph
        graph = self._build_swarm_graph()

        initial_state: SwarmState = {
            'user_brief': user_brief,
            'steps': [],
            'max_parallel': self.config.max_parallel,
            'enable_parallel': self.config.enable_parallel,
            'context_strategy': self.config.context_strategy,
            'verbose': self.verbose,
            'stream_output': self.stream_output,
        }

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
                        state['completed_task_ids'].append(completed_task.id)

                    # Stream task output if enabled
                    if state.get('stream_output', False):
                        self._stream_task_output(completed_task, result, duration)

                    # Enhanced completion message
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
        state['completed_task_ids'].append(task.id)

        # Stream task output if enabled
        if state.get('stream_output', False):
            self._stream_task_output(task, result, duration)

        # Enhanced completion message
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

        event = {
            "event": "task_completed",
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
                    # Truncate result if needed
                    result = dep_task.result
                    if len(result) > self.config.max_context_tokens:
                        result = result[:self.config.max_context_tokens] + "... [truncated]"

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

    def _execute_task_with_fallback(
        self,
        task: Task,
        prompt: str,
        state: SwarmState,
    ) -> str:
        """
        Execute task with multi-level fallback.

        Fallback chain:
        1. Primary specialist
        2. Alternative specialist (if available)
        3. Chief of Staff
        4. Error message
        """
        session_id = state.get('run_id')

        # Try primary specialist
        try:
            agent = self.get_agent(task.assigned_specialist, session_id=f"{session_id}_{task.id}")
            return agent.query(prompt)

        except Exception as e:
            error_msg = f"Failed with {task.assigned_specialist}: {e}"
            print(f"ERROR: Task {task.id} - {error_msg}", file=sys.stderr)

            # Try alternative specialist
            if task.candidate_specialists and len(task.candidate_specialists) > 1:
                fallback_slug = task.candidate_specialists[1][0]
                try:
                    agent = self.get_agent(fallback_slug, session_id=f"{session_id}_{task.id}_alt")
                    result = agent.query(prompt)
                    return f"[Fallback: {fallback_slug}]\n{result}"
                except Exception as alt_error:
                    print(f"ERROR: Alternative specialist {fallback_slug} also failed: {alt_error}", file=sys.stderr)

            # Try Chief of Staff fallback
            if task.assigned_specialist != SpecialistSlugs.CHIEF_OF_STAFF:
                try:
                    cos = self.get_agent(SpecialistSlugs.CHIEF_OF_STAFF, session_id=f"{session_id}_{task.id}_cos")
                    result = cos.query(f"Task failed. Please handle:\n{prompt}")
                    return f"[CoS Fallback]\n{result}"
                except Exception as cos_error:
                    print(f"ERROR: Chief of Staff fallback failed: {cos_error}", file=sys.stderr)

            # Final fallback: return error
            state['failed_task_ids'].append(task.id)
            return f"[ERROR] Task failed: {error_msg}"

    def _synthesis_node(self, state: SwarmState) -> SwarmState:
        """Node 5: Chief of Staff synthesizes final output from all task results."""
        start_time = time.time()

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

        # Query Chief of Staff
        agent = self.get_agent(SpecialistSlugs.CHIEF_OF_STAFF, session_id=state.get('run_id'))
        final_output = agent.query(prompt)

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
            failed_tasks=len(state.get('failed_task_ids', [])),
            fallback_count=0,  # TODO: track fallbacks
        )

    def _run_squad_mode(self, user_brief: str, squad_name: str) -> SwarmState:
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
        return self.run_swarm(enhanced_brief, use_squad=None)

    def _persist_log(self, state: SwarmState) -> None:
        """Write run metadata and steps to disk, handling dataclass serialization."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        run_id = state.get("run_id", "unknown")
        log_path = self.log_dir / f"{run_id}.json"

        # Helper to convert dataclasses to dicts
        from dataclasses import asdict, is_dataclass
        
        def to_serializable(obj):
            if is_dataclass(obj):
                return asdict(obj)
            return obj

        # Create serializable state
        serializable_state = {}
        for k, v in state.items():
            if k == "steps":
                continue
            
            # recursive conversion for specific keys
            if k in ["task_breakdown", "execution_plan"]:
                serializable_state[k] = to_serializable(v)
            elif k == "task_map":
                # Convert Dict[str, Task] -> Dict[str, dict]
                serializable_state[k] = {
                    tid: to_serializable(task) 
                    for tid, task in v.items()
                }
            else:
                serializable_state[k] = v

        log = {
            "run_id": run_id,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "steps": state.get("steps", []),
            "state": serializable_state,
        }
        
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, default=str)
