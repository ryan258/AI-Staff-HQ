#!/usr/bin/env python3
"""Executable LangGraph workflow: Strategic Planning."""

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


console = Console()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAFF_DIR = PROJECT_ROOT / "staff"


def build_graph(runner: GraphRunner):
    """Assemble the Strategic Planning workflow graph."""
    graph = build_state_graph()

    # Phase 1: Market Analysis
    market_analysis = runner.make_agent_node(
        specialist_slug="market-analyst",
        state_key="analysis",
        step_name="market_analysis",
        prompt_builder=lambda state: (
            "Analyze market trends, opportunities, and risks for: "
            f"'{state.get('topic')}'. Keep it concise and strategic."
        ),
    )

    # Phase 2: Creative Strategy
    creative_strategy = runner.make_agent_node(
        specialist_slug="creative-strategist",
        state_key="strategy",
        step_name="creative_strategy",
        prompt_builder=lambda state: (
            "Based on this market analysis, propose 3 distinct strategic angles or campaign concepts.\n\n"
            f"Topic: {state.get('topic')}\n\n"
            f"Market Analysis:\n{state.get('analysis', 'N/A')}"
        ),
    )

    # Phase 3: Executive Brief
    executive_brief = runner.make_agent_node(
        specialist_slug="chief-of-staff",
        state_key="executive_brief",
        step_name="executive_brief",
        prompt_builder=lambda state: (
            "Synthesize the market analysis and creative strategy into a one-page Executive Brief. "
            "Recommend the best path forward.\n\n"
            f"Topic: {state.get('topic')}\n\n"
            f"Market Analysis:\n{state.get('analysis', 'N/A')}\n\n"
            f"Creative Strategy:\n{state.get('strategy', 'N/A')}"
        ),
    )

    # Nodes
    graph.add_node("market_analysis", market_analysis)
    graph.add_node("creative_strategy", creative_strategy)
    graph.add_node("executive_brief", executive_brief)

    # Edges (Linear flow)
    graph.add_edge("market_analysis", "creative_strategy")
    graph.add_edge("creative_strategy", "executive_brief")
    graph.add_edge("executive_brief", END)

    graph.set_entry_point("market_analysis")
    return graph.compile()


def run_strategic_planning(
    topic: str,
    *,
    auto_approve: bool = True,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    log_dir: Optional[Path] = None,
) -> GraphState:
    """Run the Strategic Planning workflow."""
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
    parser = argparse.ArgumentParser(description="Run Strategic Planning Workflow")
    parser.add_argument("topic", help="Topic to analyze")
    parser.add_argument("--auto-approve", action="store_true")
    parser.add_argument("--model", help="Model override")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--log-dir", type=Path)

    args = parser.parse_args()

    console.print(f"[bold]Strategic Planning: {args.topic}[/bold]")

    try:
        result = run_strategic_planning(
            args.topic,
            auto_approve=args.auto_approve,
            model=args.model,
            temperature=args.temperature,
            log_dir=args.log_dir,
        )
        
        console.print("\n[green]Workflow Complete[/green]")
        console.print(f"Run ID: {result.get('run_id')}")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    main()
