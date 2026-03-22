# Getting Started with AI-Staff-HQ

# How to Use Your AI Helpers

This is the main instruction manual for using your AI team. Just follow these simple steps to get the best answers.

## 1. The Main Steps (Do This First)

Whenever you have a job to do, follow these exact steps:

1.  **Pick Your Helper:** Look at what you need to do. Do you need a planner (Strategy), an artist (Creative), or a computer person (Tech)? Pick **ONE** helper from the `staff/README.md` list.
2.  **Copy the Rules:** Open that helper's `.yaml` file and copy everything inside it.
3.  **Paste It:** Paste all those rules into your chat box.
4.  **Give the Command:** Type this exact sentence into the chat:
    `Acting as the [Helper's Name] from my AI-Staff-HQ, [tell them what you need them to do].`

**Example:**

> "Acting as the Copywriter from my AI-Staff-HQ, write a subject line for tomorrow's email."

## 2. Team Projects (Using the Chief of Staff)

Use this **ONLY** if your job needs more than one helper (like "Plan a big sale," which needs planners and artists).

1.  **Copy the Rules:** Copy all the text from `staff/strategy/chief-of-staff.yaml`.
2.  **Give the Command:** Type: `Acting as the Chief of Staff, [explain your big project].`
3.  **Follow Directions:** The Chief of Staff will tell you which other helpers to talk to. Do what they say!

## 3. Making New Helpers

If you need a helper that isn't on the list yet:

1.  **Copy the Blank Form:** Find the file `templates/persona/new-staff-member-template.md`. Make a copy of it and put it in the right folder inside `staff/`.
2.  **Name It:** Give your new file a name like `[helper-name].yaml`.
3.  **Add Details:** Type in the helper's `role` (what they do), `skills` (what they are good at), and `motto` (their catchphrase).
4.  **Check Your Work:** Run this command to make sure you didn't break anything: `uv run tools/validate_specialist.py staff/[dept]/[name].yaml`

## 4. Using the Web Dashboard

If you want colorful buttons and a nice screen instead of typing code:

1.  **Download Needs:** Type `uv sync --extra ui`
2.  **Start the Dashboard:** Type `uv run streamlit run ui/app.py`
3.  **Use the Screen:**
    - **Workflows:** Start big projects like `Strategy-Tech Handoff`.
    - **Chat:** Talk to your helpers right on the screen.
    - **Logs:** Read your old chats to see what happened.

---

**Quick Check:**

- If you are stuck thinking, "Which helper should I pick?", open the `docs/QUICK-REFERENCE.md` file.
- If you are stuck thinking, "What do I do next?", go back to Step 1 at the top of this page!
