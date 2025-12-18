"""YAML to system prompt conversion."""

from typing import List
from .schemas import SpecialistSchema


class PromptBuilder:
    """Converts specialist YAML to system prompts."""

    def __init__(self, specialist: SpecialistSchema):
        self.specialist = specialist

    def build_system_prompt(self) -> str:
        """Generate comprehensive system prompt from YAML."""
        sections = [
            self._build_identity_section(),
            self._build_capabilities_section(),
            self._build_collaboration_section(),
            self._build_standards_section(),
            self._build_knowledge_section(),
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

    def _format_list(self, items: List[str]) -> str:
        """Format list as markdown."""
        return "\n".join(f"- {item}" for item in items)

    def build_user_prompt_wrapper(self, user_query: str) -> str:
        """Wrap user query with activation context."""
        return f"""As the {self.specialist.specialist}, please respond to the following:

{user_query}

Remember to embody your role, personality, and expertise in your response."""
