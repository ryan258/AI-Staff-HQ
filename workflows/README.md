# ⚡ Workflows Directory

> _Examples of step-by-step processes for complex projects and systematic execution with your AI workforce._

## 🔄 Workflow Examples

This directory contains examples of how to get your AI specialists to work together on bigger goals.

### ⭐ **Flagship: The Planning Swarm**

This is the main way to use the system. Give it a rough idea and it builds a plan, picks the right helpers, and returns one strong result.

```bash
uv run workflows/planning_swarm.py "Turn my newsletter into a small paid product"
```

Helpful flags: `--model`, `--temperature`, `--experimental`, `--max-parallel`, `--verbose`, `--stream`, `--no-auto-approve`.

Check plan quality at any time with the evals:

```bash
uv run workflows/planning_swarm_eval.py
```

### 🧩 **Graph Workflows (Step-by-Step)**

These run a fixed set of helpers in order. Good when you know exactly which steps you want.

These two take your topic right on the command line:

- `uv run workflows/graphs/strategy_tech_handoff.py "New product idea" --auto-approve` — Market analysis → technical plan → executive brief.
- `uv run workflows/graphs/strategic_planning.py "Topic"` — Market analysis → creative strategy → executive brief.

These two are built as importable functions with a built-in demo (running the file directly just runs the demo). Call them from your own script:

```python
from workflows.graphs.cos_orchestration import run_cos_orchestration
run_cos_orchestration("Create a 3-agent marketing team plan", auto_approve=True)

from workflows.graphs.code_feature import run_code_feature
run_code_feature("Add CSV export to the dashboard", auto_approve=True)
```

### 🤖 **Python Automations**

_Executable Python scripts for automating complex tasks and workflows._

- **[Aether Brew Launch](automations/aether_brew_launch.py)** ✅ _New (v1.5.0)_ - A script to automate the launch of the Aether Brew brand.
- **[Daily News Summarizer](automations/daily_news_summarizer.py)** ✅ _New (v1.5.0)_ - A script that fetches the latest news from an RSS feed and generates a summary.
- **[Social Media Trend Tracker](automations/social_media_trend_tracker.py)** ✅ _New (v1.5.0)_ - A script that uses a public API to track trending topics.

### 🎯 **Project Type Workflows**

_Examples of specialized processes for specific project categories using multi-department coordination._

- **[Brand Development Workflow](project-types/brand-development-workflow.md)** ✅ _Complete_ - A complete brand creation process using the core Strategy and Creative specialists.
- **[Content Creation Pipeline](automation/content-creation-pipeline.md)** ✅ _Complete_ - A systematic, end-to-end workflow for producing high-quality content.

### ⚡ **Simple Workflows**

_Lightweight processes that rely on a single specialist for rapid execution._

- **[Single Blog Post](simple/single-blog-post.md)** ✅ _New_ — Fast copy production using only the Copywriter specialist.

---

## 🚀 Workflow Development with Your AI Workforce

### **Creation Principles for Multi-Specialist Coordination**

1. **Start with a strategic outcome** - Define the clear success criteria for your workflow.
2. **Map your specialist capabilities** - Identify the optimal combination of your custom specialists for the desired results.
3. **Design coordination protocols** - Create seamless handoffs between your specialists.
4. **Build in quality assurance** - Integrate review cycles for consistent excellence.
5. **Test and optimize** - Validate your workflows with real projects and improve them over time.

### **Building Your Own Workflows**

You are encouraged to build your own workflows for your recurring tasks. Use the `Chief of Staff` to help you design and orchestrate your custom workflows.
