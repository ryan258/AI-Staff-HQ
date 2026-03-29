#!/usr/bin/env python3
"""Deterministic evaluation harness for the flagship planning swarm."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator.capability_index import CapabilityIndex
from orchestrator.execution_planner import ExecutionPlanner
from orchestrator.task_analyzer import Task, TaskAnalyzer
from workflows.constants import SpecialistSlugs


STAFF_DIR = PROJECT_ROOT / "staff"
DEFAULT_CASES_PATH = PROJECT_ROOT / "evals" / "planning_swarm_cases.yaml"


class EvalExpectations(BaseModel):
    """Expected properties for a deterministic planning eval case."""

    parse_success: bool
    task_count: int
    warning_count: int
    wave_count: int
    parallel_waves: int
    chief_of_staff_tasks: int = 0
    top_specialists: dict[str, list[str]] = Field(default_factory=dict)


class PlanningEvalCase(BaseModel):
    """Single planning swarm eval case."""

    id: str
    brief: str
    planner_response: str
    notes: str | None = None
    expect: EvalExpectations
    max_parallel: int = 3


class PlanningEvalSuite(BaseModel):
    """Collection of planning swarm eval cases."""

    version: int = 1
    cases: list[PlanningEvalCase]


class StaticResponseAgent:
    """Simple agent stub that always returns the configured response."""

    def __init__(self, response: str):
        self.response = response

    def query(self, _prompt: str) -> str:
        return self.response


class StaticRunner:
    """Minimal runner stub for TaskAnalyzer."""

    def __init__(self, response: str):
        self.response = response

    def get_agent(self, _slug: str, session_id: str | None = None) -> StaticResponseAgent:
        return StaticResponseAgent(self.response)


def load_eval_suite(cases_path: Path = DEFAULT_CASES_PATH) -> PlanningEvalSuite:
    """Load the evaluation suite from YAML."""
    with open(cases_path, encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}
    return PlanningEvalSuite(**payload)


def _assign_specialists(tasks: list[Task], staff_dir: Path) -> list[Task]:
    """Run capability matching against the active roster."""
    index = CapabilityIndex(staff_dir)

    for task in tasks:
        matches = index.match_specialists(task.required_capabilities, min_score=0.3, max_results=3)
        if matches:
            task.assigned_specialist = matches[0][0]
            task.candidate_specialists = matches
        else:
            task.assigned_specialist = SpecialistSlugs.CHIEF_OF_STAFF
            task.candidate_specialists = [(SpecialistSlugs.CHIEF_OF_STAFF, 0.0)]

    return tasks


def analyze_case_observations(case: PlanningEvalCase, staff_dir: Path = STAFF_DIR) -> dict[str, Any]:
    """Analyze a case and return observed planner behavior."""
    analyzer = TaskAnalyzer(StaticRunner(case.planner_response))
    available_specialists = CapabilityIndex(staff_dir).list_all_specialists()
    breakdown = analyzer.analyze_brief(case.brief, available_specialists=available_specialists)
    warnings = analyzer.validate_task_breakdown(breakdown)
    tasks = _assign_specialists(breakdown.tasks, staff_dir)
    execution_plan = ExecutionPlanner().create_execution_plan(tasks, max_parallel=case.max_parallel)

    parallel_waves = sum(1 for wave in execution_plan.waves if wave.parallel)
    chief_of_staff_tasks = sum(1 for task in tasks if task.assigned_specialist == SpecialistSlugs.CHIEF_OF_STAFF)
    assigned_specialists = {task.id: task.assigned_specialist for task in tasks}

    return {
        "parse_success": breakdown.parse_success,
        "warning_count": len(warnings),
        "task_count": len(tasks),
        "wave_count": len(execution_plan.waves),
        "parallel_waves": parallel_waves,
        "chief_of_staff_tasks": chief_of_staff_tasks,
        "assigned_specialists": assigned_specialists,
        "warnings": warnings,
        "waves": [
            {
                "wave_id": wave.wave_id,
                "parallel": wave.parallel,
                "tasks": [task.id for task in wave.tasks],
            }
            for wave in execution_plan.waves
        ],
    }


def build_snapshot_case(
    *,
    case_id: str,
    brief: str,
    planner_response: str,
    staff_dir: Path = STAFF_DIR,
    max_parallel: int = 3,
    notes: str | None = None,
) -> dict[str, Any]:
    """Build a normalized eval case from an observed planner response."""
    case = PlanningEvalCase(
        id=case_id,
        brief=brief,
        planner_response=planner_response,
        notes=notes,
        max_parallel=max_parallel,
        expect=EvalExpectations(
            parse_success=True,
            task_count=0,
            warning_count=0,
            wave_count=0,
            parallel_waves=0,
            chief_of_staff_tasks=0,
            top_specialists={},
        ),
    )
    observed = analyze_case_observations(case, staff_dir)
    top_specialists = {
        task_id: [slug]
        for task_id, slug in observed["assigned_specialists"].items()
        if slug
    }

    snapshot = {
        "id": case_id,
        "brief": brief,
        "planner_response": planner_response,
        "expect": {
            "parse_success": observed["parse_success"],
            "task_count": observed["task_count"],
            "warning_count": observed["warning_count"],
            "wave_count": observed["wave_count"],
            "parallel_waves": observed["parallel_waves"],
            "chief_of_staff_tasks": observed["chief_of_staff_tasks"],
            "top_specialists": top_specialists,
        },
        "max_parallel": max_parallel,
    }
    if notes:
        snapshot["notes"] = notes
    return snapshot


def evaluate_case(case: PlanningEvalCase, staff_dir: Path = STAFF_DIR) -> dict[str, Any]:
    """Evaluate a single planning swarm case."""
    observed = analyze_case_observations(case, staff_dir)

    checks: list[dict[str, Any]] = []

    def add_check(name: str, actual: Any, expected: Any, passed: bool) -> None:
        checks.append(
            {
                "name": name,
                "actual": actual,
                "expected": expected,
                "passed": passed,
            }
        )

    add_check("parse_success", observed["parse_success"], case.expect.parse_success, observed["parse_success"] == case.expect.parse_success)
    add_check("task_count", observed["task_count"], case.expect.task_count, observed["task_count"] == case.expect.task_count)
    add_check("warning_count", observed["warning_count"], case.expect.warning_count, observed["warning_count"] == case.expect.warning_count)
    add_check("wave_count", observed["wave_count"], case.expect.wave_count, observed["wave_count"] == case.expect.wave_count)
    add_check("parallel_waves", observed["parallel_waves"], case.expect.parallel_waves, observed["parallel_waves"] == case.expect.parallel_waves)
    add_check(
        "chief_of_staff_tasks",
        observed["chief_of_staff_tasks"],
        case.expect.chief_of_staff_tasks,
        observed["chief_of_staff_tasks"] == case.expect.chief_of_staff_tasks,
    )

    for task_id, expected_slugs in case.expect.top_specialists.items():
        actual_slug = observed["assigned_specialists"].get(task_id)
        add_check(
            f"top_specialist:{task_id}",
            actual_slug,
            expected_slugs,
            actual_slug in expected_slugs,
        )

    passed_checks = sum(1 for check in checks if check["passed"])

    return {
        "id": case.id,
        "brief": case.brief,
        "passed": passed_checks == len(checks),
        "passed_checks": passed_checks,
        "total_checks": len(checks),
        "checks": checks,
        "warnings": observed["warnings"],
        "assigned_specialists": observed["assigned_specialists"],
        "waves": observed["waves"],
    }


def evaluate_suite(cases_path: Path = DEFAULT_CASES_PATH, staff_dir: Path = STAFF_DIR) -> dict[str, Any]:
    """Evaluate the entire planning swarm suite."""
    suite = load_eval_suite(cases_path)
    results = [evaluate_case(case, staff_dir) for case in suite.cases]
    total_checks = sum(result["total_checks"] for result in results)
    passed_checks = sum(result["passed_checks"] for result in results)
    passed_cases = sum(1 for result in results if result["passed"])

    return {
        "cases_path": str(cases_path),
        "total_cases": len(results),
        "passed_cases": passed_cases,
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "results": results,
    }


def _print_summary(summary: dict[str, Any]) -> None:
    """Print a compact human-readable summary."""
    print(
        f"Planning swarm evals: {summary['passed_cases']}/{summary['total_cases']} cases passed "
        f"({summary['passed_checks']}/{summary['total_checks']} checks)"
    )
    for result in summary["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} {result['id']} ({result['passed_checks']}/{result['total_checks']} checks)")
        if not result["passed"]:
            for check in result["checks"]:
                if check["passed"]:
                    continue
                print(
                    f"  - {check['name']}: expected {check['expected']!r}, got {check['actual']!r}"
                )


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(
        description="Run deterministic evals for the flagship planning swarm.",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to the planning swarm eval case file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full result payload as JSON",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    args = build_parser().parse_args()
    summary = evaluate_suite(args.cases)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        _print_summary(summary)

    if summary["passed_cases"] != summary["total_cases"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
