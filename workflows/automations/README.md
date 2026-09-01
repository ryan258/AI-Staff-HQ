# 🤖 Python Automations

This directory contains small Python examples designed by the **Automation Specialist**. The two top-level scripts are runnable examples; the `concepts/` subtree is illustrative prototype material and is not a production workflow.

## What These Are

The runnable examples execute locally in the project-managed Python environment. They demonstrate RSS parsing and authenticated HTTP request handling, but they do not provide a complete scheduling, persistence, or provider integration layer. They are working examples rather than complete scheduling, persistence, or provider-integration products.

## How to Run Them

Run any script from the project root with `uv`:

From the `ai-staff-hq/` project root, install the declared dependencies and run the scripts directly:

```bash
uv sync
uv run python workflows/automations/daily_news_summarizer.py <feed-url>
uv run python workflows/automations/social_media_trend_tracker.py <api-url> <api-key>
```

The conceptual example under `concepts/` is intentionally provider-agnostic and does not require the Gemini CLI; inspect it as a prototype rather than treating it as a verified external automation.

Some scripts need extra packages. Install them once with:

```bash
uv sync --extra scripts
```

Read the top of each script first to see what it does and which flags it takes.

## Ask the Automation Specialist for a New One

Describe the chore you want gone, and where to save the script. For example:

> "Automation Specialist, write a Python script that watches the `logs` folder. When a new `.md` file shows up, read it, write a one-sentence summary, and add that line to `summary.log`. Save it as `workflows/automations/log_summarizer.py`."
