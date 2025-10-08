# 🤖 Python Automations

This directory contains executable Python scripts designed by the **Automation Specialist**. These scripts represent tangible, runnable workflows that can automate complex tasks within the project ecosystem.

## Purpose

Unlike abstract blueprints, these are functional Python workflows designed to be executed locally. They can perform tasks such as file monitoring, data processing, and interacting with APIs (including Gemini itself, conceptually).

This approach makes the AI-Staff-HQ system more self-contained and powerful, allowing the `Automation Specialist` to build solutions directly, rather than just designing them for others to implement on third-party platforms.

## Execution

These scripts can be run using the Gemini CLI. The user can inspect the code and then ask Gemini to execute it.

**Example Use Case:**
> "Automation Specialist, I need a Python workflow that monitors the `logs` directory. When a new `.md` file is added, the script should read the content, generate a one-sentence summary, and append it to a central `summary.log` file. Save the script as `workflows/automations/log_summarizer.py`."
