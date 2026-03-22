# Final Launch To-Do List

Use this simple list to finish the last few chores before showing AI-Staff-HQ to the whole world!

## 1. Setting Up GitHub (Priority 5.1)
- Click **Settings → General** on the GitHub page.
- Change the description to:  
  `My personal AI system showing how to build an AI team from scratch. This isn't software—it's a whole new way to think.`
- Add these search tags:  
  `ai-workflows`, `prompt-engineering`, `personal-knowledge-management`, `ai-orchestration`, `cognitive-infrastructure`, `llm-workflows`, `ai-productivity`, `systematic-thinking`.

## 2. Publish & Share (Priority 5.3)
- Post the article named `meta/articles/ai-staff-hq-launch.md` on your blog or LinkedIn.
- Put the three square pictures from `meta/assets/` on your social media sites.
- After you post them, put a check mark next to “Shared on social media” in the `polish.md` file.

## 3. Checking for Mistakes (Priority 5.4)
Run these commands in your terminal to make sure you didn't break any links or misspell anything:
- **Link check:** `npx markdown-link-check README.md`
- **Spell check:** `npx cspell "README.md" "docs/**/*.md" "meta/**/*.md" "polish.md"`
- **Code validation:** Run this to make sure your yaml files aren't broken:  
  `python -c "import yaml, pathlib; [yaml.safe_load(p.read_text()) for p in pathlib.Path('.').rglob('*.yaml')]"`
- Make sure to check the boxes in `polish.md` when you finish!

## 4. Save and Upload
- Check your git status (`git status`).
- Save your work, send it to the internet, and add a shiny version sticker (`git tag v2.0.0 && git push --tags`).

Keep this list where you can see it so you don’t forget anything important! You can copy it again the next time you launch a huge update.
