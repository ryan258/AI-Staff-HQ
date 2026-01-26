# Gemini Guide for AI-Staff-HQ

This guide provides Google Gemini-specific instructions for working with the AI-Staff-HQ project.

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
  --text-color: #ebd2be;
  --accent-primary: #a6accd;
  --accent-success: #98c379;
  --accent-danger: #e06c75;
  --card-bg: var(--bg-color);
  --border-color: var(--accent-primary);
}
```

### Color Mapping Examples

**HTML/CSS:**

```html
<style>
  body {
    background-color: var(--bg-color);
    color: var(--text-color);
  }

  .button-primary {
    background-color: var(--accent-primary);
    color: var(--bg-color);
    border: 2px solid var(--accent-primary);
    padding: 8px 16px;
    cursor: pointer;
  }

  .button-primary:hover {
    background-color: var(--bg-color);
    color: var(--accent-primary);
  }

  .alert-success {
    background-color: var(--bg-color);
    border-left: 4px solid var(--accent-success);
    color: var(--accent-success);
    padding: 12px;
  }

  .alert-danger {
    background-color: var(--bg-color);
    border-left: 4px solid var(--accent-danger);
    color: var(--accent-danger);
    padding: 12px;
  }
</style>
```

**Streamlit (Python):**

```python
import streamlit as st

# Apply Candlelite theme
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
    }

    .stMarkdown, .stText {
        color: var(--text-color);
    }

    .stButton > button {
        background-color: var(--accent-primary);
        color: var(--bg-color);
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
    }

    .stSuccess {
        color: var(--accent-success);
    }

    .stError {
        color: var(--accent-danger);
    }
</style>
""", unsafe_allow_html=True)
```

---

## Project Overview

AI-Staff-HQ is a multi-agent orchestration framework built with Python, LangChain, and LangGraph. It provides:

- **68 Specialized AI Agents** defined in YAML
- **Multi-Agent Workflows** using LangGraph
- **CLI Interface** for direct specialist interaction
- **Streamlit Dashboard** for workflow execution
- **Persistent Conversation State** with session management

### Technology Stack

- **Python 3.12+**
- **LangChain** - Agent framework
- **LangGraph** - Workflow orchestration
- **OpenRouter** - Multi-model LLM access
- **Pydantic** - Configuration and validation
- **Rich** - Terminal UI
- **Streamlit** - Web dashboard
- **pytest** - Testing

---

## Architecture

```
┌─────────────────────────────────────────┐
│           User Interface Layer          │
│  ┌────────────┐      ┌──────────────┐  │
│  │    CLI     │      │  Streamlit   │  │
│  │ activate.py│      │   app.py     │  │
│  └────────────┘      └──────────────┘  │
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│         Orchestration Layer             │
│  ┌──────────────────────────────────┐  │
│  │   GraphRunner (LangGraph)         │  │
│  │   - Multi-agent workflows         │  │
│  │   - Approval gates                │  │
│  │   - Structured logging            │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│            Engine Layer                 │
│  ┌───────────┐  ┌──────────────────┐  │
│  │ Specialist│  │  Model Routing   │  │
│  │   Agent   │  │  (llm.py)        │  │
│  │ (core.py) │  └──────────────────┘  │
│  └───────────┘                         │
│  ┌───────────┐  ┌──────────────────┐  │
│  │   State   │  │   Configuration  │  │
│  │ (state.py)│  │   (config.py)    │  │
│  └───────────┘  └──────────────────┘  │
└─────────────────────────────────────────┘
                  │
┌─────────────────────────────────────────┐
│          Data Layer                     │
│  - 68 Specialist YAML files             │
│  - Model routing configuration          │
│  - Session persistence                  │
└─────────────────────────────────────────┘
```

---

## Development Guidelines

### 1. Code Style

- **Type Hints**: Required on all functions
- **Pydantic Models**: For all config and data structures
- **Constants**: Import from `workflows/constants.py`
  - ✅ `SpecialistSlugs.MARKET_ANALYST`
  - ❌ `"market-analyst"` (magic string)
- **Error Handling**: Always log errors to stderr
- **Docstrings**: Google-style format

### 2. Testing

All new features must include tests:

```bash
# Run full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tools --cov=orchestrator --cov=workflows

# Run specific tests
pytest tests/test_state.py::test_clear_session -v
```

### 3. UI Development

When creating or modifying any UI:

1. **Apply Candlelite theme FIRST** - Non-negotiable
2. Use CSS variables for all colors
3. No inline styles - use CSS classes
4. Ensure accessibility (WCAG AA contrast)
5. Test responsive behavior

Example workflow:

```python
# 1. Define CSS variables at top of file
candlelite_css = """
<style>
:root {
  --bg-color: #121212;
  --text-color: #EBD2BE;
  --accent-primary: #A6ACCD;
  --accent-success: #98C379;
  --accent-danger: #E06C75;
}

