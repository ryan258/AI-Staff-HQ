"""Execution planning with dependency resolution and wave creation for swarm orchestration."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Set

from orchestrator.task_analyzer import Task


@dataclass
class ExecutionWave:
    """A group of tasks to be executed together."""

    wave_id: int
    tasks: List[Task]
    parallel: bool  # True if tasks can run in parallel, False if sequential

    def __str__(self) -> str:
        """String representation of the wave."""
        mode = "PARALLEL" if self.parallel else "SEQUENTIAL"
        task_ids = [t.id for t in self.tasks]
        return f"Wave {self.wave_id} ({mode}): {task_ids}"


@dataclass
class ExecutionPlan:
    """Complete execution plan with waves."""

    waves: List[ExecutionWave]
    total_tasks: int
    parallel_tasks: int
    sequential_tasks: int

    def __str__(self) -> str:
        """String representation of the plan."""
        lines = [
            f"Execution Plan ({self.total_tasks} tasks):",
            f"  Parallel: {self.parallel_tasks}",
            f"  Sequential: {self.sequential_tasks}",
            f"  Waves: {len(self.waves)}",
            "",
        ]
        for wave in self.waves:
            lines.append(f"  {wave}")
        return "\n".join(lines)


class ExecutionPlanner:
    """Plans execution of tasks based on dependencies using topological sort."""

    def create_execution_plan(
        self,
        tasks: List[Task],
        *,
        max_parallel: int = 5,
    ) -> ExecutionPlan:
        """
        Create an execution plan from a list of tasks.

        Args:
            tasks: List of Task objects with dependencies
            max_parallel: Maximum number of tasks to execute in parallel per wave

        Returns:
            ExecutionPlan with waves

        Raises:
            ValueError: If circular dependencies are detected
        """
        if not tasks:
            return ExecutionPlan(waves=[], total_tasks=0, parallel_tasks=0, sequential_tasks=0)

        # Build dependency graph
        graph, in_degree = self._build_dependency_graph(tasks)

        # Detect circular dependencies
        if self._has_circular_dependencies(graph, in_degree, tasks):
            raise ValueError(
                "Circular dependencies detected in task breakdown. "
                "Please revise task dependencies."
            )

        # Perform topological sort and group into waves
        waves = self._create_waves(tasks, graph, in_degree, max_parallel)

        # Calculate statistics
        total_tasks = len(tasks)
        parallel_tasks = sum(len(wave.tasks) for wave in waves if wave.parallel)
        sequential_tasks = total_tasks - parallel_tasks

        return ExecutionPlan(
            waves=waves,
            total_tasks=total_tasks,
            parallel_tasks=parallel_tasks,
            sequential_tasks=sequential_tasks,
        )

    def _build_dependency_graph(
        self,
        tasks: List[Task],
    ) -> tuple[Dict[str, List[str]], Dict[str, int]]:
        """
        Build a dependency graph from tasks.

        Args:
            tasks: List of Task objects

        Returns:
            Tuple of (adjacency_list, in_degree_count)
            - adjacency_list: task_id → [dependent_task_ids]
            - in_degree: task_id → number of dependencies
        """
        # Create task ID to Task mapping
        task_map = {task.id: task for task in tasks}

        # Initialize graph and in-degree
        graph: Dict[str, List[str]] = defaultdict(list)
        in_degree: Dict[str, int] = {task.id: 0 for task in tasks}

        # Build edges
        for task in tasks:
            for dep_id in task.depends_on:
                if dep_id in task_map:
                    # Edge from dependency to dependent
                    graph[dep_id].append(task.id)
                    in_degree[task.id] += 1

        return dict(graph), in_degree

    def _has_circular_dependencies(
        self,
        graph: Dict[str, List[str]],
        in_degree: Dict[str, int],
        tasks: List[Task],
    ) -> bool:
        """
        Check for circular dependencies using Kahn's algorithm.

        Args:
            graph: Adjacency list
            in_degree: In-degree count for each task
            tasks: List of tasks

        Returns:
            True if circular dependencies exist, False otherwise
        """
        # Copy in_degree to avoid modifying original
        in_degree_copy = in_degree.copy()

        # Find all nodes with no incoming edges
        queue = deque([task.id for task in tasks if in_degree_copy[task.id] == 0])

        processed_count = 0

        while queue:
            current = queue.popleft()
            processed_count += 1

            # Remove edges from current node
            for neighbor in graph.get(current, []):
                in_degree_copy[neighbor] -= 1
                if in_degree_copy[neighbor] == 0:
                    queue.append(neighbor)

        # If we processed all tasks, no cycle exists
        return processed_count != len(tasks)

    def _create_waves(
        self,
        tasks: List[Task],
        graph: Dict[str, List[str]],
        in_degree: Dict[str, int],
        max_parallel: int,
    ) -> List[ExecutionWave]:
        """
        Create execution waves using topological sort.

        Args:
            tasks: List of tasks
            graph: Dependency graph
            in_degree: In-degree count
            max_parallel: Maximum parallel tasks per wave

        Returns:
            List of ExecutionWave objects
        """
        # Create task ID to Task mapping
        task_map = {task.id: task for task in tasks}

        # Copy in_degree to avoid modifying original
        in_degree_work = in_degree.copy()

        waves: List[ExecutionWave] = []
        wave_id = 1

        # Process tasks in waves
        while True:
            # Find all tasks with no remaining dependencies (in_degree == 0)
            ready_tasks = [
                task_map[task_id]
                for task_id, degree in in_degree_work.items()
                if degree == 0
            ]

            if not ready_tasks:
                break

            # Remove processed tasks from in_degree
            for task in ready_tasks:
                del in_degree_work[task.id]

            # Split ready tasks into batches if exceeds max_parallel
            if len(ready_tasks) > max_parallel:
                # Create multiple waves from ready tasks
                for i in range(0, len(ready_tasks), max_parallel):
                    batch = ready_tasks[i:i + max_parallel]
                    waves.append(ExecutionWave(
                        wave_id=wave_id,
                        tasks=batch,
                        parallel=len(batch) > 1,
                    ))
                    wave_id += 1
            else:
                # Single wave for all ready tasks
                waves.append(ExecutionWave(
                    wave_id=wave_id,
                    tasks=ready_tasks,
                    parallel=len(ready_tasks) > 1,
                ))
                wave_id += 1

            # Update in_degree for tasks that depend on completed tasks
            for task in ready_tasks:
                for dependent_id in graph.get(task.id, []):
                    if dependent_id in in_degree_work:
                        in_degree_work[dependent_id] -= 1

        return waves

    def visualize_plan(self, plan: ExecutionPlan) -> str:
        """
        Create a text-based visualization of the execution plan.

        Args:
            plan: ExecutionPlan to visualize

        Returns:
            Multi-line string visualization
        """
        lines = [
            "=" * 60,
            "EXECUTION PLAN",
            "=" * 60,
            f"Total Tasks: {plan.total_tasks}",
            f"Parallel Tasks: {plan.parallel_tasks}",
            f"Sequential Tasks: {plan.sequential_tasks}",
            f"Total Waves: {len(plan.waves)}",
            "",
        ]

        for wave in plan.waves:
            mode = "║  PARALLEL  ║" if wave.parallel else "║ SEQUENTIAL ║"
            lines.append("┌" + "─" * 58 + "┐")
            lines.append(f"│ Wave {wave.wave_id:2d} {mode:^40s} │")
            lines.append("├" + "─" * 58 + "┤")

            for task in wave.tasks:
                # Truncate description if too long
                desc = task.description
                if len(desc) > 50:
                    desc = desc[:47] + "..."

                lines.append(f"│ • {task.id:8s} {desc:47s} │")

                # Show capabilities
                caps = ", ".join(task.required_capabilities[:3])
                if len(caps) > 50:
                    caps = caps[:47] + "..."
                lines.append(f"│   Needs: {caps:51s} │")

                # Show dependencies
                if task.depends_on:
                    deps = ", ".join(task.depends_on)
                    if len(deps) > 50:
                        deps = deps[:47] + "..."
                    lines.append(f"│   Depends on: {deps:46s} │")

                lines.append("│" + " " * 58 + "│")

            lines.append("└" + "─" * 58 + "┘")
            lines.append("")

        return "\n".join(lines)

    def get_critical_path(self, plan: ExecutionPlan) -> List[str]:
        """
        Identify the critical path (longest dependency chain) in the plan.

        Args:
            plan: ExecutionPlan to analyze

        Returns:
            List of task IDs in the critical path
        """
        if not plan.waves:
            return []

        # Find the wave with the most dependencies upstream
        max_depth = len(plan.waves)

        # Get last wave's tasks as potential end points
        last_wave = plan.waves[-1]

        # For simplicity, return the longest chain by counting waves
        # A more sophisticated version would track actual dependency chains
        critical_path = []

        for wave in plan.waves:
            if wave.tasks:
                # Add first task from each wave as representative
                critical_path.append(wave.tasks[0].id)

        return critical_path
