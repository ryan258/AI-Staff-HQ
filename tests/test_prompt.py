"""Tests for PromptBuilder (tools/engine/prompt.py)."""

import pytest

from tools.engine.prompt import PromptBuilder
from tools.engine.schemas import SpecialistSchema


@pytest.fixture
def specialist_data():
    """Minimal valid specialist data with a deep_dive-nested workflow field,
    matching the real shape used across staff/*/*.yaml (e.g.
    pricing-strategist.yaml's `deep_dive.pricing_strategy_workflow`)."""
    return {
        "version": "1.2",
        "specialist": "Test Specialist",
        "motto": "Ship it.",
        "core_identity": {
            "role": "Test Engineer",
            "personality": "Methodical",
            "expertise": ["Testing"],
            "communication_style": "Direct",
        },
        "core_capabilities": [
            {"name": "Testing", "description": "Writes tests", "tasks": ["Write unit tests"]},
        ],
        "integration_points": {
            "primary_collaborations": ["QA Lead"],
        },
        "activation_patterns": [
            {"type": "Test Request", "pattern": "Test Specialist, test X.", "examples": ["Test Specialist, test the login flow."]},
        ],
        "performance_standards": {
            "quality_indicators": ["No flaky tests"],
            "success_metrics": ["Coverage up"],
        },
        "deep_dive": {
            "typical_deliverables": [
                {"category": "Reports", "items": ["Test report"]},
            ],
            "specialized_knowledge_areas": [
                {"area": "Testing", "skills": ["pytest"]},
            ],
            "test_strategy_workflow": [
                {"phase": "Plan", "steps": ["Write test plan"]},
                {"phase": "Execute", "steps": ["Run tests", "Record results"]},
            ],
        },
    }


def test_workflow_section_renders_deep_dive_nested_workflow(specialist_data):
    """Regression test: workflow fields are declared nested under deep_dive
    in every current specialist YAML, not at the top level. The prompt must
    surface them, not silently drop them."""
    spec = SpecialistSchema(**specialist_data)
    prompt = PromptBuilder(spec).build_system_prompt()

    assert "## Standard Workflows" in prompt
    assert "Test Strategy Workflow" in prompt
    assert "### Plan" in prompt
    assert "Write test plan" in prompt
    assert "### Execute" in prompt
    assert "Record results" in prompt


def test_workflow_section_empty_when_no_workflow_fields():
    """No _workflow/_process field anywhere means no Standard Workflows section."""
    data = {
        "version": "1.2",
        "specialist": "No Workflow Specialist",
        "motto": "N/A",
        "core_identity": {
            "role": "Role",
            "personality": "P",
            "expertise": ["X"],
            "communication_style": "C",
        },
        "core_capabilities": [{"name": "Cap", "description": "D"}],
        "integration_points": {"primary_collaborations": ["Someone"]},
        "activation_patterns": [],
        "performance_standards": {"quality_indicators": ["Q"], "success_metrics": ["S"]},
    }
    spec = SpecialistSchema(**data)
    prompt = PromptBuilder(spec).build_system_prompt()

    assert "## Standard Workflows" not in prompt


def test_grounding_section_present_and_last(specialist_data):
    spec = SpecialistSchema(**specialist_data)
    prompt = PromptBuilder(spec).build_system_prompt()

    assert "## Grounding" in prompt
    assert prompt.rstrip().endswith("that is what the request calls for.")
    # Grounding must be the final section.
    assert prompt.index("## Grounding") > prompt.index("## Quality Standards")
    assert prompt.index("## Grounding") > prompt.rindex("## Example Requests")


def test_activation_section_labeled_as_reference_only(specialist_data):
    spec = SpecialistSchema(**specialist_data)
    prompt = PromptBuilder(spec).build_system_prompt()

    assert "## Example Requests (reference only)" in prompt
    assert "## Activation Patterns" not in prompt


def test_quality_standards_section_is_actionable(specialist_data):
    spec = SpecialistSchema(**specialist_data)
    prompt = PromptBuilder(spec).build_system_prompt()

    assert "Apply these before finalizing your response:" in prompt
