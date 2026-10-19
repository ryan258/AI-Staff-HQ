# Claude Guide for AI-Staff-HQ

This guide provides Claude-specific instructions for working with the AI-Staff-HQ project.

---

## Candlelite Theme - UI Design Standards

**CRITICAL:** When implementing any user-facing UI (web, CLI, or visual interfaces), you MUST use the Candlelite theme.

### Theme Requirements

You MUST implement the Candlelite theme and use ONLY the following hex colors in all user-facing UI styles (CSS, inline styles, SVG fills/strokes, etc.):

- **#121212** (Off-Black, backgrounds)
- **#EBD2BE** (Warm Beige, primary text)
- **#A6ACCD** (Muted Lavender, primary accents/borders)
- **#98C379** (Green, success/positive)
- **#E06C75** (Red, danger/negative)

### Rules

- Do NOT use any other colors, including rgba/hsla, hex with alpha, gradients that introduce non-palette colors, or shadows that add non-palette tones.
- Prefer CSS variables at :root and reference them everywhere.
- Keep inline styles to a minimum; add class-based CSS instead.
- Map semantic usage to palette vars (e.g., borders use lavender, alerts use green/red).
- Maintain contrast and readability; default text should be #EBD2BE on #121212.

### Recommended CSS Variables

```css
:root {
  --bg-color: #121212;
  --text-color: #EBD2BE;
  --accent-primary: #A6ACCD;
  --accent-success: #98C379;
  --accent-danger: #E06C75;
  --card-bg: var(--bg-color);
  --border-color: var(--accent-primary);
}
```

### Python/Rich Console Colors

When using the Rich library for CLI output, map colors to the Candlelite theme:

```python
from rich.console import Console
from rich.theme import Theme

candlelite_theme = Theme({
    "info": "#A6ACCD",      # Muted Lavender
    "success": "#98C379",   # Green
    "warning": "#EBD2BE",   # Warm Beige
    "danger": "#E06C75",    # Red
    "muted": "#A6ACCD",     # Muted Lavender
})

console = Console(theme=candlelite_theme)
```

### Streamlit UI

When working with `ui/app.py`, apply custom CSS with the Candlelite palette:

```python
import streamlit as st

st.markdown("""
<style>
    :root {
        --bg-color: #121212;
        --text-color: #EBD2BE;
        --accent-primary: #A6ACCD;
        --accent-success: #98C379;
        --accent-danger: #E06C75;
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
    }

    .stButton > button {
        background-color: var(--accent-primary);
        color: var(--bg-color);
        border: 1px solid var(--accent-primary);
    }
</style>
""", unsafe_allow_html=True)
```

---

## Project Architecture

AI-Staff-HQ is a LangChain/LangGraph-based multi-agent orchestration system with 68 specialized AI agents.

### Key Components

1. **Specialist Engine** (`tools/engine/`)
   - `core.py` - Agent loading and execution
   - `state.py` - Conversation persistence
   - `llm.py` - Model routing with budget mode
   - `config.py` - Pydantic configuration

2. **Orchestration** (`orchestrator/`)
   - `graph_runner.py` - LangGraph workflow execution
   - Supports approval gates, structured logging, agent caching

3. **Workflows** (`workflows/`)
   - `constants.py` - Specialist slug constants (NO MAGIC STRINGS)
   - `graphs/` - LangGraph workflow definitions

4. **UI** (`ui/app.py`)
   - Streamlit dashboard
   - **MUST use Candlelite theme**

### Code Quality Standards

- **Type Hints**: Use everywhere
- **Pydantic**: For all config and data models
- **Constants**: Import from `workflows/constants.py`, never hardcode specialist names
- **Error Handling**: Log errors to stderr, never suppress exceptions silently
- **Testing**: pytest for all new features

---

## Common Claude Tasks

### 1. Code Review and Refactoring

When reviewing or refactoring code:
- Look for magic strings (specialist names) and replace with constants
- Ensure error handling logs to stderr
- Verify type hints are present
- Check that tests exist and pass

### 2. Adding Features

When adding features:
1. Read existing patterns first (don't propose changes to code you haven't read)
2. Use EnterPlanMode for non-trivial changes
3. Run tests after implementation: `uv run pytest tests/ -q`

### 3. UI Development

When creating or modifying UI:
1. **Apply Candlelite theme FIRST** - this is non-negotiable
2. Use CSS variables for colors
3. Ensure accessibility (contrast ratios)
4. Test in Streamlit: `uv run streamlit run ui/app.py`

### 4. Specialist Management

Creating new specialists:
```bash
# 1. Create YAML in appropriate department
cp templates/persona/new-staff-member-template.md staff/[dept]/[slug].yaml

# 2. Validate (checks every specialist in staff/)
uv run tools/validate_specialist.py

# 3. Test loading
uv run tools/activate.py [slug]
```

### 5. Workflow Development

