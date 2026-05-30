# 🤖 Python Automations

This folder holds ready-to-run Python scripts built by the **Automation Specialist**. Each one does a real job you can run on your own machine.

## What These Are

These are working scripts, not ideas on paper. They can watch folders, process data, call public APIs, and tie small tasks together. The goal is to let the Automation Specialist hand you a tool you can run right away, instead of a plan you have to build yourself.

## How to Run Them

Run any script from the project root with `uv`:

```bash
uv run workflows/automations/daily_news_summarizer.py
```

Some scripts need extra packages. Install them once with:

```bash
uv sync --extra scripts
```

Read the top of each script first to see what it does and which flags it takes.

## Ask the Automation Specialist for a New One

Describe the chore you want gone, and where to save the script. For example:

> "Automation Specialist, write a Python script that watches the `logs` folder. When a new `.md` file shows up, read it, write a one-sentence summary, and add that line to `summary.log`. Save it as `workflows/automations/log_summarizer.py`."
