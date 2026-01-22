#!/usr/bin/env python3
"""Activate AI Staff HQ specialists as executable agents."""

import sys
from pathlib import Path
from typing import Optional
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.engine.core import load_specialist, SpecialistAgent
from tools.engine.config import get_config
from tools.engine.state import ConversationState


console = Console()


def interactive_loop(agent: SpecialistAgent) -> None:
    """Run interactive chat session."""
    info = agent.get_info()
    session_id = info['session_id']
    
    console.print(f"\n[bold green]Activated: {info['specialist']}[/bold green]")
    console.print(f"[dim]Role: {info['role']}[/dim]")
    console.print(f"[dim]Model: {info['model']}[/dim]")
    console.print(f"[dim]Session: {session_id}[/dim]")
    console.print("\n[dim]Type 'exit' or /bye to quit. /clear to restart context.[/dim]\n")

    # Prompt toolkit session
    session = PromptSession()
    
    while True:
        try:
            user_input = session.prompt(HTML(f"<b>{info['slug']}</b>> "))
            user_input = user_input.strip()

            if not user_input:
                continue

            # Commands
            if user_input.lower() in ('exit', 'quit', '/bye', '/exit'):
                console.print("[yellow]Saving and exiting...[/yellow]")
                break
                
            if user_input.lower() in ('/clear', 'clear'):
                console.print("[yellow]Clearing conversation history...[/yellow]")
                new_session_id = agent.state.clear()
                console.print(f"[green]✓ New session started: {new_session_id}[/green]")
                continue

            # Query
            with console.status("[bold yellow]Thinking...", spinner="dots"):
                try:
                    response = agent.query(user_input)
                    
                    # Streaming simulated by printing the whole response for now
                    # (LangChain streaming is supported but requires callback handlers)
                    console.print(Panel(Markdown(response), title=f"{info['specialist']}", border_style="green"))
                    
                except KeyboardInterrupt:
                    console.print("\n[yellow]Generation cancelled by user.[/yellow]")
                    continue

        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


def query_mode(agent: SpecialistAgent, query: str) -> None:
    """Execute single query and exit."""
    info = agent.get_info()

    console.print(f"\n[bold]{info['specialist']}[/bold] [dim](using {info['model']})[/dim]")
    console.print(f"[dim]Session: {info['session_id']}[/dim]\n")

    with console.status("[bold green]Processing query...", spinner="dots"):
        try:
            response = agent.query(query)
            console.print(Panel(Markdown(response), title=f"{agent.schema.specialist}", border_style="green"))
        except KeyboardInterrupt:
            console.print("\n[yellow]Generation cancelled by user.[/yellow]")
            sys.exit(130)


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

    console.print(f"\n[dim]Total: {total} specialists[/dim]\n")


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
        help='Override model routing (e.g., xiaomi/mimo-v2-flash:free)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        help='Temperature for responses (0.0-1.0)'
    )

    parser.add_argument(
        '--resume',
        nargs='?',
        const='last',
        help='Resume session ID or "last" (default)'
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

    # Resolve resume session
    session_id = args.resume
    if session_id == 'last':
        # Find last session for this specialist
        # We need the slug first to find the directory
        # This is chicken-egg: we need core logic to resolve slug from identifier
        # For now, let's assume identifier IS the slug or close enough, 
        # OR we load the agent first then check history? 
        # Loading agent with session_id=None starts new session.
        # Let's try to resolve latest session for the specialist identifier
        # Simple heuristic: assume identifier is slug
        # But if it's a path (e.g. staff/strategy/chief-of-staff.yaml), we need the stem
        if '/' in args.specialist or args.specialist.endswith('.yaml'):
            slug = Path(args.specialist).stem
        else:
            slug = args.specialist.lower().replace(' ', '-')
            
        sessions = ConversationState.list_sessions(slug)
        if sessions:
            session_id = sessions[0]['id']
            console.print(f"[dim]Resuming last session: {session_id}[/dim]")
        else:
            console.print("[yellow]No previous session found. Starting new.[/yellow]")
            session_id = None

    # Load specialist
    try:
        console.print(f"\n[dim]Loading specialist...[/dim]")
        agent = load_specialist(
            args.specialist,
            staff_dir,
            model_override=args.model,
            temperature=args.temperature,
            session_id=session_id
        )
    except FileNotFoundError as e:
        console.print(f"\n[red]Error:[/red] {e}\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error loading specialist:[/red] {e}\n")
        if config.debug:
            raise
        sys.exit(1)

    # Execute query or enter interactive mode
    try:
        if args.query:
            query_mode(agent, args.query)
        else:
            interactive_loop(agent)
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
