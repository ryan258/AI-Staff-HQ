# Getting Started with AI-Staff-HQ

This is your step-by-step guide to using your AI team. There are two ways to work:

- **The fast way (CLI):** You have this project on your computer. You run helpers with one short command. Start here if you can.
- **The copy-paste way (web chat):** You don't have the project set up, or you like using a chat website like ChatGPT or Claude. You paste a helper's rules into the chat.

Pick the way that fits you. You can switch any time.

---

## Part A: The Fast Way (Run It On Your Computer)

### 1. Set Up Once

Install the tools:

```bash
uv sync
```

Add your API key:

```bash
cp .env.example .env
# Open .env and paste in your OPENROUTER_API_KEY
```

(Optional) Install the short `ai-staff` command so you don't have to type `uv run tools/activate.py` every time:

```bash
uv pip install -e .
```

### 2. Talk to One Helper

Start a chat with any helper. Use their short name (slug):

```bash
uv run tools/activate.py copywriter
# or, if you installed the project:
ai-staff copywriter
```

Want a quick, one-shot answer with no back-and-forth? Add `-q`:

```bash
uv run tools/activate.py market-analyst -q "What are the risks of a paid newsletter?"
```

Helpful flags:

- `--list` — show the helpers you can talk to.
- `--resume last` — pick up your last chat where you left off.
- `/exit` — type this inside a chat to close it.

### 3. Run the Flagship Planner

The **Planning Swarm** is the star of the show. Give it a rough idea and it turns that idea into a clear plan, using your active roster of 12 helpers:

```bash
uv run workflows/planning_swarm.py "Turn my newsletter into a small paid product"
```

### 4. Use the Web Dashboard (Optional)

Prefer buttons and a screen over typing commands?

```bash
uv sync --extra ui
uv run streamlit run ui/app.py
```

On the dashboard you can start workflows, chat with helpers, and read your past chats.

---

## Part B: The Copy-Paste Way (Use Any Chat Website)

Use this when you don't have the project installed, or you just like working in a chat tool.

### 1. Use One Helper

1. **Pick your helper.** Look at the [staff/README.md](staff/README.md) list and choose **one**.
2. **Copy the rules.** Open that helper's `.yaml` file and copy everything inside.
3. **Paste it** into your chat box.
4. **Give the command:**

   > "Acting as the [Helper's Name] from my AI-Staff-HQ, [tell them what you need]."

**Example:**

> "Acting as the Copywriter from my AI-Staff-HQ, write a subject line for tomorrow's email."

### 2. Run a Team Project

Use this only when a job needs more than one helper (like planning a big sale).

1. Copy all the text from `staff/strategy/chief-of-staff.yaml`.
2. Paste it in and say: "Acting as the Chief of Staff, [explain your big project]."
3. The Chief of Staff will tell you which other helpers to bring in. Follow those steps.

---

## Part C: Make a New Helper

Need a helper that isn't on the list yet?

1. **Copy the blank form.** Find `templates/persona/new-staff-member-template.md`, copy it, and put it in the right folder inside `staff/`.
2. **Name it** like `your-helper-name.yaml`.
3. **Fill in the details:** the `role` (what they do), their skills, and a `motto` (their catchphrase).
4. **Check your work:**

   ```bash
   uv run tools/validate_specialist.py staff/[dept]/your-helper-name.yaml
   ```

---

## Stuck?

- "Which helper should I pick?" → Open [docs/QUICK-REFERENCE.md](docs/QUICK-REFERENCE.md).
- "What do I do next?" → Go back to Part A, Step 2, and talk to one helper.
- "I want the big picture" → Read [README.md](README.md) and [PHILOSOPHY.md](PHILOSOPHY.md).
