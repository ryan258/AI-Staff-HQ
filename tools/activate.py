#!/usr/bin/env python3
"""Activate AI Staff HQ specialists as executable agents."""

import sys
from pathlib import Path
from typing import Optional
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.engine.core import load_specialist, SpecialistAgent
from tools.engine.config import get_config


console = Console()


def query_mode(agent: SpecialistAgent, query: str) -> None:
    """Execute single query and exit."""
    info = agent.get_info()

    console.print(f"\n[bold]{info['specialist']}[/bold] [dim](using {info['model']})[/dim]\n")

    with console.status("[bold yellow]Processing query...", spinner="dots"):
        response = agent.query(query)

    console.print(Markdown(response))
    console.print()


def list_specialists(staff_dir: Path, department: Optional[str] = None) -> None:
    """List available specialists."""
    specialists_by_dept = {}
    total = 0

    # Scan each department
    for dept_dir in sorted(staff_dir.iterdir()):
        if not dept_dir.is_dir() or dept_dir.name.startswith('.'):
            continue

        if department and dept_dir.name != department:
            continue

        # Recursively find YAMLs
        dept_specialists = []
        for yaml_file in sorted(dept_dir.rglob("*.yaml")):
            specialist_name = yaml_file.stem
            dept_specialists.append(specialist_name)

        if dept_specialists:
            specialists_by_dept[dept_dir.name] = dept_specialists
            total += len(dept_specialists)

    console.print("\n[bold]Available Specialists[/bold]\n")
    for dept, names in sorted(specialists_by_dept.items()):
        console.print(f"[cyan]{dept}[/cyan] ({len(names)})")
        for name in sorted(names):
            console.print(f"  - {name}")

    console.print(f"\n[dim]Total: {len(specialists)} specialists[/dim]\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Activate AI Staff HQ specialists as executable agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  activate chief-of-staff -q "Create a project plan"
  activate copywriter --query "Write a tagline for luxury wellness"
  activate --list
  activate --list --department tech
        """
    )

    # Specialist identifier
    parser.add_argument(
        'specialist',
        nargs='?',
        help='Specialist name (slug) or path to YAML file'
    )

    # Query mode
    parser.add_argument(
        '-q', '--query',
        help='Execute single query and exit'
    )

    # Model selection
    parser.add_argument(
        '--model',
        help='Override model routing (e.g., anthropic/claude-3-opus)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        help='Temperature for responses (0.0-1.0)'
    )

    # Discovery
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available specialists'
    )

    parser.add_argument(
        '--department',
        choices=['strategy', 'producers', 'commerce', 'tech', 'health-lifestyle', 'knowledge'],
        help='Filter specialists by department'
    )

    # Debug
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Get config
    config = get_config()
    config.debug = args.debug

    # Determine project root
    project_root = Path(__file__).parent.parent
    staff_dir = project_root / "staff"

    # List mode
    if args.list:
        list_specialists(staff_dir, args.department)
        return

    # Require specialist for other modes
    if not args.specialist:
        parser.error("specialist name or path required (use --list to see available specialists)")

    # Require query for Phase 1 (interactive mode not yet implemented)
    if not args.query:
        console.print(
            "[yellow]Note:[/yellow] Interactive mode coming in Phase 2. "
            "For now, use -q/--query for one-shot queries.\n"
        )
        parser.error("--query/-q required")

    # Load specialist
    try:
        console.print(f"\n[dim]Loading specialist...[/dim]")
        agent = load_specialist(
            args.specialist,
            staff_dir,
            model_override=args.model,
            temperature=args.temperature,
        )
    except FileNotFoundError as e:
        console.print(f"\n[red]Error:[/red] {e}\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error loading specialist:[/red] {e}\n")
        if config.debug:
            raise
        sys.exit(1)

    # Execute query
    try:
        query_mode(agent, args.query)
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted[/dim]\n")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}\n")
        if config.debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
