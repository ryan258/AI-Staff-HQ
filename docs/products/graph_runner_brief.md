# Product Brief: GraphRunner

**Version:** 1.0.0
**Status:** Enterprise Grade / Production Ready
**One-Liner:** A lightweight, type-safe orchestration engine for multi-agent workflows built on LangGraph.

## The Problem

Running multiple AI agents in sequence (e.g., Writer -> Editor -> SEO) often results in "spaghetti code" with fragile state management, poor visibility into execution steps, and no standard way to handle human approvals.

## The Solution

`GraphRunner` provides a structured, observable runtime for agentic workflows. It treats agent interactions as a directed acyclic graph (DAG) with typed state, structured logging, and built-in approval gates.

## Key Features

- **Type-Safe State:** Uses `TypedDict` (`GraphState`) to ensure data consistency between agents. No more guessing what keys exist in the `context` dictionary.
- **Observability First:** Every step, prompt, and output is automatically logged to `~/.ai-staff-hq/logs/` with detailed timestamps and run metadata.
- **Human-in-the-Loop:** Built-in `make_approval_node` allows you to pause execution for human review (CLI or API) before proceeding to critical steps.
- **Dynamic Caching:** Memoizes agent initialization (`get_agent`) to reduce overhead during complex multi-step runs.
- **Framework Agnostic:** While optimized for `ai-staff-hq` specialists, it can orchestrate any callable that accepts and returns state.

## Technical Specifications

- **Stack:** Python 3.12+, LangGraph, Pydantic (TypedDict)
- **Path:** `ai-staff-hq/orchestrator/graph_runner.py`
- **Dependencies:** `langgraph`, `rich` (for CLI visualization)

## Usage Example

```python
from orchestrator.graph_runner import GraphRunner, build_state_graph

runner = GraphRunner(staff_dir=Path("./staff"))
graph = build_state_graph()

# Define nodes
analysis = runner.make_agent_node(
    specialist_slug="market-analyst",
    state_key="analysis",
    prompt_builder=lambda s: f"Analyze: {s['topic']}"
)

# Build graph
graph.add_node("analysis", analysis)
graph.set_entry_point("analysis")

# Execute
result = runner.run_graph(graph.compile(), {"topic": "AI Trends"})
print(result["analysis"])
```

## Value Proposition

For a developer with limited energy/spoons, `GraphRunner` removes the cognitive load of managing complex async flows. It transforms "scripting" into "engineering" by enforcing structure and logging by default.
