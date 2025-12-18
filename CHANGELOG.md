# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.0] - 2025-12-18
### Added
- **Local Validation Tooling:** A CLI linter (`tools/validate_specialist.py`) to validate specialist YAML structure.
- **Package Management:** Adopted `uv` for dependency management.
- **Documentation:** New `prompt_analysis.md` artifact analyzing project prompting strategy.

### Changed
- **Directory Structure:** Consolidated `staff/technical` into `staff/tech` and `staff/creative` into `staff/producers`.
- **Documentation:** Updated all counts and paths in `README.md`, `staff/README.md`, and `docs/QUICK-REFERENCE.md`.
- **Specialist Schema:** Standardized quoting for mottos and descriptions in YAML files.

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
