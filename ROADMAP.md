# AI-Staff-HQ Roadmap

Updated: March 28, 2026
Planning Horizon: April 1, 2026 through March 31, 2027

## Direction

AI-Staff-HQ is no longer trying to be a broad "AI staff for everyone" toolkit first.

For the next 12 months, the primary goal is to turn this repository into a dependable personal second-brain workbench for Ryan. The flagship path is the planning swarm: a quality-first multi-agent workflow that takes a vague brief, chooses a small set of useful specialists, and returns one strong final deliverable.

The experimental lab remains important, but it is secondary. It should be preserved, documented, and available by opt-in. It should not shape the default experience until it proves its value through real use and evals.

## Product Thesis

By March 31, 2027, AI-Staff-HQ should feel like a practical operating system for creative and strategic work:

- It should accept vague briefs without needing perfect prompting.
- It should pull in relevant context from prior work, guides, and logs.
- It should produce a coherent final output, not just an interesting trace.
- It should leave behind semantic logs, reusable artifacts, and a searchable history.
- It should default to a small active roster and only widen scope when evidence supports it.

## What Great Looks Like

By the end of this roadmap, the default experience should be:

1. You give the system a rough brief.
2. The system loads the right project context and style guides.
3. The planning swarm creates a tight execution plan with sane delegation.
4. Specialists produce useful intermediate work only when needed.
5. Chief of Staff synthesizes a strong final deliverable.
6. The run is saved with semantic logs, searchable outputs, and enough metadata to reuse later.

## Rules For The Year

- The planning swarm stays the flagship.
- The active roster stays small by default.
- Experimental staff remain opt-in.
- Archived staff remain preserved, not deleted.
- No new specialist is promoted to active without a real eval reason.
- No major workflow is added without tests and an eval story.
- UI work follows the flagship workflow; it does not lead it.
- Logs, output artifacts, and naming must stay semantic and human-readable.

## Current Baseline

As of March 28, 2026:

- The active, experimental, and archived roster tiers exist.
- The flagship planning swarm is live.
- Real-brief capture and eval scaffolding exist.
- Semantic log naming exists for new runs, and the old backlog has been migrated.
- Dynamic CoS orchestration and Streamlit exist, but they are secondary.
- Phase 1 gaps: planner variance, parser brittleness, and thin real-brief coverage.
- Phase 2 gaps: weak memory and context loading, plus limited searchability across prior runs.
- Phase 3 gaps: limited artifact reuse and no consistent deliverable packaging.
- Phase 4 gaps: no durable review and continuity layer for work across days and weeks.

## Phase 1: Harden The Flagship

Window: April 1, 2026 through June 30, 2026

Goal: Make the planning swarm reliable enough that it becomes the default way to think through real work.

### Priority Work

- Replace naive JSON extraction in planning paths with stricter structured-output handling.
- Reduce planner variance so similar briefs produce similar task structures.
- Expand real-brief eval coverage with at least 10 recurring prompt types from actual use.
- Tighten capability matching and fallback behavior.
- Keep the active roster small and evidence-based.
- Ensure every flagship run persists a useful semantic log and a clear final output.

### Deliverables

- Structured planner contract for the flagship path.
- Real-brief eval suite with at least 10 cases.
- Stable active roster definition with documented promotion and demotion rules.
- Clear failure reporting for parse errors, fallback use, and synthesis failures.

### Exit Criteria

- The real-brief eval suite passes at a stable baseline.
- The flagship planner consistently produces defensible task breakdowns.
- Default output quality is high enough that it is worth using on real briefs first, not just tests.

## Phase 2: Build Context And Memory

Window: July 1, 2026 through September 30, 2026

Goal: Stop treating each run as isolated. Add one lightweight memory layer that reliably improves repeated work on the same projects.

### Priority Work

