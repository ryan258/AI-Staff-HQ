#!/usr/bin/env python3
"""Capture real planning briefs into deterministic eval fixtures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Callable

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator.swarm_runner import SwarmRunner
from workflows.planning_swarm_eval import build_snapshot_case
from workflows.schemas.swarm import SwarmConfig


STAFF_DIR = PROJECT_ROOT / "staff"
DEFAULT_REAL_BRIEFS_PATH = PROJECT_ROOT / "evals" / "planning_swarm_real_briefs.yaml"


def load_brief_capture_file(path: Path) -> dict[str, Any]:
    """Load the real-brief capture file, creating a basic shell if needed."""
    if not path.exists():
        return {"version": 1, "cases": []}

    with open(path, encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}

    if "cases" not in payload or payload["cases"] is None:
        payload["cases"] = []
    if "version" not in payload:
        payload["version"] = 1

    return payload


def capture_case_with_runner(
    case: dict[str, Any],
    runner: SwarmRunner,
) -> dict[str, Any]:
    """Capture the live planner response for a single brief and build a snapshot case."""
    brief = str(case.get("brief", "")).strip()
    if not brief:
        raise ValueError(f"Case {case.get('id', '<unknown>')} is missing a brief")

    available_specialists = runner.capability_index.list_all_specialists()
    breakdown = runner.task_analyzer.analyze_brief(
        brief,
        session_id=None,
        available_specialists=available_specialists,
    )

    return build_snapshot_case(
        case_id=str(case.get("id", "")).strip() or "unnamed-case",
        brief=brief,
        planner_response=breakdown.raw_response,
        notes=case.get("notes"),
        max_parallel=int(case.get("max_parallel", 3) or 3),
    )


def update_capture_cases(
    payload: dict[str, Any],
    *,
    case_ids: set[str] | None,
    capture_fn: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    """Update selected cases in the capture payload using a capture function."""
    updated_cases: list[dict[str, Any]] = []

    for case in payload.get("cases", []):
        case_id = str(case.get("id", "")).strip()
        should_capture = not case_ids or case_id in case_ids
        if should_capture:
            updated_cases.append(capture_fn(case))
        else:
            updated_cases.append(case)

    return {
        "version": payload.get("version", 1),
        "cases": updated_cases,
    }


def write_capture_file(path: Path, payload: dict[str, Any]) -> None:
    """Write the capture file back to disk."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=False)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(
        description="Capture real planning briefs into deterministic eval fixtures.",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_REAL_BRIEFS_PATH,
        help="Path to the real-brief capture YAML file",
    )
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        help="Capture only the specified case id (repeatable)",
    )
    parser.add_argument("--model", help="Override the model used for capture")
    parser.add_argument("--temperature", type=float, help="Override model temperature")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the updated YAML instead of writing it back to disk",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    args = build_parser().parse_args()

    payload = load_brief_capture_file(args.cases)
    runner = SwarmRunner(STAFF_DIR, config=SwarmConfig(), model_override=args.model, temperature=args.temperature, auto_approve=True)
    updated = update_capture_cases(
        payload,
        case_ids=set(args.case_ids) if args.case_ids else None,
        capture_fn=lambda case: capture_case_with_runner(case, runner),
    )

    if args.dry_run:
        print(yaml.safe_dump(updated, sort_keys=False, allow_unicode=False))
        return

    write_capture_file(args.cases, updated)
    print(f"Captured {len(updated['cases'])} planning brief fixture(s) into {args.cases}")


if __name__ == "__main__":
    main()