/* Then use variables in all selectors */
.my-component {
  background: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--accent-primary);
}
</style>
"""

# 2. Apply early in component lifecycle
st.markdown(candlelite_css, unsafe_allow_html=True)
```

---

## Common Tasks

### Adding a New Specialist

1. Create YAML file:

```bash
cp templates/persona/new-staff-member-template.md staff/tech/new-specialist.yaml
```

2. Edit with required fields:

```yaml
specialist: "Full Name"
role: "Role Title"
slug: "slug-name"
department: tech
expertise:
  - Area 1
  - Area 2
collaboration:
  reports_to: chief-of-staff
  works_with:
    - other-specialist
```

3. Validate:

```bash
python tools/validate_specialist.py staff/tech/new-specialist.yaml
```

4. Test:

```bash
python tools/activate.py new-specialist
```

### Creating a Workflow

Example LangGraph workflow:

```python
from orchestrator.graph_runner import GraphRunner, build_state_graph
from workflows.constants import SpecialistSlugs  # ALWAYS use constants

def build_graph(runner: GraphRunner):
    graph = build_state_graph()

    # Phase 1: Analysis
    analysis = runner.make_agent_node(
        specialist_slug=SpecialistSlugs.MARKET_ANALYST,  # NOT "market-analyst"
        state_key="analysis",
        step_name="market_analysis",
        prompt_builder=lambda state: f"Analyze: {state.get('topic')}"
    )

    # Phase 2: Strategy
    strategy = runner.make_agent_node(
        specialist_slug=SpecialistSlugs.CREATIVE_STRATEGIST,
        state_key="strategy",
        step_name="creative_strategy",
        prompt_builder=lambda state: f"Based on: {state.get('analysis')}"
    )

    # Build graph
    graph.add_node("analysis", analysis)
    graph.add_node("strategy", strategy)
    graph.add_edge("analysis", "strategy")
    graph.set_entry_point("analysis")
    graph.add_edge("strategy", END)

    return graph.compile()
```

### Modifying the Streamlit UI

When updating `ui/app.py`:

1. **Always maintain Candlelite theme**
2. Add custom CSS in a centralized location
3. Use Streamlit components with theme overrides
4. Test locally: `streamlit run ui/app.py`

---

## Configuration

### Environment Variables

Create `.env` from `.env.example`:

```bash
# Primary API (recommended)
OPENROUTER_API_KEY=sk-or-v1-...

# Optional fallbacks
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Model settings
DEFAULT_MODEL=moonshotai/kimi-k2:free
MAX_HISTORY_TURNS=20
MAX_CONTEXT_TOKENS=32000
```

### Model Routing

Edit `config/model_routing.yaml`:

```yaml
# Budget mode (disabled by default)
budget_mode:
  enabled: false # Change to true to use free models
  model: "moonshotai/kimi-k2:free"

# Role-based routing (highest precedence)
role_routing:
  "Market Research & Competitive Analysis Specialist": "moonshotai/kimi-k2:free"

# Department fallback
department_routing:
  strategy: "moonshotai/kimi-k2:free"
  tech: "moonshotai/kimi-k2:free"
```

---

## Session Management

Sessions persist to: `~/.ai-staff-hq/sessions/[specialist]/[session_id].json`

**Session ID Format:** `YYYYMMDD_HHMMSS_hex8` (24 characters)

**Commands:**

- `/clear` - Start new session (keeps system message)
- `/exit` or `exit` - Save and quit
- `/bye` - Quit

**Programmatic Access:**

```python
from tools.engine.state import ConversationState

# Create new session
state = ConversationState("market-analyst")

# Clear session
new_id = state.clear()

# Save session
state.save()

# Load session
state = ConversationState("market-analyst", session_id="20251219_143022_a1b2c3d4")
state.load()
```

---

## Error Handling Best Practices

### DO:

```python
try:
    agent = runner.get_agent(SpecialistSlugs.MARKET_ANALYST, session_id=run_id)
    response = agent.query(task)
except Exception as e:
    # Log to stderr
    print(f"ERROR: Failed to run agent: {e}", file=sys.stderr)
    # Provide fallback or re-raise
    raise
```

### DON'T:

```python
try:
    agent = runner.get_agent("market-analyst", session_id=run_id)  # Magic string!
    response = agent.query(task)
except Exception:
    pass  # Silent failure - BAD!
```

---

## Testing Checklist

Before submitting changes:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Type hints present on new functions
- [ ] No magic strings (use `workflows/constants.py`)
- [ ] Error handling logs to stderr
- [ ] UI uses Candlelite theme (if applicable)
- [ ] Documentation updated
- [ ] Code follows existing patterns

---

## Resources

- **AGENTS.md** - General AI agent guide
- **CLAUDE.md** - Claude-specific guide
- **README.md** - Project overview
- **GETTING-STARTED.md** - Setup instructions
- **QUICK-REFERENCE.md** - All 68 specialists
- **docs/phase4.md** - Orchestration details
- **ROADMAP.md** - Future plans

---

## Support

For issues or questions:

1. Check existing documentation
2. Review test files for usage examples
3. Examine similar code in the codebase
4. Consult `pyproject.toml` for dependencies
