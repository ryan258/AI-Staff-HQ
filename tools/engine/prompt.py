"""YAML to system prompt conversion."""

from typing import List
from .schemas import SpecialistSchema


class PromptBuilder:
    """Converts specialist YAML to system prompts."""

    def __init__(self, specialist: SpecialistSchema):
        self.specialist = specialist

    def build_system_prompt(self) -> str:
        """Generate comprehensive system prompt from YAML.

        Section order favors what the model needs to act on the current
        request (identity, capabilities, workflow, quality bar) before
        deeper reference material (knowledge, collaboration) and example
        phrasings (activation patterns, which are catalog metadata rather
        than response-shaping instructions). Grounding runs last for
        recency.
        """
        sections = [
            self._build_identity_section(),
            self._build_capabilities_section(),
            self._build_workflow_section(),
            self._build_standards_section(),
            self._build_knowledge_section(),
            self._build_collaboration_section(),
            self._build_activation_section(),
            self._build_grounding_section(),
        ]

        return "\n\n".join(filter(None, sections))

    def _build_identity_section(self) -> str:
        """Core identity and role."""
        identity = self.specialist.core_identity
        return f"""# {self.specialist.specialist}

**Motto**: {self.specialist.motto}

## Your Role
You are a {identity.role}.

**Personality**: {identity.personality}

**Communication Style**: {identity.communication_style}

**Core Expertise**:
{self._format_list(identity.expertise)}"""

    def _build_capabilities_section(self) -> str:
        """Core capabilities and tasks."""
        caps = []
        for cap in self.specialist.core_capabilities:
            cap_text = f"### {cap.name}\n{cap.description}"
            if cap.tasks:
                cap_text += f"\n\n**Key Tasks**:\n{self._format_list(cap.tasks)}"
            caps.append(cap_text)

        return f"## Your Capabilities\n\n" + "\n\n".join(caps)

    def _build_collaboration_section(self) -> str:
        """Integration and collaboration patterns."""
        collab = self.specialist.integration_points
        text = "## Collaboration\n\n"
        text += f"**Primary Collaborators**: {', '.join(collab.primary_collaborations)}\n"
        if collab.secondary_collaborations:
            text += f"**Secondary Collaborators**: {', '.join(collab.secondary_collaborations)}"
        return text

    def _build_standards_section(self) -> str:
        """Performance standards and quality metrics."""
        standards = self.specialist.performance_standards
        return f"""## Quality Standards

Apply these before finalizing your response:

**Quality Indicators**:
{self._format_list(standards.quality_indicators)}

**Success Metrics**:
{self._format_list(standards.success_metrics)}"""

    def _build_knowledge_section(self) -> str:
        """Deep dive knowledge areas (if available)."""
        if not self.specialist.deep_dive:
            return ""

        dd = self.specialist.deep_dive
        sections = []

        # Deliverables
        deliverables = []
        for cat in dd.typical_deliverables:
            deliverables.append(f"**{cat.category}**:\n{self._format_list(cat.items)}")
        sections.append(f"### Typical Deliverables\n\n" + "\n\n".join(deliverables))

        # Knowledge areas
        knowledge = []
        for area in dd.specialized_knowledge_areas:
            knowledge.append(f"**{area.area}**:\n{self._format_list(area.skills)}")
        sections.append(f"### Specialized Knowledge\n\n" + "\n\n".join(knowledge))

        return "## Deep Expertise\n\n" + "\n\n".join(sections)

    def _build_activation_section(self) -> str:
        """Example activation phrasings (reference only, not a required format)."""
        patterns = []
        for pat in self.specialist.activation_patterns:
            # Handle schema fluidity (type vs name)
            pat_type = pat.type or pat.name or "General Pattern"
            if pat.pattern:
                pat_text = f"**{pat_type}**\nTrigger: `{pat.pattern}`"
                if pat.examples:
                    pat_text += f"\nExamples:\n{self._format_list(pat.examples)}"
                patterns.append(pat_text)
            elif pat.sub_types:
                # Handle nested patterns
                sub_text = f"**{pat_type}**"
                for sub in pat.sub_types:
                    sub_name = sub.type or sub.name or "Sub-pattern"
                    if sub.pattern:
                        sub_text += f"\n- {sub_name}: `{sub.pattern}`"
                patterns.append(sub_text)

        if not patterns:
            return ""

        return (
            "## Example Requests (reference only)\n\n"
            "These illustrate the kind of requests you handle. Respond to the "
            "actual request below, not to these examples.\n\n" + "\n\n".join(patterns)
        )

    def _build_grounding_section(self) -> str:
        """Anti-hallucination instruction; placed last in the prompt for recency."""
        return (
            "## Grounding\n\n"
            "Ground your response in the request below and the expertise above. "
            "If specific details are missing that you would normally need, state "
            "your assumption plainly rather than inventing facts about the user's "
            "real business, product, or situation. This does not limit imaginative "
            "or speculative work when that is what the request calls for."
        )

    def _build_workflow_section(self) -> str:
        """Inject workflows dynamically.

        Workflow/process fields (e.g. `pricing_strategy_workflow`) are
        declared nested under `deep_dive` in every current specialist YAML,
        not at the top level, so both locations are scanned. Both models
        allow extra fields (schema 'extra'='allow'), which is how these
        dynamically-named fields survive validation.
        """
        workflows = []
        seen = set()

        def collect(source: dict) -> None:
            for field, value in source.items():
                if not ((field.endswith('_workflow') or field.endswith('_process')) and isinstance(value, list)):
                    continue
                if field in seen:
                    continue
                seen.add(field)
                steps = []
                for phase in value:
                    phase_title = phase.get('phase', 'Phase')
                    step_list = phase.get('steps', [])
                    steps.append(f"### {phase_title}\n{self._format_list(step_list)}")

                workflows.append(f"**{field.replace('_', ' ').title()}**\n\n" + "\n\n".join(steps))

        collect(self.specialist.model_dump())
        if self.specialist.deep_dive:
            collect(self.specialist.deep_dive.model_dump())

        if not workflows:
            return ""

        return "## Standard Workflows\n\n" + "\n\n".join(workflows)

    def _format_list(self, items: List[str]) -> str:
        """Format list as markdown."""
        return "\n".join(f"- {item}" for item in items)

    def build_user_prompt_wrapper(self, user_query: str) -> str:
        """Wrap user query with activation context."""
        return f"""As the {self.specialist.specialist}, please respond to the following:

{user_query}

Remember to embody your role, personality, and expertise in your response."""
