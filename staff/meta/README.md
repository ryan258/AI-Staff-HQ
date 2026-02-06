# Morphling Operator Guide

`Morphling` is your universal adaptive specialist. It is designed to take almost any task, infer the best working style, and execute with the right persona for the problem.

Source definition: `staff/meta/morphling.yaml`

## What Morphling Is Best At

Morphling is strongest when you need flexibility, speed, and cross-domain synthesis:

- Ambiguous requests where you are not sure which specialist to route to
- Mixed tasks (for example: strategy + coding + writing in one session)
- Fast first drafts that can later be handed to a domain specialist
- Translation between specialist outputs (technical to executive, research to copy, etc.)
- One-off problems where creating a custom workflow is overkill

## Core Capabilities (From `morphling.yaml`)

### 1) Adaptive Problem Solving
Morphling dynamically changes its method based on the request.

Use it for:
- Debugging a stack trace
- Designing a launch plan
- Writing narrative or marketing copy
- Structuring analysis with decision criteria

### 2) Context Absorption
Morphling is optimized to absorb local context and align to existing patterns.

Use it for:
- Codebase-aware recommendations
- Refactors that follow project conventions
- Summaries of large context blocks

### 3) Persona Shapeshifting
Morphling can emulate the best role for the task.

Examples:
- "Act as a Senior Rust Engineer and find the race condition."
- "Act as a Direct Response Copywriter and write 5 hooks."
- "Act as a Data Scientist and design the experiment."

### 4) Zero-Shot Optimization
Morphling is meant to produce useful outputs without heavy prompt engineering.

Use it when:
- You need quality output quickly
- You do not want to pick a specialist first
- You want a high-quality baseline before specialist refinement

## When To Use Morphling vs Other Specialists

Use Morphling when:
- The task spans multiple departments
- You are triaging and scoping
- You need an adaptive first pass

Use a dedicated specialist when:
- You need deep domain rigor in one area
- Compliance/precision is critical (legal, tax, security, medical)
- You want specialist-specific frameworks from that YAML

Use Chief of Staff when:
- Multiple specialists must collaborate with handoffs and quality gates

## Activation and CLI Usage

Run from `/Users/ryanjohnson/dotfiles/ai-staff-hq`.

### Interactive Session

```bash
uv run tools/activate.py morphling
```

### One-Shot Query

```bash
uv run tools/activate.py morphling -q "Design a migration plan from monolith to services."
```

### Resume Prior Session

```bash
uv run tools/activate.py morphling --resume last
uv run tools/activate.py morphling --resume 20260205_203015_ab12cd34
```

### Override Model and Temperature

```bash
uv run tools/activate.py morphling \
  --model "openai/gpt-4.1" \
  --temperature 0.3 \
  -q "Review this architecture proposal and identify failure modes."
```

### Activate by File Path

```bash
uv run tools/activate.py staff/meta/morphling.yaml
```

### List Specialists

```bash
uv run tools/activate.py --list
```

Note: `--department` does not currently include `meta`, so use full list mode to find Morphling.

## Interactive Session Commands

Inside interactive mode:

- `exit`, `quit`, `/bye`, `/exit`: save and quit
- `/clear` or `clear`: reset conversation context and start a new session ID

## Session, State, and Logs

- Sessions are stored at `~/.ai-staff-hq/sessions/morphling/`
- Session ID format: `YYYYMMDD_HHMMSS_hex8`
- Conversation history is trimmed to `max_history_turns` (default 20 turns) while preserving system prompt
- If logging is enabled, per-session logs are written to `logs/<session_id>.md`

## Model Routing Behavior

Selection order in engine:

1. `--model` override
2. Budget mode model (if enabled in routing config)
3. `default_model` from environment/config
4. Role routing
5. Department fallback

Practical implication: if `default_model` is set, role/department routing may not be used unless you override.

## Prompting Morphling for Maximum Capacity

Use this structure:

```text
Morphling, take this as a [persona].

Objective:
[single clear outcome]

Context:
[relevant facts, files, constraints]

Requirements:
[must-have rules, scope, non-goals]

Output format:
[table, checklist, code patch, ADR, bullets, JSON schema]

Quality bar:
[acceptance criteria, tests, edge cases, risk checks]
```

