# Notes on Specialist Creation

These notes capture why each specialist was built the way it was, along with integration guidance discovered in live usage.

---

## Copywriter

- **Why this specialist exists:** Needed a dedicated owner for conversion messaging once the product scope outgrew ad-hoc prompts. Repeatedly found myself re-deriving voice/tone rules and re-justifying proof points. Formalizing the role stabilized launch copy quality.  
- **Design decisions:**  
  - Kept capabilities focused on narrative structure, conversion execution, and iteration loops. Resisted adding social copy/SEO depth to maintain a tight scope—those are delegated to future specialists.  
  - Activation patterns mirror real weekly routines: launch asset creation, optimization sprints, and tone calibration after brand updates. Calls out specific knowledge-base files so context stays traceable.  
  - Success metrics are behavior-based (iteration quality, cross-team clarity) rather than vanity word counts.  
- **Integration highlights:**  
  - Brand Strategist sets narrative guardrails before Copywriter executes—documented under `integration_notes` to prevent siloed messaging.  
  - Market Analyst partnership is essential; copy shifts are always backed by quantitative or qualitative evidence.  
  - Chief of Staff uses this specialist when coordinating multi-asset launches, ensuring version control on messaging.  
- **What changed after real use:** Added the microcopy activation example specifically for onboarding tests after the Product team requested reusable CTA variants. That nudged the capability set to include iterative optimization explicitly.

---

## Brand Strategist

- **Why this specialist exists:** Without a strategic owner, positioning drifted every time a new campaign spun up. Needed a role to hold the narrative plan, translate research into usable frameworks, and enforce consistency across specialists.  
- **Design decisions:**  
  - Core capabilities mirror the cadence of quarterly brand sprints: (1) positioning architecture, (2) narrative systems, (3) experience alignment, (4) equipping the rest of the AI workforce.  
  - Activation patterns map to actual requests raised during the AI-Staff-HQ public release prep—especially the narrative blueprint that fed Copywriter and Art Director simultaneously.  
  - Performance standards emphasize alignment and adoption metrics. Strategy only succeeds when other specialists pick it up quickly.  
- **Integration highlights:**  
  - Market Analyst partnership retains a dedicated bullet because the qualitative/quantitative handshake is what keeps positioning rooted in reality.  
  - Activation examples are grounded in files that already exist (`knowledge-base/research/operator-interviews.md`, journey maps) to make prompts reproducible.  
  - Chief of Staff coordination ensures broader governance—critical when multiple departments consume the narrative.  
- **What changed after real use:** Expanded the experience audit capability after discovering that our onboarding and support touchpoints drifted from the refreshed trust pillar. That experience also validated the need to spell out cross-functional recommendations in audit outputs.

---

## Data Analyst

- **Why this specialist exists:** As the launch motion ramped up, decision-making lagged because metric investigations were inconsistent. Needed a dedicated analyst to translate dashboards into action and keep every initiative tied to revenue or retention impact.  
- **Design decisions:**  
  - Capabilities emphasize diagnostics, opportunity sizing, experimentation, and reporting—the four buckets of analysis work I rely on weekly.  
  - Activation patterns explicitly reference how prompts flow from alerts (trend investigation), planning sessions (opportunity sizing), and experimentation cycles.  
  - Communication style intentionally stresses plain language: prior iterations produced analysis that was technically correct but hard to translate into prompts.  
- **Integration highlights:**  
  - Chief of Staff and Market Analyst collaborations top the list—one sets priorities, the other provides context.  
  - Success metrics skew toward responsiveness and adoption, mirroring the SLA expectations we agreed on during incident reviews.  
  - Automation Specialist mention ensures recurring dashboards aren’t one-off manual efforts.  
- **What changed after real use:** Added the “Operational Reporting” capability once we realized weekly KPI distributions were living in Notion and not optimized for prompt consumption. The activation examples now include context-window discipline to keep summaries lightweight enough for downstream specialists.
