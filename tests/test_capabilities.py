"""Tests for agent capabilities and filesystem boundaries."""

import os
import pytest
from pathlib import Path
from tools.engine.capabilities import read_file, write_file, list_directory, run_command


def test_capabilities_within_permitted_root(tmp_path, monkeypatch):
    """Test reading and writing within permitted root."""
    monkeypatch.setenv("USER_CWD", str(tmp_path))

    # Write file
    res_write = write_file.invoke({"path": "sub/hello.txt", "content": "world"})
    assert "Successfully wrote" in res_write

    # Read file
    res_read = read_file.invoke({"path": "sub/hello.txt"})
    assert res_read == "world"

    # List directory
    res_list = list_directory.invoke({"path": "sub"})
    assert "- hello.txt" in res_list


def test_capabilities_block_traversal_outside_permitted_root(tmp_path, monkeypatch):
    """Test that attempting to read or write outside permitted root is denied."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("secret_data")

    monkeypatch.setenv("USER_CWD", str(sandbox))

    # Read outside
    res_read = read_file.invoke({"path": "../secret.txt"})
    assert "Access denied" in res_read

    # Write outside
    res_write = write_file.invoke({"path": "../escaped.txt", "content": "pwn"})
    assert "Access denied" in res_write

    # List outside
    res_list = list_directory.invoke({"path": ".."})
    assert "Access denied" in res_list


def test_capabilities_shell_policy(tmp_path, monkeypatch):
    """Test that MORPHLING_SHELL_ENABLED=false blocks command execution."""
    monkeypatch.setenv("USER_CWD", str(tmp_path))
    monkeypatch.setenv("MORPHLING_SHELL_ENABLED", "false")

    res = run_command.invoke({"command": "echo test"})
    assert "disabled by security policy" in res


def test_shell_is_disabled_by_default(tmp_path, monkeypatch):
    """Morphling must not inherit an unrestricted shell by default."""
    monkeypatch.setenv("USER_CWD", str(tmp_path))
    monkeypatch.delenv("MORPHLING_SHELL_ENABLED", raising=False)

    res = run_command.invoke({"command": "echo test"})
    assert "disabled by security policy" in res


def test_shell_requires_an_explicit_true_enable_flag(tmp_path, monkeypatch):
    """Unknown enable values must fail closed rather than activate the shell."""
    monkeypatch.setenv("USER_CWD", str(tmp_path))
    monkeypatch.setenv("MORPHLING_SHELL_ENABLED", "yes")

    res = run_command.invoke({"command": "echo test"})

    assert "disabled by security policy" in res


def test_allowlisted_shell_rejects_outside_paths_and_shell_metacharacters(tmp_path, monkeypatch):
    """The default explicit shell mode must enforce the same filesystem boundary."""
    monkeypatch.setenv("USER_CWD", str(tmp_path))
    monkeypatch.setenv("MORPHLING_SHELL_ENABLED", "true")
    monkeypatch.setenv("MORPHLING_SHELL_MODE", "allowlist")

    outside = run_command.invoke({"command": "cat /etc/hosts"})
    assert "outside permitted root" in outside

    injected = run_command.invoke({"command": "echo safe; cat /etc/hosts"})
    assert "shell metacharacters" in injected


def test_allowlisted_shell_rejects_relative_symlink_escape(tmp_path, monkeypatch):
    """A relative path argument must not follow a symlink outside the root."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside-secret")
    (sandbox / "link.txt").symlink_to(outside)
    monkeypatch.setenv("USER_CWD", str(sandbox))
    monkeypatch.setenv("MORPHLING_SHELL_ENABLED", "true")
    monkeypatch.setenv("MORPHLING_SHELL_MODE", "allowlist")

    result = run_command.invoke({"command": "cat link.txt"})

    assert "outside permitted root" in result
    assert "outside-secret" not in result


def test_owner_shell_requires_unrestricted_root_flag(tmp_path, monkeypatch):
    """Arbitrary shell mode must not silently bypass the root policy."""
    monkeypatch.setenv("USER_CWD", str(tmp_path))
    monkeypatch.setenv("MORPHLING_SHELL_ENABLED", "true")
    monkeypatch.setenv("MORPHLING_SHELL_MODE", "owner")
    monkeypatch.setenv("MORPHLING_OWNER_MODE", "true")
    monkeypatch.delenv("MORPHLING_UNRESTRICTED_ROOT", raising=False)

    result = run_command.invoke({"command": "cat /etc/hosts"})

    assert "MORPHLING_UNRESTRICTED_ROOT=true" in result


def test_unrestricted_root_requires_explicit_owner_mode(tmp_path, monkeypatch):
    """The path bypass flag cannot independently disable the root boundary."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside-secret")
    monkeypatch.setenv("USER_CWD", str(sandbox))
    monkeypatch.setenv("MORPHLING_UNRESTRICTED_ROOT", "true")
    monkeypatch.setenv("MORPHLING_OWNER_MODE", "false")

    denied = read_file.invoke({"path": str(outside)})
    assert "outside permitted root" in denied

    monkeypatch.setenv("MORPHLING_OWNER_MODE", "true")
    allowed = read_file.invoke({"path": str(outside)})
    assert allowed == "outside-secret"


def test_owner_shell_requires_explicit_owner_mode(tmp_path, monkeypatch):
    """Arbitrary shell execution requires the separate owner-mode gate."""
    monkeypatch.setenv("USER_CWD", str(tmp_path))
    monkeypatch.setenv("MORPHLING_SHELL_ENABLED", "true")
    monkeypatch.setenv("MORPHLING_SHELL_MODE", "owner")
    monkeypatch.setenv("MORPHLING_OWNER_MODE", "false")

    denied = run_command.invoke({"command": "echo test"})
    assert "requires MORPHLING_OWNER_MODE=true" in denied


def test_capability_helpers_reject_symlink_escape(tmp_path, monkeypatch):
    """Resolved symlink targets must remain beneath USER_CWD."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    (sandbox / "link.txt").symlink_to(outside)
    monkeypatch.setenv("USER_CWD", str(sandbox))

    assert "outside permitted root" in read_file.invoke({"path": "link.txt"})
    assert "outside permitted root" in write_file.invoke({"path": "link.txt", "content": "overwrite"})
