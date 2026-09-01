# 🤖 Python Automations

This directory contains small Python examples designed by the **Automation Specialist**. The two top-level scripts are runnable examples; the `concepts/` subtree is illustrative prototype material and is not a production workflow.

## Purpose

The runnable examples execute locally in the project-managed Python environment. They demonstrate RSS parsing and authenticated HTTP request handling, but they do not provide a complete scheduling, persistence, or provider integration layer.

This approach makes the AI-Staff-HQ system more self-contained and powerful, allowing the `Automation Specialist` to build solutions directly, rather than just designing them for others to implement on third-party platforms.

## Execution

From the `ai-staff-hq/` project root, install the declared dependencies and run the scripts directly:

```bash
uv sync
uv run python workflows/automations/daily_news_summarizer.py <feed-url>
uv run python workflows/automations/social_media_trend_tracker.py <api-url> <api-key>
```

The conceptual example under `concepts/` is intentionally provider-agnostic and does not require the Gemini CLI; inspect it as a prototype rather than treating it as a verified external automation.

**Example Use Case:**
> "Automation Specialist, I need a Python workflow that monitors the `logs` directory. When a new `.md` file is added, the script should read the content, generate a one-sentence summary, and append it to a central `summary.log` file. Save the script as `workflows/automations/log_summarizer.py`."
