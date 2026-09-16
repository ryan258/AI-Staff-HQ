"""Tests for conversation state persistence."""

import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from langchain_core.messages import HumanMessage, AIMessage

from tools.engine.state import (
    ConversationState,
    SessionCorruptError,
    SessionIdentityMismatchError,
)

def test_state_initialization(mock_env):
    """Test new session initialization."""
    state = ConversationState(specialist_slug="test-specialist")

    assert state.specialist_slug == "test-specialist"
    assert len(state.session_id) == 24
    # Validate format: YYYYMMDD_HHMMSS_hex8
    import re
    pattern = r'^\d{8}_\d{6}_[0-9a-f]{8}$'
    assert re.match(pattern, state.session_id), f"Session ID format invalid: {state.session_id}"
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

def test_clear_session(mock_env):
    """Test clearing session creates new ID and resets messages."""
    state = ConversationState("test-clear")

    # Add some messages
    from langchain_core.messages import SystemMessage
    state.add_message(SystemMessage(content="System"))
    state.add_message(HumanMessage(content="Q1"))
    state.add_message(AIMessage(content="A1"))

    old_session_id = state.session_id

    # Clear
    new_session_id = state.clear()

    # Verify new session
    assert new_session_id != old_session_id
    assert len(new_session_id) == 24
    assert len(state.messages) == 1  # Only system message kept
    assert isinstance(state.messages[0], SystemMessage)


def test_session_id_path_traversal_rejected(mock_env):
    """Test that path traversal attempts in session_id or specialist_slug are rejected."""
    with pytest.raises(ValueError, match="forbidden characters"):
        ConversationState("test-specialist", session_id="../../escaped")

    with pytest.raises(ValueError, match="forbidden characters"):
        ConversationState("../../escaped", session_id="normal_id")

    with pytest.raises(ValueError, match="forbidden characters"):
        ConversationState("test-specialist", session_id="foo/bar")


def test_session_file_private_permissions(mock_env):
    """Test that session files are saved with 0600 permissions."""
    import stat
    state = ConversationState("test-perm")
    state.add_message(HumanMessage(content="Private message"))
    state.save()

    assert state.session_file.exists()
    file_mode = stat.S_IMODE(state.session_file.stat().st_mode)
    assert file_mode == 0o600


def test_list_sessions_rejects_traversal_specialist_slug(mock_env):
    """Session listing must validate and contain the specialist directory."""
    with pytest.raises(ValueError, match="forbidden characters"):
        ConversationState.list_sessions("../outside")


def test_load_distinguishes_corrupt_session_and_preserves_evidence(mock_env):
    """Malformed JSON is a hard load error, not a new-session miss."""
    state = ConversationState("corrupt-session", session_id="20260831_120000_deadbeef")
    state.session_file.write_text("{not-json", encoding="utf-8")
    original = state.session_file.read_text(encoding="utf-8")

    with pytest.raises(SessionCorruptError, match="corrupt"):
        state.load()

    assert state.session_file.read_text(encoding="utf-8") == original


def test_session_lock_symlink_is_rejected(mock_env):
    """A malicious lock path must not redirect state writes elsewhere."""
    state = ConversationState("lock-symlink", session_id="20260831_120000_deadbeef")
    outside_lock = mock_env / "outside.lock"
    outside_lock.write_text("sentinel", encoding="utf-8")
    lock_path = state.session_dir / f".{state.session_id}.lock"
    lock_path.symlink_to(outside_lock)
    state.add_message(HumanMessage(content="should not be written"))

    with pytest.raises(SessionCorruptError, match="lock"):
        state.save()

    assert outside_lock.read_text(encoding="utf-8") == "sentinel"


def test_load_distinguishes_identity_mismatch(mock_env):
    """A valid file for another session must not be treated as missing."""
    state = ConversationState("identity-session", session_id="20260831_120000_deadbeef")
    state.session_file.write_text(
        json.dumps({
            "session_id": state.session_id,
            "specialist": "different-specialist",
            "created_at": state.created_at,
            "updated_at": state.updated_at,
            "messages": [],
        }),
        encoding="utf-8",
    )

    with pytest.raises(SessionIdentityMismatchError, match="specialist"):
        state.load()


def test_concurrent_state_saves_preserve_appended_messages(mock_env):
    """Per-session locking and merge-on-save must retain independent appends."""
    session_id = "20260831_120000_deadbeef"
    first = ConversationState("concurrent-session", session_id=session_id)
    second = ConversationState("concurrent-session", session_id=session_id)
    first.add_message(HumanMessage(content="first message"))
    second.add_message(HumanMessage(content="second message"))

    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda state: state.save(), (first, second)))

    saved = json.loads(first.session_file.read_text(encoding="utf-8"))
    contents = [item["data"]["content"] for item in saved["messages"]]
    assert "first message" in contents
    assert "second message" in contents


