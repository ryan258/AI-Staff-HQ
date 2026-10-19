"""Tests for core agent logic."""

import os
import stat
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
    agent.config.enable_logging = True

    mock_llm.invoke.return_value = AIMessage(content="Logged answer")

    agent.query("Hello from the semantic log test")

    log_files = list(agent.config.log_dir.glob("*.md"))
    assert len(log_files) == 1
    assert log_files[0].name.startswith("tech-lead__hello-from-the-semantic-log-test__")
    assert log_files[0].name.endswith(f"__{agent.state.session_id}.md")


def test_interaction_logging_is_disabled_by_default(mock_env, mock_yaml, mock_llm, mock_router):
    """Private prompts must not be persisted unless logging is explicitly enabled."""
    agent = SpecialistAgent(mock_yaml)
    agent.config.log_dir = mock_env / ".ai-staff-hq" / "logs"

    mock_llm.invoke.return_value = AIMessage(content="private response")
    agent.query("private prompt")

    assert not agent.config.log_dir.exists()


def test_interaction_log_redacts_sensitive_content_and_is_private(
    mock_env, mock_yaml, mock_llm, mock_router
):
    """Opted-in interaction logs must redact secrets and use mode 0600."""
    agent = SpecialistAgent(mock_yaml)
    agent.config.log_dir = mock_env / ".ai-staff-hq" / "logs"
    agent.config.enable_logging = True
    mock_llm.invoke.return_value = AIMessage(
        content="response Bearer response-secret-token-1234567890"
    )

    prompt = "password: super-secret sk-or-v1-abcdef1234567890abcdef1234567890\n"
    prompt += "-----BEGIN PRIVATE KEY-----\nprivate-key-body\n-----END PRIVATE KEY-----"
    agent.query(prompt)

    log_file = next(agent.config.log_dir.glob("*.md"))
    assert stat.S_IMODE(log_file.stat().st_mode) == 0o600
    content = log_file.read_text(encoding="utf-8")
    assert "super-secret" not in log_file.name
    assert "super-secret" not in content
    assert "sk-or-v1-" not in content
    assert "private-key-body" not in content
    assert "response-secret-token" not in content
    assert "[REDACTED_PRIVATE_KEY]" in content

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


def test_agent_query_raises_on_llm_failure(mock_env, mock_yaml, mock_llm, mock_router):
    """Test that agent query raises AgentExecutionError on LLM failure."""
    from tools.engine.core import AgentExecutionError

    agent = SpecialistAgent(mock_yaml)
    mock_llm.invoke.side_effect = RuntimeError("Connection timeout")

    with pytest.raises(AgentExecutionError, match="Failed to get response from AI model"):
        agent.query("Hello")


def test_agent_query_raises_on_empty_reply(mock_env, mock_yaml, mock_llm, mock_router):
    """A reasoning model that spends its whole budget thinking must not count as an answer."""
    from tools.engine.core import AgentExecutionError

    agent = SpecialistAgent(mock_yaml)
    mock_llm.invoke.return_value = AIMessage(content="")

    with pytest.raises(AgentExecutionError, match="empty reply"):
        agent.query("Hello", max_tokens=16)
    assert not any(isinstance(m, AIMessage) for m in agent.state.messages)


def test_load_specialist_outside_staff_dir_rejected(mock_env, mock_yaml, mock_llm):
    """Test that load_specialist rejects paths outside the staff directory."""
    outside_dir = mock_env / "outside"
    outside_dir.mkdir(parents=True, exist_ok=True)
    outside_yaml = outside_dir / "external.yaml"
    outside_yaml.write_text(mock_yaml.read_text())

    staff_dir = mock_yaml.parent.parent

    with pytest.raises(PermissionError, match="must be inside staff directory"):
        load_specialist(str(outside_yaml), staff_dir)
