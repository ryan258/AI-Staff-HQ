#!/usr/bin/env python3
"""
Workflows: Strategic Planning (Python SDK Example)

This script demonstrates how to use the AI-Staff-HQ Python SDK to 
orchestrate a multi-step workflow between different specialists.

Flow:
1. User Input (Topic)
2. Market Analyst (Research)
3. Creative Strategist (Ideation)
4. Chief of Staff (Synthesis)
"""

import sys
from pathlib import Path

# Add project root to path so we can import tools
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.engine.core import load_specialist
from workflows.constants import SpecialistSlugs
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def main():
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        console.print("[bold green]Strategic Planning Workflow[/bold green]")
        topic = console.input("Enter the initiative or topic to analyze: ")

    staff_dir = project_root / "staff"

    # 1. Initialize Agents
    with console.status("[bold]Loading specialists...[/bold]"):
        market_analyst = load_specialist(SpecialistSlugs.MARKET_ANALYST, staff_dir)
        creative_strategist = load_specialist(SpecialistSlugs.CREATIVE_STRATEGIST, staff_dir)
        chief_of_staff = load_specialist(SpecialistSlugs.CHIEF_OF_STAFF, staff_dir)

    # 2. Market Analysis
    console.print(f"\n[bold blue]Phase 1: Market Analysis ({market_analyst.schema.specialist})[/bold blue]")
    with console.status("Analyzing market trends and risks...", spinner="dots"):
        analysis = market_analyst.query(
            f"Please analyze the current market trends, opportunities, and risks for: '{topic}'. "
            "Keep it concise and focus on strategic factors."
        )
    console.print(Panel(Markdown(analysis), title="Market Analysis", border_style="blue"))

    # 3. Creative Strategy
    console.print(f"\n[bold magenta]Phase 2: Creative Strategy ({creative_strategist.schema.specialist})[/bold magenta]")
    with console.status("Developing strategic angles...", spinner="dots"):
        # We pass the analysis as context
        strategy = creative_strategist.query(
            f"Based on this market analysis:\n\n{analysis}\n\n"
            f"Propose 3 distinct strategic angles or campaign concepts for '{topic}'."
        )
    console.print(Panel(Markdown(strategy), title="Creative Strategy", border_style="magenta"))

    # 4. Synthesis
    console.print(f"\n[bold white]Phase 3: Executive Brief ({chief_of_staff.schema.specialist})[/bold white]")
    with console.status("Synthesizing executive brief...", spinner="dots"):
        brief = chief_of_staff.query(
            f"Context: We are exploring '{topic}'.\n\n"
            f"Market Intelligence:\n{analysis}\n\n"
            f"Strategic Options:\n{strategy}\n\n"
            "Task: Create a one-page Executive Strategy Brief. "
            "Recommend the best path forward and outline next steps."
        )
    console.print(Panel(Markdown(brief), title="Executive Brief", border_style="white"))

    console.print("\n[bold green]Workflow Complete![/bold green] 🚀")

if __name__ == "__main__":
    main()