def test_trimmed_sessions_preserve_repeated_turns_and_bounded_context(mock_env):
    from langchain_core.messages import SystemMessage
    from tools.engine.config import get_config

    get_config().max_history_turns = 1
    state = ConversationState("repeated-turns")
    state.add_message(SystemMessage(content="system"))
    for question, answer in [("again", "first"), ("different", "second"), ("again", "third")]:
        state.add_message(HumanMessage(content=question))
        state.add_message(AIMessage(content=answer))
        state.save()
        assert len(state.messages) == 3
    state.save()  # An unchanged save must not duplicate events.
    saved = json.loads(state.session_file.read_text())
    assert [item["data"]["content"] for item in saved["messages"]] == [
        "system", "again", "first", "different", "second", "again", "third"
    ]
    loaded = ConversationState("repeated-turns", session_id=state.session_id)
    assert loaded.load()
    assert [item.content for item in loaded.messages] == ["system", "again", "third"]


def test_legacy_session_concurrent_identical_appends_are_distinct_events(mock_env):
    from langchain_core.messages import SystemMessage, messages_to_dict
    from tools.engine.config import get_config

    get_config().max_history_turns = 1
    first = ConversationState("legacy-repeat")
    first.session_file.write_text(json.dumps({
        "session_id": first.session_id, "specialist": first.specialist_slug,
        "created_at": first.created_at,
        "messages": messages_to_dict([SystemMessage(content="system"), HumanMessage(content="old"), AIMessage(content="old answer")]),
    }))
    second = ConversationState(first.specialist_slug, session_id=first.session_id)
    assert first.load() and second.load()
    for state in (first, second):
        state.add_message(HumanMessage(content="same question"))
        state.add_message(AIMessage(content="same answer"))
    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda state: state.save(), (first, second)))
    first.save()
    saved = json.loads(first.session_file.read_text())
    contents = [item["data"]["content"] for item in saved["messages"]]
    assert contents == ["system", "old", "old answer", "same question", "same answer", "same question", "same answer"]
    assert len(first.messages) == len(second.messages) == 3


def test_save_retry_after_replacement_does_not_duplicate_events(mock_env, monkeypatch):
    import os

    state = ConversationState("retry-event")
    state.add_message(HumanMessage(content="repeatable"))
    original_chmod = os.chmod

    def fail_after_replace(path, mode):
        if path == state.session_file:
            raise OSError("post-replace failure")
        return original_chmod(path, mode)

    with monkeypatch.context() as patch:
        patch.setattr(os, "chmod", fail_after_replace)
        with pytest.raises(OSError, match="post-replace"):
            state.save()
    state.save()
    saved = json.loads(state.session_file.read_text())
    assert len(saved["messages"]) == len(saved["message_ids"]) == 1


def test_disabled_persistence_keeps_only_bounded_context(mock_env):
    from langchain_core.messages import SystemMessage
    from tools.engine.config import get_config

    config = get_config()
    config.save_sessions = False
    config.max_history_turns = 1
    state = ConversationState("ephemeral-context")
    state.add_message(SystemMessage(content="system"))
    for index in range(100):
        state.add_message(HumanMessage(content=f"question {index}"))
        state.add_message(AIMessage(content=f"answer {index}"))
        state.save()
    assert len(state.messages) == 3
    assert state._pending_messages == []
    assert not state.session_file.exists()
    state.clear()
    assert len(state.messages) == 1
    assert state._pending_messages == []
    assert not state.session_file.exists()


def test_disabling_persistence_discards_previously_pending_events(mock_env):
    state = ConversationState("disabled-pending")
    state.add_message(HumanMessage(content="unsaved"))
    assert state._pending_messages
    state.config.save_sessions = False
    state.save()
    assert state._pending_messages == []
    assert not state.session_file.exists()


@pytest.mark.parametrize("identities", [[], ["same", "same"], [None], [["invalid"]]])
def test_invalid_event_id_metadata_preserves_corrupt_evidence(mock_env, identities):
    state = ConversationState("invalid-event-ids")
    state.add_message(HumanMessage(content="message"))
    state.save()
    data = json.loads(state.session_file.read_text())
    data["message_ids"] = identities
    state.session_file.write_text(json.dumps(data))
    original = state.session_file.read_text()
    with pytest.raises(SessionCorruptError, match="message_ids"):
        state.load()
    assert state.session_file.read_text() == original
