# Getting Started with AI-Staff-HQ

Welcome—this guide gives you three entry ramps into the repository plus quick links to examples that match common jobs-to-be-done. Pick the track that fits your learning style, then expand using the mastery progression.

## Choose Your Path

### 🚀 Quick Start (15 minutes)
For hands-on learners who want a win immediately.
1. **Clone or download the repo.** Load the project into your AI workspace so specialists are in context.
2. **Activate one of the Essential 5 specialists.** Try `"Acting as the Art Director from my AI-Staff-HQ, create a hero image concept for our onboarding email."`
3. **Reference a finished specialist.** Skim `examples/specialists/completed-copywriter.yaml` to see how activation patterns are structured.
4. **Log the result.** Capture what worked in `knowledge-base/` so you can reuse the prompt later.

### 📖 Systematic Learner (1 hour)
For operators who want to understand the philosophy before executing.
1. **Read the framing:** `README.md` → [PHILOSOPHY.md](PHILOSOPHY.md).
2. **Study one example specialist + notes:** `examples/specialists/completed-brand-strategist.yaml` and `examples/specialists/notes-on-creation.md`.
3. **Walk through a project brief:** `examples/project-briefs/simple-blog-post-brief.md` shows selective template usage.
4. **Shadow the workflow transcript:** Follow `examples/workflows/blog-post-execution-transcript.md` prompt-by-prompt.
5. **Run a lightweight replay:** Activate the Chief of Staff to coordinate two specialists using the same brief.

### 🏗️ Builder (2–4 hours)
For builders ready to craft their own workforce.
1. **Fork the repository** so you can customize.
2. **Design your first custom specialist:** copy `templates/persona/new-staff-member-template.md` and use the Prompt Engineer to fill it out.
3. **Create a structured project brief:** adapt `examples/project-briefs/brand-launch-brief.md` for your own initiative.
4. **Execute with orchestration:** replicate the handoffs in `examples/workflows/brand-development-execution-transcript.md`.
5. **Measure + iterate:** borrow patterns from `examples/before-after/roi-analysis.md` to quantify the impact of your workflow.

## Learning Paths by Use Case
- **Content Marketing:** Start with `examples/project-briefs/simple-blog-post-brief.md`, then follow `examples/workflows/blog-post-execution-transcript.md`, and reuse assets from `examples/specialists/completed-copywriter.yaml`.
- **Brand Launch:** Review `examples/project-briefs/brand-launch-brief.md`, study the before/after comparison in `examples/before-after/prompt-vs-workflow-comparison.md`, then run `examples/workflows/brand-development-execution-transcript.md`.
- **Analytics & Optimization:** Pair `examples/specialists/completed-data-analyst.yaml` with the ROI framework in `examples/before-after/roi-analysis.md`, and route insights through the Chief of Staff for cross-team action.
- **Template Customization:** Start with `templates/project/project-brief-simple.md` for quick wins, or expand into `templates/project/project-brief-comprehensive.md` alongside the insights in `examples/specialists/notes-on-creation.md` to craft domain-specific processes.

## The Mastery Progression
A condensed version of the path from `R2N.md`—use it to gauge your next milestone.
- **Level 1 · Practitioner:** Execute single tasks with the five core specialists until activation prompts feel natural.
- **Level 2 · Creator:** Build one custom specialist using the persona template and document activation patterns.
- **Level 3 · Orchestrator:** Run a departmental project with the Chief of Staff coordinating 2–3 specialists.
- **Level 4 · Commander:** Deliver a cross-department initiative using the Project Brief templates (simple or comprehensive) and explicit handoffs.
- **Level 5 · Architect:** Invent your own workflow, measure ROI, and feed improvements back into specialists, briefs, and transcripts.

## Platform-Specific Notes
- **Gemini / Google AI Studio:** Load the repository, then issue activation prompts exactly as written—Gemini handles long YAML prompts well but benefits from the context discipline noted in `PHILOSOPHY.md`.
- **OpenAI Assistants / ChatGPT:** Attach only the files you need for the task (specialist YAML + relevant brief) to stay within token limits; lean on the Chief of Staff for sequencing.
- **Local Models:** Prune files you do not need before loading; the modular folder structure exists to keep context windows lean.
- **Automation Hooks:** When using API-based runners, script the workflow order defined in the transcripts so prompts/outputs stay deterministic.

---
Use this guide as the launchpad, then keep iterating: capture what works in `knowledge-base/`, refine specialists in `staff/`, and contribute back via `examples/` when you harden new patterns.
