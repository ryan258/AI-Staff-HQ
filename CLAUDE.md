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
3. Follow the TodoWrite workflow for tracking
4. Run tests after implementation: `pytest tests/ -v`

### 3. UI Development

When creating or modifying UI:
1. **Apply Candlelite theme FIRST** - this is non-negotiable
2. Use CSS variables for colors
3. Ensure accessibility (contrast ratios)
4. Test in Streamlit: `streamlit run ui/app.py`

### 4. Specialist Management

Creating new specialists:
```bash
# 1. Create YAML in appropriate department
cp templates/persona/new-staff-member-template.md staff/[dept]/[slug].yaml

# 2. Validate
python tools/validate_specialist.py staff/[dept]/[slug].yaml

# 3. Test loading
python tools/activate.py [slug]
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

### Tool Usage

- Use **Read** before Edit/Write (required)
- Use **Glob** for file pattern matching
- Use **Grep** for code search
- Use **Task** tool with Explore agent for codebase exploration
- Prefer parallel tool calls when operations are independent

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
pytest tests/ -v

# Run specific test file
pytest tests/test_state.py -v

# Run specific test
pytest tests/test_state.py::test_clear_session -v
```

---

## Configuration Files

- `.env` - API keys and environment config
- `config/model_routing.yaml` - Model routing rules
  - **Budget mode is DISABLED by default** (enabled: false)
  - Role-based routing takes precedence
  - Department fallback routing

---

## Session Management

Sessions persist to `~/.ai-staff-hq/sessions/[specialist]/[session_id].json`

Session ID format: `YYYYMMDD_HHMMSS_hex8` (24 characters)

Clear session in interactive mode: `/clear`

---

## Git Workflow

When committing changes:
1. Small, focused commits (1 issue per commit)
2. Run tests before committing
3. Follow commit message format:
   ```
   type: description

   🤖 Generated with Claude Code

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   ```

---

## Questions?

Refer to:
- **AGENTS.md** - General AI agent guide
- **README.md** - Project overview
- **GETTING-STARTED.md** - Setup
- **QUICK-REFERENCE.md** - Specialist directory
