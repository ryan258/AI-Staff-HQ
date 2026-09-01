# 🚀 The CLI Workflow: Your AI Workforce on the Command Line

This guide is for people who like to work in the terminal. It shows two ways to run your specialists from the command line.

## 🎯 Two Ways to Run Specialists

1. **The built-in CLI (recommended).** This project ships with its own command, `tools/activate.py`. It loads a specialist, keeps the conversation, and saves your session. No extra tools needed.
2. **An outside coding assistant.** You can also paste a specialist's instructions into a tool like the Gemini CLI, OpenAI's Codex, or Claude Code. This is handy when you are already coding in one of those.

Most of the time, start with the built-in CLI.

## 🗺️ Using the Built-in CLI

Run everything from the project root (the folder that holds `tools/` and `staff/`).

### Talk to one specialist

```bash
uv run tools/activate.py copywriter
```

This opens a chat with the Copywriter. Type `exit` to leave, or `/clear` to start fresh.

### Ask one question and get one answer

```bash
uv run tools/activate.py market-analyst -q "Who are the top 3 competitors for a paid newsletter?"
```

### See the whole team

```bash
uv run tools/activate.py --list
```

### Run the planning swarm on a big idea

```bash
uv run workflows/planning_swarm.py "Turn my newsletter into a small paid product"
```

The swarm picks the right helpers, splits the work, and returns one strong result.

## 🛠️ Using an Outside Coding Assistant

If you would rather use a tool like the Gemini CLI, OpenAI's Codex, or Claude Code, you can feed a specialist's role into it with the same `Acting as the [ROLE]...` pattern. Pass your files as context.

For example, to have the Prompt Engineer review a script:

```bash
cat my-script.py | gemini "Act as the Prompt Engineer from my AI-Staff-HQ. Review this Python script and suggest improvements."
```

## 🔗 Chaining Specialists

The real power of the command line is connecting steps. You can pipe one specialist's output into the next, or write a short shell script that:

1. Uses the **Market Analyst** to research a topic.
2. Passes that research to the **Copywriter** to write a blog post.
3. Passes the blog post to the **SEO Specialist** to tune it for search.

For a hands-off version of this, the planning swarm does the chaining for you.

## 🌟 Why Use the CLI

- **Speed:** One command, one answer. No clicking around.
- **Automation:** Wrap your common tasks in shell scripts.
- **Integration:** Plug your specialists into the tools you already use.

This workflow fits developers and anyone who likes to keep their hands on the keyboard.
