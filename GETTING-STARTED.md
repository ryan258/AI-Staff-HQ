# Getting Started with AI-Staff-HQ

# How to Use Your AI Staff

This is the standard operating procedure for deploying your AI workforce. Follow this linear process to get results without ambiguity.

## 1. The Core Workflow (Do This First)

When you have a task, follow these exact steps:

1.  **Select the Specialist:** Look at your request. Does it need Strategy, Creative, or Tech? Pick **ONE** specialist from `staff/README.md`.
2.  **Load the Context:** Copy the entire content of that specialist's YAML file.
3.  **Paste into Chat:** Paste the YAML into your AI interface.
4.  **Activate:** Type exactly: `Acting as the [Specialist Name] from my AI-Staff-HQ, [your specific request].`

**Example:**
> "Acting as the Copywriter from my AI-Staff-HQ, write a subject line for tomorrow's email."

## 2. Advanced Coordination (Chief of Staff)

Use this **ONLY** if your task requires more than one specialist (e.g., "Plan a campaign" involves Strategy + Creative).

1.  **Load Context:** Copy `staff/strategy/chief-of-staff.yaml`.
2.  **Activate:** `Acting as the Chief of Staff, [your multi-part request].`
3.  **Execute:** The Chief of Staff will tell you which other specialists to load. Follow its instructions.

## 3. Creating New Specialists

If no existing specialist fits your need:

1.  **Copy Template:** Copy `templates/persona/new-staff-member-template.md` to the correct department folder in `staff/`.
2.  **Rename:** Change the filename to `[specialist-name].yaml`.
3.  **Define:** Fill in the `role`, `skills`, and `motto` fields.
4.  **Validate:** Run `uv run tools/validate_specialist.py` to check your work.

---

**Cognitive Check:**
- If you are thinking "Which specialist do I use?", check `docs/QUICK-REFERENCE.md`.
- If you are thinking "How do I do this?", come back to step 1 of this file.
