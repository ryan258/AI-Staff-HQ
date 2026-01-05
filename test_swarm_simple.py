#!/usr/bin/env python3
"""Simple test of swarm orchestration - makes API calls!"""

import sys
from pathlib import Path

from orchestrator.swarm_runner import SwarmRunner
from workflows.schemas.swarm import SwarmConfig


def main():
    """Test swarm with a simple brief."""
    print("="*60)
    print("SWARM ORCHESTRATION TEST")
    print("="*60)
    print("\nWARNING: This will make API calls and cost tokens!\n")

    # Initialize
    staff_dir = Path("staff")
    config = SwarmConfig(
        max_parallel=2,
        enable_parallel=True,
    )

    runner = SwarmRunner(
        staff_dir,
        config=config,
        model_override="nvidia/nemotron-3-nano-30b-a3b:free",  # Cheap model for testing
        auto_approve=True,
    )

    # Simple brief
    brief = "Write a short tagline (one sentence) for a coffee shop called 'Morning Brew'"

    print(f"Brief: {brief}\n")
    print("Starting swarm execution...\n")

    try:
        # Run swarm
        result = runner.run_swarm(brief)

        # Display results
        print("\n" + "="*60)
        print("FINAL OUTPUT")
        print("="*60)
        print(result.get('final_output', '[No output]'))

        # Display metrics
        print("\n" + "="*60)
        print("METRICS")
        print("="*60)

        metrics = result.get('metrics', {})

        # Debug: print raw metrics
        if not metrics:
            print("\n⚠️  No metrics found in result")
        else:
            print(f"\n📊 Raw metrics keys: {metrics.keys()}")

        exec_stats = metrics.get('execution_stats', {})
        print(f"\nExecution Stats:")
        print(f"  Total Tasks: {exec_stats.get('total_tasks', 0)}")
        print(f"  Parallel Tasks: {exec_stats.get('parallel_tasks', 0)}")
        print(f"  Duration: {exec_stats.get('total_duration_seconds', 0):.2f}s")

        specialist_usage = metrics.get('specialist_usage', {})
        print(f"\nSpecialist Usage:")
        specialists = specialist_usage.get('specialists_used', {})
        for slug, count in specialists.items():
            print(f"  {slug}: {count} task(s)")

        matching = metrics.get('matching_quality', {})
        print(f"\nMatching Quality:")
        print(f"  Avg Match Score: {matching.get('avg_match_score', 0):.2f}")
        unmatched = matching.get('unmatched_capabilities', [])
        if unmatched:
            print(f"  Unmatched: {unmatched}")

        print("\n✓ Test completed successfully!")
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
