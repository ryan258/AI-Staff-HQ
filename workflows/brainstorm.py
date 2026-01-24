#!/usr/bin/env python3
"""
Workflows: Brainstorm (Brain + Storm)

A multi-agent swarm that researches a topic, synthesizes an executive brief,
and (upon approval) stores the knowledge in the central Hive Mind.

Flow:
1. User Input (Topic)
2. Market Analyst (Research)
3. Creative Strategist (Ideation)
4. Chief of Staff (Synthesis)
5. Human Approval -> Ingest to Brain
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm

# Add project root to path for ai-staff-hq tools
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dotfiles root to path for Brain tools
# Assuming ai-staff-hq is in ~/dotfiles/ai-staff-hq
dotfiles_root = project_root.parent
sys.path.insert(0, str(dotfiles_root))

try:
    from tools.engine.core import load_specialist
    from workflows.constants import SpecialistSlugs
except ImportError as e:
    print(f"Error importing AI-Staff-HQ tools: {e}")
    sys.exit(1)

try:
    from brain.lib import memory
except ImportError:
    # Brain might not be configured or path is wrong
    memory = None

console = Console()

def main():
    console.rule("[bold purple]🧠 Brainstorm Swarm[/bold purple]")
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
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
            "recommend the best path forward and outline next steps."
        )
    
    console.print("\n")
    console.print(Panel(Markdown(brief), title="Final Executive Brief", border_style="green"))

    # 5. The Brain Integration
    console.rule("[bold yellow]Hive Mind Integration[/bold yellow]")
    
    if memory is None:
        console.print("[yellow]Warning: Hive Mind library not found. Cannot save.[/yellow]")
        return

    client = memory.get_client()
    if not client:
        console.print("[red]Error: Could not connect to Hive Mind service (is start_brain.sh running?).[/red]")
        return

    if Confirm.ask("[bold]Save this brief to The Brain?[/bold]"):
        with console.status("Ingesting into Hive Mind..."):
            
            # Metadata construction
            metadata = {
                "source": "swarm_brainstorm",
                "type": "executive_brief",
                "level": "strategic",
                "topics": topic,
                "project_context": "ai-staff-hq",
                "agents_involved": f"{market_analyst.get_info()['slug']},{creative_strategist.get_info()['slug']},{chief_of_staff.get_info()['slug']}"
            }
            
            # We save the brief as the main content, but we could also save the full context
            content = f"# Strategy Brief: {topic}\n\n{brief}"
            
            memory.add_memory(client, content, metadata=metadata)
            
        console.print("[bold green]Success! Memory stored in Hive Mind.[/bold green] 🧠")
    else:
        console.print("[dim]Skipped saving to Brain.[/dim]")

if __name__ == "__main__":
    main()
