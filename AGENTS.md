# AI Agents Guide for AI-Staff-HQ

This guide provides instructions for AI assistants working with the AI-Staff-HQ project.

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

### Usage Examples

**Background and Text:**
```css
body {
  background-color: var(--bg-color);
  color: var(--text-color);
}
```

**Buttons and Accents:**
```css
.btn-primary {
  background-color: var(--accent-primary);
  color: var(--bg-color);
  border: 1px solid var(--accent-primary);
}

.btn-success {
  background-color: var(--accent-success);
  color: var(--bg-color);
}

.btn-danger {
  background-color: var(--accent-danger);
  color: var(--bg-color);
}
```

**Borders and Dividers:**
```css
.card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
}

hr {
  border-color: var(--border-color);
}
```

---

## Project Structure

AI-Staff-HQ is organized as follows:

- **staff/** - 68 specialist YAML definitions organized by department
- **tools/** - Core Python engine for activating specialists
- **workflows/** - Multi-agent orchestration workflows
- **orchestrator/** - LangGraph-based workflow execution
- **ui/** - Streamlit dashboard interface
- **tests/** - Test suite
- **docs/** - Documentation

## Working with Specialists

Specialists are defined in YAML files under `staff/`. Each specialist has:
- Metadata (name, role, department)
- Expertise areas
- Collaboration patterns
- Activation triggers

When creating or modifying UI for specialist interaction, ensure you use the Candlelite theme colors.

## Development Guidelines

1. **Type Safety**: Use Pydantic for all configuration and data models
2. **Testing**: All new features require tests
3. **Documentation**: Update relevant docs when adding features
4. **Code Style**: Follow existing patterns; use type hints
5. **UI Design**: ALWAYS use Candlelite theme for all visual interfaces

## Common Tasks

### Adding a New Specialist
1. Create YAML file in appropriate `staff/[department]/` directory
2. Follow the template structure from existing specialists
3. Test with `python tools/validate_specialist.py staff/[department]/[slug].yaml`

### Creating a Workflow
1. Use LangGraph for multi-agent workflows
2. Import constants from `workflows/constants.py` (no magic strings)
3. Add to `ui/app.py` for Streamlit dashboard access
4. If the workflow has a UI component, apply Candlelite theme

### Updating UI
When modifying `ui/app.py` or any visual interface:
1. Import and use the Candlelite color palette
2. Use CSS variables for maintainability
3. Ensure contrast meets accessibility standards
4. Test in both light and dark environments (theme is optimized for dark)

---

## API Keys and Configuration

The project supports multiple LLM providers via OpenRouter. See `.env.example` for configuration.

## Questions?

Refer to:
- **README.md** - Project overview
- **GETTING-STARTED.md** - Setup instructions
- **QUICK-REFERENCE.md** - Full 68 specialist directory
- **docs/phase4.md** - Orchestration documentation
