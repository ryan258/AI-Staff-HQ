"""Tests for core agent logic."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from tools.engine.core import SpecialistAgent, load_specialist
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

@pytest.fixture
def mock_yaml(tmp_path):
    """Create a mock specialist YAML file."""
    staff_dir = tmp_path / "staff" / "tech"
    staff_dir.mkdir(parents=True)
    
    yaml_content = """
specialist: "Tech Specialist"
version: "1.0"
motto: "Code is poetry."
core_identity:
  role: "Software Engineer"
  personality: "Logical"
  communication_style: "Direct"
  expertise:
    - "Python"
  key_behaviors:
    - "Unit testing"
core_capabilities:
  - name: "Coding"
    description: "Writing robust code"
    tasks: ["Write unit tests"]
  - name: "Debugging"
    description: "Troubleshooting issues"
integration_points:
  inputs:
    - "JIRA"
  outputs:
    - "PRs"
  requirements:
    - "Clear specs"
  primary_collaborations:
    - "Product Manager"
activation_patterns:
  - pattern: "Code Review"
    examples: ["Can you review this?"]
performance_standards:
  quality_indicators:
    - "Bug free"
  success_metrics:
    - "Time to merge"
  accuracy: "High"
  timeliness: "Fast"
  completeness: "Total"
models:
  primary: "mock-model"
"""
    yaml_file = staff_dir / "tech-lead.yaml"
    yaml_file.write_text(yaml_content)
    return yaml_file

@pytest.fixture
def mock_router(mocker, mock_llm):
    """Mock ModelRouter class to avoid loading config."""
    # Patch the class where it is imported in core.py
    mock_cls = mocker.patch("tools.engine.core.ModelRouter")
    mock_instance = mock_cls.return_value
    # Default behavior for select_model
    mock_instance.select_model.return_value = "mock/model"
    # Return the shared mock_llm
    mock_instance.create_llm.return_value = mock_llm
    return mock_instance

def test_agent_initialization(mock_env, mock_yaml, mock_llm, mock_router):
    """Test initializing a SpecialistAgent."""
    agent = SpecialistAgent(mock_yaml)
    
    # Verify properties
    assert agent.schema.specialist == "Tech Specialist"
    assert agent.department == "tech"
    # Should fallback to default_model from mock_env/config since config is empty
    assert agent.model_name == "mock/model" 

def test_agent_query(mock_env, mock_yaml, mock_llm, mock_router):
    """Test querying the agent."""
    agent = SpecialistAgent(mock_yaml)
    
    # Setup mock response
    mock_llm.invoke.return_value = AIMessage(content="Mock answer")
    
    response = agent.query("Hello")
    
    # Verify response
    assert response == "Mock answer"
    
    # Verify state updated (System + Human + AI)
    # Note: call_args captures reference to mutable list, so it sees 3 messages
    assert len(agent.state.messages) == 3
    assert isinstance(agent.state.messages[1], HumanMessage)
    assert isinstance(agent.state.messages[2], AIMessage)
    
    # Verify LLM called
    mock_llm.invoke.assert_called_once()
    # We trust the call happened with the list reference
    
    # Check manual deep copy logic if strict history is needed, but sufficient here


def test_agent_query_uses_semantic_markdown_log_name(mock_env, mock_yaml, mock_llm, mock_router):
    """Interaction logs should use semantic filenames for new sessions."""
    agent = SpecialistAgent(mock_yaml)
    agent.config.log_dir = mock_env / ".ai-staff-hq" / "logs"

    mock_llm.invoke.return_value = AIMessage(content="Logged answer")

    agent.query("Hello from the semantic log test")

    log_files = list(agent.config.log_dir.glob("*.md"))
    assert len(log_files) == 1
    assert log_files[0].name.startswith("tech-lead__hello-from-the-semantic-log-test__")
    assert log_files[0].name.endswith(f"__{agent.state.session_id}.md")

def test_load_specialist_factory(mock_env, mock_yaml, mock_llm):
    """Test the load_specialist factory function."""
    staff_dir = mock_yaml.parent.parent # staff/
    
    # Load by identifier
    agent = load_specialist("tech-lead", staff_dir)
    assert agent.schema.specialist == "Tech Specialist"
    
    # Load by path
    agent2 = load_specialist(str(mock_yaml), staff_dir)
    assert agent2.schema.specialist == "Tech Specialist"
    
    # Validation error for missing
    with pytest.raises(FileNotFoundError):
        load_specialist("missing-agent", staff_dir)
