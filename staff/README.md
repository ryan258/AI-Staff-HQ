# 👥 AI Staff Directory

> _Your AI workforce, sorted into 7 color-coded departments (a nod to Magic: The Gathering colors)._

## How the Team Is Organized

You have **68 helpers** in total, split into three tiers:

- ⭐ **Active roster (12):** The default team. These run automatically and power the flagship planning swarm. The list lives in `config/specialist_roster.yaml`.
- 🧪 **Experimental (56):** Kept for niche or special jobs. They still work, but you turn them on yourself with `--tier experimental` or the `--experimental` flag.
- 🗄️ **Archived:** A handful of the weakest or most redundant roles, kept inside the experimental set for reference only.

See the whole team on the command line:

```bash
uv run tools/activate.py --list                       # active roster
uv run tools/activate.py --list --tier experimental   # experimental
uv run tools/activate.py --list --tier all            # everyone
```

---

## ⭐ Active Roster (12)

| Helper | Department |
|--------|------------|
| [Chief of Staff](strategy/chief-of-staff.yaml) | Strategy |
| [Market Analyst](strategy/market-analyst.yaml) | Strategy |
| [Creative Strategist](strategy/creative-strategist.yaml) | Strategy |
| [Brand Builder](strategy/brand-builder.yaml) | Strategy |
| [Data Analyst](strategy/data-analyst.yaml) | Strategy |
| [Academic Researcher](strategy/academic-researcher.yaml) | Strategy |
| [Scenario Planner](strategy/scenario-planner.yaml) | Strategy |
| [Copywriter](producers/copywriter.yaml) | Producers |
| [Software Architect](tech/software-architect.yaml) | Tech |
| [Automation Specialist](tech/automation-specialist.yaml) | Tech |
| [Productivity Architect](tech/productivity-architect.yaml) | Tech |
| [Quality Control Specialist](tech/quality-control-specialist.yaml) | Tech |

---

## 📂 Full Directory by Department

A ⭐ means the helper is on the active roster. Everything else is experimental (opt-in).

### 🟦 Strategy (13) — Planning & Insights
**Path:** `staff/strategy/`

- ⭐ [Chief of Staff](strategy/chief-of-staff.yaml) — Leads projects and coordinates the team.
- ⭐ [Market Analyst](strategy/market-analyst.yaml) — Market research and competition.
- ⭐ [Creative Strategist](strategy/creative-strategist.yaml) — Big ideas and campaign concepts.
- ⭐ [Brand Builder](strategy/brand-builder.yaml) — Brand identity and messaging.
- ⭐ [Data Analyst](strategy/data-analyst.yaml) — Reads numbers and finds patterns.
- ⭐ [Academic Researcher](strategy/academic-researcher.yaml) — Deep, fact-checked research.
- ⭐ [Scenario Planner](strategy/scenario-planner.yaml) — "What if" paths and risk maps.
- 🧪 [Trend Forecaster](strategy/trend-forecaster.yaml) — Spots what's coming next.
- 🧪 [Learning Scientist](strategy/learning-scientist.yaml) — How people learn best.
- 🧪 [Ethicist](strategy/ethicist.yaml) — Right-and-wrong questions.
- 🧪 [Alchemist](strategy/alchemist.yaml) — Mixes unrelated ideas together.
- 🧪 [Cartographer Invisible](strategy/cartographer-invisible.yaml) — Maps what others miss.
- 🧪 [Etymologist Decay](strategy/etymologist-decay.yaml) — How words and meanings shift.

### 🟥 Producers (15) — Creative & Production
**Path:** `staff/producers/`

- ⭐ [Copywriter](producers/copywriter.yaml) — Words that sell or persuade.
- 🧪 [Art Director](producers/art-director.yaml) — Visual look and feel.
- 🧪 [Narrative Designer](producers/narrative-designer.yaml) — Story structure and worlds.
- 🧪 [Community Manager](producers/community-manager.yaml) — Talking with your audience.
- 🧪 [Event Planner](producers/event-planner.yaml) — Events and experiences.
- 🧪 [Beta Reader](producers/beta-reader.yaml) — Early feedback on writing.
- 🧪 [Creative Writer](producers/creative-writer.yaml) — Fiction and creative prose.
- 🧪 [Dialect Coach](producers/dialect-coach.yaml) — Makes voices sound real.
- 🧪 [Dream Navigator](producers/dream-navigator.yaml) — Works with dream imagery.
- 🧪 [Forensic Consultant](producers/forensic-consultant.yaml) — Realistic crime detail for stories.
- 🧪 [Mirror Maker](producers/mirror-maker.yaml) — Flips ideas to see them anew.
- 🧪 [Mythologist](producers/mythologist.yaml) — Myths and legends.
- 🧪 [Narrator](producers/narrator.yaml) — Reads and voices the story.
- 🧪 [Symbolist](producers/symbolist.yaml) — Hidden meaning and symbols.
- 🧪 [Translator Silence](producers/translator-silence.yaml) — Reads what's left unsaid.

### ⬛ Commerce (10) — Growth & Selling
**Path:** `staff/commerce/`

- 🧪 [Social Media Strategist](commerce/social-media-strategist.yaml) — Growth on social platforms.
- 🧪 [SEO Specialist](commerce/seo-specialist.yaml) — Getting found on search.
- 🧪 [Conversion Optimizer](commerce/conversion-optimizer.yaml) — More clicks to "buy".
- 🧪 [Customer Acquisition Specialist](commerce/customer-acquisition-specialist.yaml) — Finds new customers.
- 🧪 [Influencer Strategist](commerce/influencer-strategist.yaml) — Partnerships and influencers.
- 🧪 [Pricing Strategist](commerce/pricing-strategist.yaml) — What to charge.
- 🧪 [Commercial Real Estate Analyst](commerce/commercial-real-estate-analyst.yaml) — Commercial property analysis.
- 🧪 [Interior Designer](commerce/interior-designer.yaml) — Indoor space design.
- 🧪 [Landscape Architect](commerce/landscape-architect.yaml) — Outdoor space design.
- 🧪 [Real Estate Investor](commerce/real-estate-investor.yaml) — Property investing.

