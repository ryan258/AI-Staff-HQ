#!/usr/bin/env python3
"""Executable LangGraph workflow: Code Feature Implementation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from rich.console import Console
from langgraph.graph import END

from orchestrator.graph_runner import GraphRunner, build_state_graph, GraphState
from workflows.constants import SpecialistSlugs


console = Console()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAFF_DIR = PROJECT_ROOT / "staff"


def build_graph(runner: GraphRunner):
    """Assemble the Code Feature workflow graph."""
    graph = build_state_graph()

    # Phase 1: Spec Design (Architect)
    spec_design = runner.make_agent_node(
        specialist_slug=SpecialistSlugs.SOFTWARE_ARCHITECT,
        state_key="spec",
        step_name="spec_design",
        prompt_builder=lambda state: (
            "Design a technical specification for the following feature request. "
            "Include file structure, key classes, and logic flow.\n\n"
            f"Feature Request: {state.get('topic')}"
        ),
    )

    # Phase 2: Implementation (Toolmaker)
    implementation = runner.make_agent_node(
        specialist_slug=SpecialistSlugs.TOOLMAKER,
        state_key="code",
        step_name="implementation",
        prompt_builder=lambda state: (
            "Implement the feature based on this specification. "
            "Provide the code for the necessary files.\n\n"
            f"Specification:\n{state.get('spec', 'N/A')}"
        ),
    )

    # Phase 3: Quality Check (QA)
    quality_check = runner.make_agent_node(
        specialist_slug=SpecialistSlugs.QUALITY_CONTROL_SPECIALIST,
        state_key="qa_report",
        step_name="quality_check",
        prompt_builder=lambda state: (
            "Review the implementation against the specification. "
            "Identify potential bugs, edge cases, or style issues.\n\n"
            f"Specification:\n{state.get('spec', 'N/A')}\n\n"
            f"Implementation:\n{state.get('code', 'N/A')}"
        ),
    )

    # Nodes
    graph.add_node("spec_design", spec_design)
    graph.add_node("implementation", implementation)
    graph.add_node("quality_check", quality_check)

    # Edges
    graph.add_edge("spec_design", "implementation")
    graph.add_edge("implementation", "quality_check")
    graph.add_edge("quality_check", END)

    graph.set_entry_point("spec_design")
    return graph.compile()


def run_code_feature(
    topic: str,
    *,
    auto_approve: bool = True,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    log_dir: Optional[Path] = None,
) -> GraphState:
    """Run the Code Feature workflow."""
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


if __name__ == "__main__":
    # Simplified CLI for testing
    run_code_feature("Test Feature", auto_approve=True)