### High-Leverage Prompt Patterns

#### 1) Triage + Plan + Execute

```text
Morphling, act as a principal engineer.
First: identify root cause hypotheses.
Second: propose a ranked fix plan.
Third: implement the top fix and include verification steps.
```

#### 2) Cross-Domain Synthesis

```text
Morphling, blend market analyst + copywriter + product strategist personas.
Create a launch brief with:
1) ICP insight
2) messaging angles
3) offer strategy
4) 30-day experiment plan with KPIs.
```

#### 3) Critique Loop

```text
Morphling, generate v1.
Then self-critique against this rubric: clarity, risks, feasibility, testability.
Then return v2 with explicit improvements.
```

#### 4) Strict Output Contract

```text
Morphling, return only JSON with keys:
summary, assumptions, risks, plan, next_actions.
No extra prose.
```

## Advanced Operating Modes

### Mode A: Universal Router
Ask Morphling to decide whether to stay in-role or hand off:

```text
Morphling, decide whether this is best solved by you directly or by a specialist.
If handoff is better, name the specialist and provide a ready-to-send handoff brief.
```

### Mode B: Translator Between Specialists

```text
Morphling, translate this Software Architect output into an executive summary with decisions, risks, and cost impact.
```

### Mode C: Quality Gate Reviewer

```text
Morphling, review this deliverable as a strict QA lead.
Flag issues by severity and propose exact fixes.
```

## Collaboration Patterns

### Pattern 1: Morphling First, Specialist Deep Dive

1. Use Morphling for problem framing and draft.
2. Route refined task to specialist for depth.
3. Return to Morphling for synthesis into final format.

### Pattern 2: Chief of Staff Orchestration with Morphling Support

1. Chief of Staff coordinates multi-specialist workflow.
2. Morphling handles integration gaps, translation, and rapid adaptation between outputs.

### Pattern 3: Iterative Improvement Sprint

1. Morphling creates v1.
2. You provide targeted feedback.
3. Morphling revises with explicit delta notes.
4. Repeat until acceptance criteria are satisfied.

## Common Use Cases

- Code debugging and refactoring strategy
- Architecture reviews and tradeoff analysis
- Product and go-to-market planning
- Sales/marketing copy in multiple tones
- Technical documentation and SOP drafting
- Data interpretation and experiment design
- Brainstorming with structured outputs

## Troubleshooting

### "Specialist not found"

- Confirm slug: `morphling`
- Or use full path: `staff/meta/morphling.yaml`
- Run `uv run tools/activate.py --list`

### "No API keys found"

Set one of:
- `OPENROUTER_API_KEY` (recommended)
- `OPENAI_API_KEY` (fallback path)

### Responses drift or lose focus

- Start a new clean context: `/clear`
- Lower temperature: `--temperature 0.2` to `0.4`
- Add stricter output contract and acceptance criteria

### Output quality is generic

- Specify persona explicitly
- Provide context artifacts
- Require self-critique + revision pass

## Tuning Morphling Itself (`morphling.yaml`)

If you customize Morphling:

- `core_identity` changes role/personality/expertise framing
- `core_capabilities` changes what the system prompt emphasizes
- `activation_patterns` changes suggested trigger language
- `performance_standards` changes evaluation criteria
- `deep_dive` changes deliverables and knowledge framing

Validate after edits:

```bash
uv run python tools/validate_specialist.py
```

Then test:

```bash
uv run tools/activate.py morphling -q "Run a smoke test of your adaptive capabilities."
```

## Quick Command Cheat Sheet

```bash
# Interactive
uv run tools/activate.py morphling

# One-shot
uv run tools/activate.py morphling -q "..."

# Resume latest
uv run tools/activate.py morphling --resume last

# Override model
uv run tools/activate.py morphling --model "openai/gpt-4.1"

# Override temperature
uv run tools/activate.py morphling --temperature 0.3

# Debug mode
uv run tools/activate.py morphling --debug
```

## Recommended Daily Workflow

1. Start with Morphling for scoping and first draft.
2. Decide: keep Morphling or hand off to specialist.
3. Run one critique-and-revise loop.
4. Save final with explicit assumptions, risks, and next actions.

This gives you speed, flexibility, and consistent output quality without over-designing every task.
