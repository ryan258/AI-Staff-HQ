"""Tests for conversation state persistence."""

import json
import pytest
from langchain_core.messages import HumanMessage, AIMessage

from tools.engine.state import ConversationState

def test_state_initialization(mock_env):
    """Test new session initialization."""
    state = ConversationState(specialist_slug="test-specialist")
    
    assert state.specialist_slug == "test-specialist"
    assert len(state.session_id) == 8
    assert state.messages == []
    
    # Check directory created
    expected_dir = mock_env / ".ai-staff-hq" / "sessions" / "test-specialist"
    assert expected_dir.exists()

def test_add_message_and_save(mock_env):
    """Test adding messages and saving to disk."""
    state = ConversationState("test-specialist")
    
    msg = HumanMessage(content="Hello")
    state.add_message(msg)
    
    assert len(state.messages) == 1
    
    # Save
    state.save()
    
    # Verify file
    session_file = state.session_file
    assert session_file.exists()
    
    with open(session_file) as f:
        data = json.load(f)
        
    assert data["session_id"] == state.session_id
    assert data["specialist"] == "test-specialist"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["data"]["content"] == "Hello"

def test_load_session(mock_env):
    """Test loading an existing session."""
    # Create original state
    original = ConversationState("test-load")
    original.add_message(HumanMessage(content="Question"))
    original.add_message(AIMessage(content="Answer"))
    original.save()
    
    # Load new instance with same ID
    loaded = ConversationState("test-load", session_id=original.session_id)
    success = loaded.load()
    
    assert success is True
    assert loaded.session_id == original.session_id
    assert len(loaded.messages) == 2
    assert isinstance(loaded.messages[0], HumanMessage)
    assert isinstance(loaded.messages[1], AIMessage)
    assert loaded.messages[1].content == "Answer"

def test_history_trimming(mock_env):
    """Test that history is trimmed to max turns."""
    from tools.engine.config import get_config
    config = get_config()
    config.max_history_turns = 2  # Keep last 2 turns (4 messages)
    
    state = ConversationState("trim-test")
    
    # Add System message (should always flip)
    from langchain_core.messages import SystemMessage
    sys_msg = SystemMessage(content="System")
    state.add_message(sys_msg)
    
    # Add 3 turns (6 messages)
    for i in range(3):
        state.add_message(HumanMessage(content=f"Q{i}"))
        state.add_message(AIMessage(content=f"A{i}"))
        
    # Total messages: 1 (Sys) + 6 (Chat) = 7
    # Should keep Sys + Last 2 turns (4 messages) = 5 total
    
    assert len(state.messages) == 5
    assert state.messages[0].content == "System"
    assert state.messages[1].content == "Q1"  # Q0/A0 trimmed
    assert state.messages[-1].content == "A2"
