# Final Launch Checklist

Use this list to complete the remaining Priority 5 tasks before announcing AI-Staff-HQ publicly.

## 1. Repository Metadata (Priority 5.1)
- Open **Settings → General** in GitHub.
- Set the description to  
  `Personal AI operating system demonstrating systematic AI workforce orchestration. Cognitive infrastructure as code—not a product, but a paradigm.`
- Add topics:  
  `ai-workflows`, `prompt-engineering`, `personal-knowledge-management`, `ai-orchestration`, `cognitive-infrastructure`, `llm-workflows`, `ai-productivity`, `systematic-thinking`.

## 2. Publish & Share (Priority 5.3)
- Publish `meta/articles/ai-staff-hq-launch.md` on your blog, Dev.to, or LinkedIn.
- Share the three 1080×1080 assets from `meta/assets/` across your social channels.
- After posting, check off “Shared on social media” in `polish.md`.

## 3. Quality Assurance (Priority 5.4)
Run these commands (from repository root) once network access is available:
- **Link check:** `npx markdown-link-check README.md` (and optionally other docs).
- **Spell check:** `npx cspell "README.md" "docs/**/*.md" "meta/**/*.md" "polish.md"` adding domain-specific words to the config if needed.
- **YAML validation:** After installing PyYAML (`pip install pyyaml`), run  
  `python -c "import yaml, pathlib; [yaml.safe_load(p.read_text()) for p in pathlib.Path('.').rglob('*.yaml')]"`.
- Confirm code blocks render correctly (spot-check key docs).
- Mark the corresponding boxes in `polish.md` when finished.

## 4. Commit & Tag
- Ensure the working tree is clean (`git status`).
- Commit the final changes, push to origin, and tag the release if desired (e.g., `git tag v2.0.0 && git push --tags`).

Keeping this checklist visible ensures you don’t forget the public-facing tasks before announcing the launch.  
Duplicate or adapt it when you evolve the system for future releases.
