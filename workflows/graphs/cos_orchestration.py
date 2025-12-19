#!/usr/bin/env python3
"""Executable LangGraph workflow: Dynamic CoS Orchestration (Manager-Worker Loop)."""

from __future__ import annotations

import json
import re
import argparse
from pathlib import Path
from typing import Optional, Literal
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END

from orchestrator.graph_runner import GraphRunner, build_state_graph, GraphState


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAFF_DIR = PROJECT_ROOT / "staff"


def get_available_specialists(staff_dir: Path) -> dict[str, list[str]]:
    """Discover all available specialists grouped by department."""
    specialists = {}
    for dept_dir in staff_dir.iterdir():
        if not dept_dir.is_dir() or dept_dir.name.startswith('.'):
            continue
        dept_specialists = []
        for yaml_file in dept_dir.rglob("*.yaml"):
            # Get the specialist slug (filename without extension)
            slug = yaml_file.stem
            dept_specialists.append(slug)
        if dept_specialists:
            specialists[dept_dir.name] = sorted(dept_specialists)
    return specialists


def extract_json(text: str) -> list:
    """Extract JSON list from text (naive)."""
    try:
        # Find first [ and last ]
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end != -1:
            return json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return []


def build_graph(runner: GraphRunner):
    """Assemble the Dynamic Orchestration graph with a Worker Loop."""
    graph = build_state_graph()

    # Discover available specialists
    available_specialists = get_available_specialists(STAFF_DIR)

    # Format specialist list for prompt
    specialist_list = []
    for dept, specialists in sorted(available_specialists.items()):
        specialist_list.append(f"  {dept.upper()}: {', '.join(specialists)}")
    specialists_text = "\n".join(specialist_list)

    # Node 1: Planning (Manager)
    # Generates a JSON list of tasks for other specialists
    def plan_step(state: GraphState) -> GraphState:
        # Use public get_agent
        agent = runner.get_agent("chief-of-staff", session_id=state.get("run_id"))
        prompt = (
            "You are the Orchestrator. Break down this request into specific tasks for your staff.\n"
            "You MUST ONLY delegate to specialists from this EXACT list below. "
            "Use their exact slug names (e.g., 'copywriter', 'market-analyst').\n\n"
            "AVAILABLE SPECIALISTS:\n"
            f"{specialists_text}\n\n"
            "Return ONLY a JSON list of tasks. Do not do the work yourself.\n"
            "If you try to use a specialist not in the list above, it will fail.\n\n"
            "Format:\n"
            '[{"specialist": "slug-name", "task": "specific instructions"}, ...]\n\n'
            f"Request: {state.get('topic')}"
        )
        response = agent.query(prompt)

        # Parse tasks
        tasks = extract_json(response)

        # Validate specialists exist - filter out invalid ones
        valid_specialists = set()
        for dept_specialists in available_specialists.values():
            valid_specialists.update(dept_specialists)

        validated_tasks = []
        invalid_tasks = []
        for task in tasks:
            specialist_slug = task.get("specialist", "").lower()
            if specialist_slug in valid_specialists:
                validated_tasks.append(task)
            else:
                invalid_tasks.append(task)
                # Re-assign invalid tasks to chief-of-staff to handle
                validated_tasks.append({
                    "specialist": "chief-of-staff",
                    "task": f"[Reassigned from non-existent '{specialist_slug}']: {task.get('task', '')}"
                })

        runner.record_step(state, "cos_planning", {
            "prompt": prompt,
            "response": response,
            "parsed_tasks": tasks,
            "validated_tasks": validated_tasks,
            "invalid_specialists_requested": [t.get("specialist") for t in invalid_tasks],
            "parse_success": bool(tasks)
        })

        return {**state, "strategy_plan": response, "queue": validated_tasks, "results": []}

    # Node 2: Worker (Dynamic Dispatch)
    def worker_step(state: GraphState) -> GraphState:
        queue = list(state.get("queue", []))
        if not queue:
            return state
            
        # Pop next task
        task = queue.pop(0)
        slug = task.get("specialist", "chief-of-staff").lower()
        instruction = task.get("task", "")
        
        # Run Agent
        try:
            agent = runner.get_agent(slug, session_id=state.get("run_id"))
            response = agent.query(instruction)
        except Exception as e:
            # Log specific error but continue workflow
            error_msg = f"Failed to load/run agent '{slug}': {e}"
            response = f"[System Error]: {error_msg}"
            
            # Helper fallback if specific agent fails
            if slug != "chief-of-staff":
                 try:
                     fallback_agent = runner.get_agent("chief-of-staff", session_id=state.get("run_id"))
                     fallback_resp = fallback_agent.query(f"Task for {slug} failed. Please handle: {instruction}")
                     response += f"\n\n[CoS Fallback]: {fallback_resp}"
                 except Exception:
                     pass

        # Record result
        result_entry = {
            "specialist": slug,
            "task": instruction,
            "output": response
        }
        
        update = {
            "queue": queue,
            "results": state.get("results", []) + [result_entry]
        }
        
        runner.record_step(state, f"worker_{slug}", result_entry)
        return {**state, **update}

    # Node 3: Synthesis
    def synthesis_step(state: GraphState) -> GraphState:
        agent = runner.get_agent("chief-of-staff", session_id=state.get("run_id"))
        
        # Compile context from results
        results_text = ""
        for res in state.get("results", []):
            results_text += f"\n### Output from {res['specialist']}:\n{res['output']}\n"
            
        prompt = (
            "Review the work produced by your staff and synthesize the final answer.\n"
            "Ensure coherence and quality.\n\n"
            f"Original Request: {state.get('topic')}\n\n"
            f"Staff Outputs:\n{results_text}"
        )
        
        response = agent.query(prompt)
        
        runner.record_step(state, "cos_synthesis", {
            "prompt": prompt,
            "response": response
        })
        
        return {**state, "final_output": response}

    # Conditional Edge Logic
    def check_queue(state: GraphState) -> Literal["worker", "synthesis"]:
        if state.get("queue"):
            return "worker"
        return "synthesis"

    # Add Nodes
    graph.add_node("planning", plan_step)
    graph.add_node("worker", worker_step)
    graph.add_node("synthesis", synthesis_step)

    # Add Edges
    graph.add_edge("planning", "worker") # Start loop (or skip if queue empty checked inside?)
    # Actually we need a conditional edge after planning to handle empty queue immediately
    # But for simplicity, let's route Planning -> Worker -> Check
    # If Planning returns empty queue, Worker checks queue, finds empty, returns.
    # Then we check again?
    # Better: Planning -> Check -> Worker/Synthesis
    
    # Creating a router node/function
    graph.add_conditional_edges(
        "planning",
        check_queue,
        {"worker": "worker", "synthesis": "synthesis"}
    )
    
    graph.add_conditional_edges(
        "worker",
        check_queue,
        {"worker": "worker", "synthesis": "synthesis"}
    )
    
    graph.add_edge("synthesis", END)

    graph.set_entry_point("planning")
    return graph.compile()


def run_cos_orchestration(
    topic: str,
    *,
    auto_approve: bool = True,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    log_dir: Optional[Path] = None,
) -> GraphState:
    """Run the dynamic orchestration."""
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
        "queue": [],
        "results": []
    }
    return runner.run_graph(graph, initial_state)

if __name__ == "__main__":
    # Test
    run_cos_orchestration("Create a 3-agent marketing team plan for 'Coffee AI'", auto_approve=True)