### 💿 Tech (12) — Systems & Technology
**Path:** `staff/tech/`

- ⭐ [Software Architect](tech/software-architect.yaml) — Plans software the right way.
- ⭐ [Automation Specialist](tech/automation-specialist.yaml) — Automates repeat chores.
- ⭐ [Productivity Architect](tech/productivity-architect.yaml) — Systems for getting more done.
- ⭐ [Quality Control Specialist](tech/quality-control-specialist.yaml) — Catches bugs and mistakes.
- 🧪 [Prompt Engineer](tech/prompt-engineer.yaml) — Better instructions for AI.
- 🧪 [Toolmaker](tech/toolmaker.yaml) — Builds custom tools and scripts.
- 🧪 [Operations Manager](tech/operations-manager.yaml) — Smooth day-to-day operations.
- 🧪 [Cybersecurity Specialist](tech/cybersecurity-specialist.yaml) — Security and risk.
- 🧪 [Supply Chain Coordinator](tech/supply-chain-coordinator.yaml) — Logistics and supply.
- 🧪 [Handyman](tech/handyman.yaml) — Fixes broken things.
- 🧪 [Infinite Looper](tech/infinite-looper.yaml) — Repeats a task until it's right.
- 🧪 [Irony Detector](tech/irony-detector.yaml) — Spots sarcasm and irony.

### 🟩 Health & Lifestyle (9) — Wellness & Mindset
**Path:** `staff/health-lifestyle/`

- 🧪 [Habit Architect](health-lifestyle/habit-architect.yaml) — Builds good daily habits.
- 🧪 [Cognitive Behavioral Therapist](health-lifestyle/cognitive-behavioral-therapist.yaml) — Helpful thinking patterns.
- 🧪 [Stoic Coach](health-lifestyle/stoic-coach.yaml) — Calm and resilience.
- 🧪 [Health Coach](health-lifestyle/health-coach.yaml) — Food, movement, and wellness.
- 🧪 [Meditation Instructor](health-lifestyle/meditation-instructor.yaml) — Mindfulness and breathing.
- 🧪 [Active Imagination Guide](health-lifestyle/active-imagination-guide.yaml) — Inner reflection work.
- 🧪 [Humanist](health-lifestyle/humanist.yaml) — Growth and meaning.
- 🧪 [Shadow Worker](health-lifestyle/shadow-worker.yaml) — Facing hard inner stuff.
- 🧪 [Xenobiologist](health-lifestyle/xenobiologist.yaml) — Thinks from a truly alien view.

### ⬜ Knowledge (8) — Legal, Money & Records
**Path:** `staff/knowledge/`

- 🧪 [Business Lawyer](knowledge/business-lawyer.yaml) — Contracts and business law.
- 🧪 [Tax Strategist](knowledge/tax-strategist.yaml) — Tax planning.
- 🧪 [Investment Advisor](knowledge/investment-advisor.yaml) — Investing and wealth.
- 🧪 [Financial Therapist](knowledge/financial-therapist.yaml) — Your relationship with money.
- 🧪 [Antiquarian](knowledge/antiquarian.yaml) — Old and rare objects.
- 🧪 [Archivist Silence](knowledge/archivist-silence.yaml) — Lost or hidden records.
- 🧪 [Librarian Babel](knowledge/librarian-babel.yaml) — Finds the right source.
- 🧪 [Local Historian](knowledge/local-historian.yaml) — Local history and place.

### 🟪 Meta (1) — Shapeshifter
**Path:** `staff/meta/`

- 🧪 [Morphling](meta/morphling.yaml) — Adapts to any job that doesn't fit the others. (See [meta/README.md](meta/README.md) for its extra abilities.)

---

## 📈 Add Your Own Helper

The team is meant to grow. To add a new helper:

1. **Copy the template:** `templates/persona/new-staff-member-template.md` into the right department folder under `staff/`, and rename it `your-helper.yaml`.
2. **Fill it in:** role, personality, expertise, capabilities, and activation patterns. (Match the structure in the template.)
3. **Learn from examples:** Read a few existing helpers to see the depth and tone expected.
4. **Validate it:**

   ```bash
   uv run tools/validate_specialist.py
   ```

   (This checks every helper in `staff/`, including your new one.)

### Department Color Map (Magic: The Gathering)

- 🟦 **Blue** → `strategy/` — Planning & Insights
- 🟥 **Red** → `producers/` — Creative & Production
- ⬛ **Black** → `commerce/` — Growth & Commerce
- 💿 **Grey/Artifact** → `tech/` — Systems & Technology
- 🟩 **Green** → `health-lifestyle/` — Health & Lifestyle
- ⬜ **White** → `knowledge/` — Specialized Knowledge
- 🟪 **Colorless** → `meta/` — Meta and orchestration

Older roster-planning notes live in `archive/legacy-docs/` if you want the history.

---

## 🎯 What Every Helper Includes

- **Core Identity:** Role, personality, expertise, and communication style.
- **Core Capabilities:** 3–5 major capability areas with descriptions.
- **Integration Points:** Who they work with.
- **Activation Patterns:** Example prompts that trigger them.
- **Performance Standards:** Quality markers and success metrics.
- **Deep Dive:** Deliverables, knowledge areas, and workflows.
