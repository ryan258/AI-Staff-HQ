# Phase 4: Autonomous Swarm & Interface

This phase delivers executable multi-agent workflows (LangGraph) and a browser UI for running them.

## What’s Included
- `orchestrator/graph_runner.py` — helper for building LangGraph workflows with approvals, logging, and agent caching.
- `workflows/graphs/strategy_tech_handoff.py` — Strategy → Tech → Executive Brief graph (market-analyst → software-architect → chief-of-staff).
- `ui/app.py` — Streamlit dashboard to launch the graph and view results.

## Install (with optional extras)
```bash
# Base (includes langgraph for orchestration)
uv sync

# UI extra if you want Streamlit
uv sync --extra ui
```

## Run the graph via CLI
```bash
uv run workflows/graphs/strategy_tech_handoff.py "Build an AI fitness coach app" --auto-approve
```
- Use `--auto-approve` to skip interactive approval gates.
- `--model` and `--temperature` propagate to all specialists.
- Logs: `logs/graphs/<run_id>.json`.

## Run the Streamlit UI
```bash
uv run streamlit run ui/app.py
```
- Configure auto-approval, model override, and temperature in the sidebar.
- Start the Strategy → Tech graph from the main panel and view step logs inline.

## Extend with new graphs
1) Start with `build_state_graph()` from `orchestrator/graph_runner.py`.
2) Create nodes via `runner.make_agent_node(...)` and optional gates with `runner.make_approval_node(...)`.
3) Compile with LangGraph and invoke via `GraphRunner.run_graph`.
4) Save your graph under `workflows/graphs/` and document run instructions in this file.