- Add project context manifests for recurring domains such as brands, story worlds, and active initiatives.
- Build a lightweight retrieval layer over approved local materials: guides, notes, prior outputs, and semantic logs.
- Normalize run metadata so history is queryable by project, workflow, specialist, and subject.
- Establish a reusable case library of past briefs, outputs, and preferred patterns.
- Introduce context-budget and de-duplication rules so retrieval helps more than it distracts.

### Deliverables

- A documented project context manifest format and loader.
- Retrieval support in the flagship planning flow for at least 3 recurring project types.
- Searchable run history with normalized project and subject metadata.
- Clear rules for what context is injected automatically versus manually.
- A small case library that can be reused during planning and synthesis.

### Exit Criteria

- The planning swarm can pull in relevant project context without manual copy/paste.
- Repeated work in the same domain feels faster and more grounded.
- Past outputs can be found and reused without digging through raw logs.

## Phase 3: Move From Plans To Deliverables

Window: October 1, 2026 through December 31, 2026

Goal: The system should stop ending at "here is a plan" for everything. For core use cases, it should produce complete work packages.

### Priority Work

- Turn flagship outputs into reusable deliverable bundles.
- Support common personal use cases with stronger end artifacts:
  creative development, brand writing, strategic planning, content packaging, and technical scoping.
- Add review and approval gates where they improve quality.
- Formalize output schemas for core deliverable types.
- Improve synthesis so final outputs feel authored, not merely concatenated.

### Deliverables

- At least 3 high-value output package types.
- Reusable artifact structure per run, not just a final text blob.
- Better final synthesis prompts and review heuristics.
- Tests and evals covering output-package integrity.

### Exit Criteria

- The system regularly produces usable final artifacts, not just promising drafts.
- The best workflows save time on real projects rather than only demonstrating orchestration.

## Phase 4: Personal Operating System

Window: January 1, 2027 through March 31, 2027

Goal: Turn AI-Staff-HQ into a dependable day-to-day workbench for continuity, review, and next-step recovery.

### Priority Work

- Add one dependable review loop for daily and weekly planning.
- Connect planning runs to next actions, active projects, and backlog review.
- Add a lightweight continuity surface for current focus, recent outputs, and open threads.
- Refine the Chief of Staff role around continuity and memory, not just delegation.
- Define which experimental workflows are ready to graduate and which should remain lab-only.

### Deliverables

- A stable daily review workflow and a stable weekly review workflow.
- A clear project-overview surface, still CLI-first with secondary UI support if warranted.
- A documented graduation path for experimental specialists and workflows.
- A stable internal version of AI-Staff-HQ that can be treated as the default personal workbench.

### Exit Criteria

- The system is useful across days and weeks, not just single prompts.
- Active work, recent outputs, and next steps are visible and recoverable.
- There is a clear distinction between stable workflows and experimental lab work.

## Experimental Track

The experimental track remains active all year, but it is explicitly constrained.

### Allowed

- Trying unusual specialist combinations.
- Running opt-in experimental staff.
- Building weird or narrow workflows for discovery.
- Testing alternate orchestration strategies behind flags.

### Not Allowed To Distort The Core

- Experimental work does not expand the default active roster automatically.
- Experimental work does not redefine the default UI.
- Experimental work does not ship as the recommended path without eval evidence.

## What We Will Not Prioritize

For this roadmap window, these are not primary goals:

- Broad public productization.
- Maximizing roster size.
- Building a large plugin ecosystem.
- Re-optimizing everything around lowest cost.
- Heavy UI investment before the flagship runtime and memory layers are stable.

## Metrics That Matter

The project should be judged by these outcomes, not by breadth alone:

- Real-brief eval pass rate.
- Final deliverable quality on recurring personal workflows.
- Delegation quality and fallback rate.
- Searchability and reuse of prior work.
- Time saved on repeated planning and writing tasks.
- Stability of the active roster.

## Definition Of Done For This Roadmap

This roadmap is complete when AI-Staff-HQ is the first place to bring a vague brief, because it reliably turns it into grounded, reusable work with context, continuity, and a strong final output.
