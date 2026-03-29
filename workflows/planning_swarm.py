#!/usr/bin/env python3
"""Flagship planning swarm entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator.swarm_runner import SwarmRunner
from workflows.schemas.swarm import SwarmConfig


STAFF_DIR = PROJECT_ROOT / "staff"


def run_planning_swarm(
    topic: str,
    *,
    auto_approve: bool = True,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    include_experimental: bool = False,
    max_parallel: int = 3,
    verbose: bool = False,
    stream: bool = False,
):
    """Run the quality-first planning swarm."""
    config = SwarmConfig(
        max_parallel=max_parallel,
        enable_parallel=True,
        roster_tiers=["active", "experimental"] if include_experimental else ["active"],
    )
    runner = SwarmRunner(
        STAFF_DIR,
        config=config,
        model_override=model,
        temperature=temperature,
        auto_approve=auto_approve,
        verbose=verbose,
        stream_output=stream,
    )
    return runner.run_swarm(topic)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for the planning swarm."""
    parser = argparse.ArgumentParser(
        description="Run the flagship AI-Staff-HQ planning swarm.",
    )
    parser.add_argument("topic", help="Brief, idea, or project to turn into a plan")
    parser.add_argument("--model", help="Override the model for all specialists")
    parser.add_argument("--temperature", type=float, help="Override model temperature")
    parser.add_argument(
        "--experimental",
        action="store_true",
        help="Include experimental specialists in matching",
    )
    parser.add_argument(
        "--max-parallel",
        type=int,
        default=3,
        help="Maximum tasks to execute in parallel",
    )
    parser.add_argument(
        "--no-auto-approve",
        action="store_true",
        help="Require interactive approval gates where configured",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed stderr progress")
    parser.add_argument("--stream", action="store_true", help="Stream task events as JSON on stderr")
    return parser


def main() -> None:
    """CLI entrypoint."""
    args = build_parser().parse_args()
    result = run_planning_swarm(
        args.topic,
        auto_approve=not args.no_auto_approve,
        model=args.model,
        temperature=args.temperature,
        include_experimental=args.experimental,
        max_parallel=args.max_parallel,
        verbose=args.verbose,
        stream=args.stream,
    )
    print(result.get("final_output", "[No output generated]"))


if __name__ == "__main__":
    main()
