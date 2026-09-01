# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-09-01 Remediation Follow-up

### Fixed

- **Private interaction logs:** Logging is opt-in by default. When enabled, prompts, responses, semantic filenames, and structured state are redacted before persistence and written atomically with `0600` files under `0700` directories.
- **Session persistence:** Session listing is contained and identifier-validated; corrupt or identity-mismatched sessions raise explicit load errors instead of being treated as new sessions; per-session locking and append merging preserve concurrent messages.
- **Swarm budget enforcement:** A per-run ledger reserves prompt and completion capacity before every provider attempt, passes the remaining completion cap to the provider, counts failed/retry/fallback attempts, stops synthesis when exhausted, and reports the ledger totals through `SwarmMetrics`.
- **Approval and terminal status:** Configured approval uses the inherited handler/interactive path, while `auto_approve=false` does not create an implicit gate. `BLOCKED`, `FAILED`, and `COMPLETED` states are preserved in the graph and top-level log, and task streaming events match the actual outcome.
- **Planning and providers:** Unsafe task/dependency identifiers and malformed planning structures fail before graph construction. Anthropic-only configuration is rejected explicitly because the current factory implements OpenRouter/OpenAI only; prior routing-precedence coverage is restored.
- **GraphRunner durability:** A successful graph now fails visibly when its run log cannot be persisted, while an existing graph failure remains the primary error and records the secondary logging failure. Interrupts are preserved, invalid non-mapping graph results fail explicitly, and secondary logging diagnostics cannot mask either condition.
- **Automation dependencies:** The runnable RSS and HTTP examples declare `feedparser` and `requests` in project metadata and are covered by import/compile integrity tests.

### Changed

- **Morphling trust boundary:** Shell execution is disabled by default. Allowlist mode uses `shell=False`, read-oriented commands, root/symlink checks, and metacharacter rejection. Broad owner mode requires both `MORPHLING_OWNER_MODE=true` and `MORPHLING_UNRESTRICTED_ROOT=true` and is documented as owner-only.
- **Planning CLI:** `workflows/planning_swarm.py` now exposes `--budget`, `--require-approval`, and `--no-auto-approve` controls that map to the enforced runtime policy.
- **Planning evals:** Malformed model output is represented as an explicit parse failure with zero tasks/waves instead of silently creating a generic task.
- **Automation documentation:** Runnable examples now use the project-managed `uv` environment; conceptual examples are clearly labeled as prototypes.

### Added

- Added direct regression coverage for sensitive-log redaction and permissions, malformed/corrupt/concurrent sessions, capability and symlink boundaries, budget reservation and exhaustion, approval handlers, blocked/failed stream events, strict task parsing, provider routing, and planning-eval failure reporting.

### Verification

- `uv run pytest -q`: `108 passed`.
- Nested changed Python compilation and `git diff --check` pass. Root integration tests and the consolidated finding-by-finding record are maintained in `../docs/archive/20260831-PLAN.md`.

Live provider calls, authenticated integrations, and broad Morphling owner mode were not exercised in this remediation pass.

## [2.2.0] - 2026-01-22
### Added
- **Swarm Orchestration:** `bin/dhp-swarm.py` for parallel execution with streaming output and verbose logging.
- **LangGraph Orchestration:** `orchestrator/graph_runner.py` and `workflows/graphs/strategy_tech_handoff.py`.
- **Streamlit UI:** `ui/app.py` for launching graphs and reviewing inline logs.
- **Extended Roster:** Documented 68 specialists total (41 core + 27 extended) across 7 departments.

### Changed
- **Documentation:** Updated counts, commands, output paths, and model routing defaults across AI-Staff-HQ docs.
- **Model Routing:** Documented per-role model variables with optional brand override.

## [2.1.0] - 2025-12-18
### Added
- **Local Validation Tooling:** A CLI linter (`tools/validate_specialist.py`) to validate specialist YAML structure.
- **Package Management:** Adopted `uv` for dependency management.
- **Documentation:** New `prompt_analysis.md` artifact analyzing project prompting strategy.

### Changed
- **Directory Structure:** Consolidated `staff/technical` into `staff/tech` and `staff/creative` into `staff/producers`.
- **Documentation:** Updated all counts and paths in `README.md`, `staff/README.md`, and `docs/QUICK-REFERENCE.md`.
- **Specialist Schema:** Standardized quoting for mottos and descriptions in YAML files.
- **Cognitive Accessibility:** Rewrote `GETTING-STARTED.md` from multi-path learning framework to unambiguous standard operating procedure.
- **Personal Documentation:** Shifted `README.md` framing from "your workforce" to "MY workforce" - personal infrastructure focus.
- **Quick Reference:** Reframed "Common Mistakes" as "Rules of Engagement" in `docs/QUICK-REFERENCE.md`.
- **Phase 2 Complete - Workflow Mastery:**
  - Deep dive sections completed for all core 41 specialists with comprehensive deliverables, knowledge areas, and workflows
  - Added inter-specialist workflow documentation: `strategy-tech-handoff.md` and `content-optimization-loop.md`

### Removed
- **Community Platform:** Removed "Community Contribution Platform" from roadmap to focus on local tooling.
- **Legacy Directories:** Deleted `staff/technical` and `staff/creative` folders.
- **Placeholder:** Removed empty `main.py`.

## [2.0.0] - 2025-10-01
### Added
- **Core Team:** Added 5 essential specialists as foundational examples.
- **Templates:** "Bring Your Own Staff" templates for creating new specialists.

### Changed
- **Framework Refactor:** Major refactor to "Lean and Extensible" architecture.
- **Documentation:** Streamlined all documentation for v2.0.0 launch.
