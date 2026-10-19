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
3. Test with `uv run tools/validate_specialist.py staff/[department]/[slug].yaml`

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

The project routes all models through OpenRouter (direct OpenAI keys also work). See `.env.example` for settings and `MODEL_CONTROL.md` for routing, fallback chains, and current model IDs.

- Model IDs go stale, free ones especially. Verify against `https://openrouter.ai/api/v1/models` before writing one into config or docs.
- Every call carries a timeout, retries, and the `fallback_models` chain from `config/model_routing.yaml`; keep new LLM clients on `ModelRouter.create_llm` so they inherit all three.
- Tool-using agents use `langchain.agents.create_agent` (LangGraph v1).

## Questions?

Refer to:
- **README.md** - Project overview
- **GETTING-STARTED.md** - Setup instructions
- **docs/QUICK-REFERENCE.md** - Full 68 specialist directory
- **docs/phase4.md** - Orchestration documentation

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
