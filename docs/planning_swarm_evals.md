# Planning Swarm Evals

This repo now includes a deterministic eval harness for the flagship planning swarm.

## Why It Exists

The active roster is intentionally small. That only works if changes to:

- roster membership
- capability names
- matching heuristics
- task dependency logic

can be checked against a stable set of planning cases.

These evals are designed to answer one question:

`If we change the active roster or matching logic, did planning quality get better or worse?`

## What It Tests

The starter suite checks:

- task parsing success vs fallback behavior
- task count discipline
- warning count from task validation
- top specialist choice for representative tasks
- execution-wave shape, including parallelizable work
- how often work collapses back to `chief-of-staff`

## Run It

```bash
uv run workflows/planning_swarm_eval.py
```

For machine-readable output:

```bash
uv run workflows/planning_swarm_eval.py --json
```

## How To Use Results

If a case fails on specialist choice:
- check whether the active roster is missing the right role
- check whether the capability wording in the YAML is too vague
- check whether the matching heuristic is over-rewarding fuzzy matches

If a case fails on wave count or parallel waves:
- inspect task dependencies
- look for tasks that should be independent but were chained together
- look for tasks that should be sequential but were left independent

If a case falls back to `chief-of-staff` too often:
- the active roster may be too small for that use case
- or the planner is emitting capability labels that do not map cleanly to the roster

## Add Real Briefs One By One

Start with the scaffold file:

- [planning_swarm_real_briefs.yaml](/Users/ryanjohnson/Projects/AI-Staff-HQ/evals/planning_swarm_real_briefs.yaml)

Replace the placeholder brief with one of your real rough prompts, then capture the planner output and baseline expectations:

```bash
uv run workflows/planning_swarm_capture.py --case your-case-id
```

That command will:

- run the live planner on the selected real brief
- store the raw planner response in the case file
- generate an `expect` block from the observed behavior

After capture, the real-brief file becomes a normal deterministic eval file. Run it with:

```bash
uv run workflows/planning_swarm_eval.py --cases evals/planning_swarm_real_briefs.yaml
```

If you want to regenerate a case after changing the active roster or model:

```bash
uv run workflows/planning_swarm_capture.py --case your-case-id
```

## Where To Edit

- Eval cases: [planning_swarm_cases.yaml](/Users/ryanjohnson/Projects/AI-Staff-HQ/evals/planning_swarm_cases.yaml)
- Real briefs: [planning_swarm_real_briefs.yaml](/Users/ryanjohnson/Projects/AI-Staff-HQ/evals/planning_swarm_real_briefs.yaml)
- Eval runner: [planning_swarm_eval.py](/Users/ryanjohnson/Projects/AI-Staff-HQ/workflows/planning_swarm_eval.py)
- Capture workflow: [planning_swarm_capture.py](/Users/ryanjohnson/Projects/AI-Staff-HQ/workflows/planning_swarm_capture.py)
- Active roster: [specialist_roster.yaml](/Users/ryanjohnson/Projects/AI-Staff-HQ/config/specialist_roster.yaml)

Keep the suite small and opinionated. Add cases only when they represent a real planning pattern you care about preserving.
