#!/usr/bin/env python3
"""Executable LangGraph workflow: Strategy -> Tech -> Exec Brief."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from langgraph.graph import END

from orchestrator.graph_runner import GraphRunner, build_state_graph, GraphState
from workflows.constants import SpecialistSlugs


console = Console()
PROJECT_ROOT = Path(__file__).parents[2]
STAFF_DIR = PROJECT_ROOT / "staff"


def build_graph(runner: GraphRunner):
    """Assemble the Strategy -> Tech -> Executive Brief workflow graph."""
    graph = build_state_graph()

    analyze_market = runner.make_agent_node(
        specialist_slug=SpecialistSlugs.MARKET_ANALYST,
        state_key="analysis",
        step_name="market_analysis",
        prompt_builder=lambda state: (
            "Analyze market trends, opportunities, risks, and audience for: "
            f"'{state.get('topic')}'. Keep it concise and executive-friendly."
        ),
    )

    technical_plan = runner.make_agent_node(
        specialist_slug=SpecialistSlugs.SOFTWARE_ARCHITECT,
        state_key="technical_plan",
        step_name="technical_plan",
        prompt_builder=lambda state: (
            "Using the market analysis below, outline a technical approach and system design.\n\n"
            f"Topic: {state.get('topic')}\n\n"
            f"Market Analysis:\n{state.get('analysis', 'N/A')}\n\n"
            "Deliver a short architecture overview, key components, and risks."
        ),
    )

    executive_brief = runner.make_agent_node(
        specialist_slug=SpecialistSlugs.CHIEF_OF_STAFF,
        state_key="executive_brief",
        step_name="executive_brief",
        prompt_builder=lambda state: (
            "Create an executive brief that synthesizes the market analysis and technical plan. "
            "Highlight the recommendation, rationale, risks, and next steps.\n\n"
            f"Topic: {state.get('topic')}\n\n"
            f"Market Analysis:\n{state.get('analysis', 'N/A')}\n\n"
            f"Technical Plan:\n{state.get('technical_plan', 'N/A')}"
        ),
    )

    approval = runner.make_approval_node("approval: proceed to tech plan")

    graph.add_node("market_analysis", analyze_market)
    graph.add_node("approval_gate", approval)
    graph.add_node("technical_plan", technical_plan)
    graph.add_node("executive_brief", executive_brief)

    graph.add_edge("market_analysis", "approval_gate")
    graph.add_edge("approval_gate", "technical_plan")
    graph.add_edge("technical_plan", "executive_brief")
    graph.add_edge("executive_brief", END)

    graph.set_entry_point("market_analysis")
    return graph.compile()


def run_strategy_tech_handoff(
    topic: str,
    *,
    auto_approve: bool = True,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    log_dir: Optional[Path] = None,
) -> GraphState:
    """Run the Strategy -> Tech -> Executive Brief workflow."""
    runner = GraphRunner(
        STAFF_DIR,
        model_override=model,
        temperature=temperature,
        auto_approve=auto_approve,
        log_dir=log_dir,
    )
    graph = build_graph(runner)
    initial_state: GraphState = {
        "topic": topic,
        "steps": [],
    }
    return runner.run_graph(graph, initial_state)


def main():
    parser = argparse.ArgumentParser(
        description="Run the Strategy -> Tech -> Executive Brief workflow.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("topic", help="Topic or project to analyze.")
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve handoffs without prompting.",
    )
    parser.add_argument(
        "--model",
        help="Override model routing for this run (e.g., anthropic/claude-3-5-sonnet).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="Temperature for all agent calls.",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        help="Directory for graph run logs (default: logs/graphs).",
    )

    args = parser.parse_args()

    console.print("[bold]Strategy → Tech → Executive Brief[/bold]")
    console.print(f"[dim]Topic:[/dim] {args.topic}")

    try:
        result = run_strategy_tech_handoff(
            args.topic,
            auto_approve=args.auto_approve,
            model=args.model,
            temperature=args.temperature,
            log_dir=args.log_dir,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        return
    except Exception as e:
        console.print(f"\n[red]Workflow failed:[/red] {e}")
        return

    console.print("\n[green]Workflow complete.[/green]\n")
    if "analysis" in result:
        console.print(Panel(Markdown(result["analysis"]), title="Market Analysis", border_style="cyan"))
    if "technical_plan" in result:
        console.print(Panel(Markdown(result["technical_plan"]), title="Technical Plan", border_style="magenta"))
    if "executive_brief" in result:
        console.print(Panel(Markdown(result["executive_brief"]), title="Executive Brief", border_style="green"))

    console.print(f"[dim]Run ID:[/dim] {result.get('run_id')}  |  Logs: {Path(args.log_dir or 'logs/graphs') / (result.get('run_id') + '.json')}\n")


if __name__ == "__main__":
    main()
