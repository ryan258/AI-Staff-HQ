"""Task analysis and breakdown using Chief of Staff for swarm orchestration."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from orchestrator.graph_runner import GraphRunner


@dataclass
class Task:
    """A single task identified by the Chief of Staff."""

    id: str
    description: str
    required_capabilities: List[str]
    depends_on: List[str]  # Task IDs this task depends on
    priority: int  # 1=critical, 2=important, 3=nice-to-have
    assigned_specialist: Optional[str] = None
    result: Optional[str] = None
    candidate_specialists: List[tuple[str, float]] = None  # (slug, score) pairs


@dataclass
class TaskBreakdown:
    """Complete task breakdown from Chief of Staff analysis."""

    tasks: List[Task]
    original_brief: str
    raw_response: str
    parse_success: bool


class TaskAnalyzer:
    """Analyzes user briefs and breaks them down into structured tasks."""

    def __init__(self, runner: GraphRunner):
        """
        Initialize task analyzer.

        Args:
            runner: GraphRunner instance for loading Chief of Staff
        """
        self.runner = runner

    def analyze_brief(
        self,
        user_brief: str,
        *,
        session_id: Optional[str] = None,
        available_specialists: Optional[List[str]] = None,
    ) -> TaskBreakdown:
        """
        Analyze user brief and break it down into tasks.

        Args:
            user_brief: The user's request/brief
            session_id: Optional session ID for agent caching
            available_specialists: Optional list of available specialist slugs

        Returns:
            TaskBreakdown with parsed tasks
        """
        # Build the analysis prompt
        prompt = self._build_analysis_prompt(user_brief, available_specialists)

        # Query Chief of Staff
        from workflows.constants import SpecialistSlugs
        agent = self.runner.get_agent(SpecialistSlugs.CHIEF_OF_STAFF, session_id=session_id)
        response = agent.query(prompt)

        # Parse the JSON response
        tasks = self._parse_task_json(response)

        # Validate and create TaskBreakdown
        if not tasks:
            # Fallback: treat entire brief as single task
            tasks = [self._create_fallback_task(user_brief)]
            parse_success = False
        else:
            parse_success = True

        return TaskBreakdown(
            tasks=tasks,
            original_brief=user_brief,
            raw_response=response,
            parse_success=parse_success,
        )

    def _build_analysis_prompt(
        self,
        user_brief: str,
        available_specialists: Optional[List[str]] = None,
    ) -> str:
        """
        Build the prompt for Chief of Staff to analyze the brief.

        Args:
            user_brief: The user's request
            available_specialists: Optional list of available specialists

        Returns:
            Formatted prompt string
        """
        specialist_list = ""
        if available_specialists:
            specialist_list = f"\n\nAVAILABLE SPECIALISTS:\n{', '.join(available_specialists)}"

        prompt = f"""You are coordinating a swarm of AI specialists to complete a complex request.

USER BRIEF:
{user_brief}
{specialist_list}

Break this request into specific, atomic tasks. For each task specify:
1. **id**: Unique task identifier (e.g., "task_1", "task_2")
2. **description**: Clear, actionable task description (1-2 sentences)
3. **required_capabilities**: List of 1-3 required capabilities (e.g., ["copywriting", "SEO"])
4. **depends_on**: List of task IDs this task depends on (empty list [] if independent)
5. **priority**: 1=critical, 2=important, 3=nice-to-have

CRITICAL REQUIREMENTS:
- Keep tasks INDEPENDENT where possible (enables parallel execution)
- Only add dependencies when truly necessary (e.g., writing depends on research)
- Each task should be completable by a single specialist
- Use general capability names (e.g., "copywriting" not "write landing page copy")
- Minimum 1 task, maximum 10 tasks

Return ONLY a JSON array with no additional text:

[
  {{
    "id": "task_1",
    "description": "Research target audience demographics and pain points",
    "required_capabilities": ["market research", "data analysis"],
    "depends_on": [],
    "priority": 1
  }},
  {{
    "id": "task_2",
    "description": "Analyze competitor positioning and messaging",
    "required_capabilities": ["competitive analysis", "market research"],
    "depends_on": [],
    "priority": 1
  }},
  {{
    "id": "task_3",
    "description": "Create content outline based on research findings",
    "required_capabilities": ["content strategy", "copywriting"],
    "depends_on": ["task_1", "task_2"],
    "priority": 1
  }}
]

FEW-SHOT EXAMPLES:

