"""Pydantic schemas for swarm orchestration state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict

from orchestrator.execution_planner import ExecutionPlan
from orchestrator.task_analyzer import TaskBreakdown


class SwarmState(TypedDict, total=False):
    """State dictionary passed between swarm execution nodes."""

    # Core request
    user_brief: str
    run_id: str

    # Task breakdown
    task_breakdown: TaskBreakdown  # From TaskAnalyzer
    execution_plan: ExecutionPlan  # From ExecutionPlanner

    # Task execution tracking
    task_map: Dict[str, Any]  # task_id → Task object with results
    completed_task_ids: List[str]
    failed_task_ids: List[str]

    # Wave tracking
    current_wave_id: int
    completed_waves: List[int]

    # Final output
    final_output: str

    # Metadata and logging
    steps: List[Dict[str, Any]]  # Execution log
    metrics: Dict[str, Any]  # Performance metrics
    approvals: List[str]  # Approval gates passed

    # Configuration
    max_parallel: int
    enable_parallel: bool
    context_strategy: str  # 'dependencies_only', 'full', 'summary'
    verbose: bool  # Show detailed progress output
    stream_output: bool  # Stream task outputs as JSON events


@dataclass
class SwarmMetrics:
    """Performance and cost metrics for swarm execution."""

    # Execution stats
    total_tasks: int
    parallel_tasks: int
    sequential_tasks: int
    total_duration_seconds: float
    avg_task_duration_seconds: float

    # Specialist usage
    specialists_used: Dict[str, int]  # slug → count
    unique_specialists: int

    # Matching quality
    avg_match_score: float
    unmatched_capabilities: List[str]

    # Performance
    speedup_factor: float  # Actual duration vs theoretical sequential
    parallelization_efficiency: float  # Actual speedup / theoretical speedup

    # Costs
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    # Errors
    failed_tasks: int = 0
    fallback_count: int = 0
    errors: List[str] = None

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'execution_stats': {
                'total_tasks': self.total_tasks,
                'parallel_tasks': self.parallel_tasks,
                'sequential_tasks': self.sequential_tasks,
                'total_duration_seconds': self.total_duration_seconds,
                'avg_task_duration_seconds': self.avg_task_duration_seconds,
            },
            'specialist_usage': {
                'specialists_used': self.specialists_used,
                'unique_specialists': self.unique_specialists,
            },
            'matching_quality': {
                'avg_match_score': self.avg_match_score,
                'unmatched_capabilities': self.unmatched_capabilities,
            },
            'performance': {
                'speedup_factor': self.speedup_factor,
                'parallelization_efficiency': self.parallelization_efficiency,
            },
            'costs': {
                'total_prompt_tokens': self.total_prompt_tokens,
                'total_completion_tokens': self.total_completion_tokens,
                'total_tokens': self.total_tokens,
                'estimated_cost_usd': self.estimated_cost_usd,
            },
            'errors': {
                'failed_tasks': self.failed_tasks,
                'fallback_count': self.fallback_count,
                'error_messages': self.errors,
            },
        }


@dataclass
class SwarmConfig:
    """Configuration for swarm execution."""

    # Parallel execution
    max_parallel: int = 5
    enable_parallel: bool = True

    # Context management
    context_strategy: str = 'dependencies_only'  # 'dependencies_only', 'full', 'summary'
    max_context_tokens: int = 500  # Truncate individual results

    # Cost control
    max_budget_tokens: Optional[int] = None  # Halt if exceeded
    budget_warning_threshold: float = 0.8  # Warn at 80% budget

    # Error handling
    max_retries: int = 2
    enable_fallback: bool = True

    # Quality control
    min_capability_match_score: float = 0.3
    require_approval: bool = False

    def validate(self) -> List[str]:
        """
        Validate configuration and return list of warnings.

        Returns:
            List of validation warning messages (empty if valid)
        """
        warnings = []

        if self.max_parallel < 1:
            warnings.append("max_parallel must be >= 1")

        if self.max_parallel > 20:
            warnings.append("max_parallel > 20 may cause rate limiting")

        if self.context_strategy not in {'dependencies_only', 'full', 'summary'}:
            warnings.append(f"Invalid context_strategy: {self.context_strategy}")

        if self.max_context_tokens < 100:
            warnings.append("max_context_tokens too low (< 100)")

        if self.min_capability_match_score < 0.0 or self.min_capability_match_score > 1.0:
            warnings.append("min_capability_match_score must be 0.0-1.0")

        return warnings