When creating LangGraph workflows:
```python
# GOOD - Uses constants
from workflows.constants import SpecialistSlugs

node = runner.make_agent_node(
    specialist_slug=SpecialistSlugs.MARKET_ANALYST,
    state_key="analysis",
    step_name="market_analysis"
)

# BAD - Magic string
node = runner.make_agent_node(
    specialist_slug="market-analyst",  # DON'T DO THIS
    ...
)
```

---

## Claude-Specific Patterns

### Planning

- Use EnterPlanMode for:
  - New features
  - Multi-file changes
  - Architectural decisions
  - When approach is unclear

- Skip EnterPlanMode for:
  - Single-line fixes
  - Typos
  - Simple, obvious changes

### Communication

- Be concise in terminal output
- Use Rich for formatted CLI output (with Candlelite colors)
- Never use emojis unless explicitly requested
- Focus on facts over validation

---

## Testing

```bash
# Run all tests
uv run pytest tests/ -q

# Run specific test file
uv run pytest tests/test_state.py -v

# Run specific test
uv run pytest tests/test_state.py::test_clear_session -v
```

---

## Configuration Files

- `.env` - API keys and environment config
- `config/model_routing.yaml` - Model routing rules
  - **Budget mode is DISABLED by default** (enabled: false)
  - Role-based routing takes precedence
  - Department fallback routing
  - `fallback_models`: OpenRouter retry chain for down or retired models.
    Free model IDs disappear without notice; verify against
    `https://openrouter.ai/api/v1/models` before changing defaults.
- `REQUEST_TIMEOUT_SECONDS` / `MAX_RETRIES` in `.env` bound every model call.

---

## Session Management

Sessions persist to `~/.ai-staff-hq/sessions/[specialist]/[session_id].json`

Session ID format: `YYYYMMDD_HHMMSS_hex8` (24 characters)

Clear session in interactive mode: `/clear`

---

## Git Workflow

Commit only when Ryan explicitly asks. Then: one issue per commit, tests
green first, `type: description` subject. Use the attribution trailer the
harness supplies rather than a hardcoded model name.

---

## Questions?

Refer to:
- **AGENTS.md** - General AI agent guide
- **README.md** - Project overview
- **GETTING-STARTED.md** - Setup
- **docs/QUICK-REFERENCE.md** - Specialist directory
- **MODEL_CONTROL.md** - Model selection and routing

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **AI-Staff-HQ** (2322 symbols, 3817 relationships, 134 execution flows).

> Index stale? Run `node .gitnexus/run.cjs analyze --index-only` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? Bootstrap with `npx`, `bunx`, or `pnpm dlx` — e.g. `bunx gitnexus@latest analyze` (npm 11 npx crash; #1939).

## Always Do

- **MUST run impact before editing.** Use `impact({target: "symbolName", direction: "upstream"})` or `node .gitnexus/run.cjs impact "symbolName" --direction upstream --repo .`; report callers, processes, and risk. Never substitute grep for graph analysis.
- **MUST analyze graph changes before committing.** Use `detect_changes({scope: "all"})` (MCP) or `node .gitnexus/run.cjs detect-changes --scope all --repo .` (CLI fallback). `partial: true` or `truncated: true` is not a clean check — a zero means unseen, not unaffected; re-run it. For regression review: `detect_changes({scope: "compare", base_ref: "main"})` or `node .gitnexus/run.cjs detect-changes --scope compare --base-ref "main" --repo .`.
- MUST warn on HIGH/CRITICAL `risk` pre-edit; never use `riskSharedAxes` to waive a HIGH/CRITICAL `risk` warning. Compare File/symbol: MCP File omits axes; Graph-RAG expands File.
- **MUST treat `risk: UNKNOWN` as unresolved, not as low.** An empty caller set is not evidence the symbol is unused — it can also mean the callers are not resolvable by the index (plain-object property access, dynamic dispatch, cross-language calls). `impact` pairs `UNKNOWN` with a `riskNote` saying so. Confirm with a text search before treating the symbol as safe to change or delete; do not proceed on the strength of a zero.
- **MUST use `query({search_query: "concept"})` for concepts/flows, `context({name: "symbolName"})` for a named symbol, or `impact` for blast radius, on read-only callers, dependencies, imports, or execution flow.** Graph first; text search only for empty/`UNKNOWN`/literals.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method before MCP/CLI impact analysis.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis, and never read `UNKNOWN` as an all-clear — it means the walk could not answer, which is the one verdict that requires confirming by other means.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit before MCP/CLI graph change analysis.

## Resources

| Resource | Use for |
| --- | --- |
| `gitnexus://repo/AI-Staff-HQ/context` | Codebase overview, check index freshness |
| `gitnexus://repo/AI-Staff-HQ/clusters` | All functional areas |
| `gitnexus://repo/AI-Staff-HQ/processes` | All execution flows |
| `gitnexus://repo/AI-Staff-HQ/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
| --- | --- |
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