Brief: "Write a blog post about AI tools"
Tasks:
[
  {{"id": "task_1", "description": "Research top AI tools in 2025", "required_capabilities": ["research", "technology analysis"], "depends_on": [], "priority": 1}},
  {{"id": "task_2", "description": "Write blog post content based on research", "required_capabilities": ["copywriting", "technical writing"], "depends_on": ["task_1"], "priority": 1}}
]

Brief: "Create a marketing campaign for a new product"
Tasks:
[
  {{"id": "task_1", "description": "Define target audience and positioning", "required_capabilities": ["market analysis", "brand strategy"], "depends_on": [], "priority": 1}},
  {{"id": "task_2", "description": "Develop campaign messaging and taglines", "required_capabilities": ["copywriting", "brand messaging"], "depends_on": ["task_1"], "priority": 1}},
  {{"id": "task_3", "description": "Design campaign assets and creative", "required_capabilities": ["graphic design", "creative direction"], "depends_on": ["task_2"], "priority": 2}}
]

Now analyze the user brief above and return the JSON task array.
"""
        return prompt

    def _parse_task_json(self, response: str) -> List[Task]:
        """
        Extract and parse JSON task array from Chief of Staff response.

        Uses the pattern from cos_orchestration.py (lines 42-52).

        Args:
            response: Raw response from Chief of Staff

        Returns:
            List of Task objects (empty if parsing fails)
        """
        # Extract JSON array from response
        try:
            # Find first [ and last ]
            start = response.find('[')
            end = response.rfind(']') + 1

            if start == -1 or end == 0:
                return []

            json_str = response[start:end]
            task_dicts = json.loads(json_str)

            if not isinstance(task_dicts, list):
                return []

            # Convert to Task objects
            tasks = []
            for i, task_dict in enumerate(task_dicts):
                if not isinstance(task_dict, dict):
                    continue

                # Extract and validate fields
                task_id = task_dict.get('id', f'task_{i+1}')
                description = task_dict.get('description', '')
                required_caps = task_dict.get('required_capabilities', [])
                depends_on = task_dict.get('depends_on', [])
                priority = task_dict.get('priority', 2)

                # Validate required fields
                if not description or not isinstance(required_caps, list):
                    continue

                # Ensure depends_on is a list
                if not isinstance(depends_on, list):
                    depends_on = []

                # Normalize capability names to lowercase
                required_caps = [c.lower().strip() for c in required_caps if isinstance(c, str)]

                # Validate priority
                if not isinstance(priority, int) or priority < 1 or priority > 3:
                    priority = 2

                tasks.append(Task(
                    id=task_id,
                    description=description,
                    required_capabilities=required_caps,
                    depends_on=depends_on,
                    priority=priority,
                ))

            return tasks

        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            # Log error to stderr but don't crash
            import sys
            print(f"Warning: Failed to parse task JSON: {e}", file=sys.stderr)
            return []

    def _create_fallback_task(self, user_brief: str) -> Task:
        """
        Create a fallback task when parsing fails.

        This treats the entire brief as a single task assigned to Chief of Staff.

        Args:
            user_brief: The original user brief

        Returns:
            Single Task object
        """
        return Task(
            id='task_1',
            description=user_brief,
            required_capabilities=['general coordination', 'strategic planning'],
            depends_on=[],
            priority=1,
        )

    def validate_task_breakdown(self, breakdown: TaskBreakdown) -> List[str]:
        """
        Validate task breakdown and return list of warnings/errors.

        Args:
            breakdown: TaskBreakdown to validate

        Returns:
            List of validation warning messages (empty if all valid)
        """
        warnings = []

        # Check task count
        if len(breakdown.tasks) == 0:
            warnings.append("No tasks created")
        elif len(breakdown.tasks) > 15:
            warnings.append(f"Large number of tasks ({len(breakdown.tasks)}). Consider simplifying.")

        # Check for circular dependencies
        task_ids = {task.id for task in breakdown.tasks}
        for task in breakdown.tasks:
            # Check if dependencies exist
            for dep_id in task.depends_on:
                if dep_id not in task_ids:
                    warnings.append(f"Task {task.id} depends on non-existent task {dep_id}")

            # Check for self-dependency
            if task.id in task.depends_on:
                warnings.append(f"Task {task.id} depends on itself")

        # Check for tasks with no capabilities
        for task in breakdown.tasks:
            if not task.required_capabilities:
                warnings.append(f"Task {task.id} has no required capabilities")

        return warnings
