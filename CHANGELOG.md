# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Flagship Planning Swarm:** Added `workflows/planning_swarm.py` as the quality-first orchestration path for turning vague briefs into structured final outputs.
- **Roster Tiering:** Added `config/specialist_roster.yaml` and `tools/engine/roster.py` to support active, experimental, and archived specialist tiers.
- **Planning Evals:** Added deterministic planning evals via `workflows/planning_swarm_eval.py`, `evals/planning_swarm_cases.yaml`, and real-brief capture via `workflows/planning_swarm_capture.py` and `evals/planning_swarm_real_briefs.yaml`.
- **Semantic Log Migration Tooling:** Added `tools/migrate_legacy_logs.py` to rename legacy timestamp-only logs to semantic names.
- **Regression Coverage:** Added test coverage for roster tiers, planning evals, capture flow, semantic log migration, swarm config defaults, and theme semantics.

### Changed
- **Flagship Focus:** Reframed the project around a personal second-brain workbench with the planning swarm as the primary path.
- **Default Specialist Surface:** Default orchestration now uses the active roster by default, with experimental staff preserved as opt-in and archived staff preserved for reference.
- **Logging:** Graph logs and markdown interaction logs now use semantic filenames derived from workflow, specialist, and prompt/brief subjects; legacy logs were migrated to the new scheme.
- **Dynamic CoS Parity:** `workflows/graphs/cos_orchestration.py` can now opt into experimental specialists, matching planning swarm behavior.
- **Roadmap:** Replaced the old roadmap with a new April 2026 to March 2027 plan centered on flagship reliability, memory/context, deliverables, and personal operating-system workflows.
- **Documentation:** Updated orchestration, eval, roster, and roadmap docs to reflect the current flagship-first architecture and semantic logging behavior.

### Fixed
- **Model Routing Clarity:** Set `config/model_routing.yaml` budget mode to `enabled: false` when no budget model is configured.
- **SwarmConfig Defaults:** `SwarmConfig.roster_tiers` now defaults directly to `["active"]` rather than relying on mutation during validation.
- **Theme Semantics:** Restored visual distinction between warning and accent styling in `ui/theme.py` and added explicit Streamlit warning styling.
- **Log Subject Extraction:** Improved semantic naming heuristics so migrated and new logs use meaningful subjects from briefs and task prompts instead of generic coordinator boilerplate.

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
