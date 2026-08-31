"""File system and command execution capabilities for agents."""

import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import List
from langchain_core.tools import tool

# Limits for run_command output to prevent token explosion.
_MAX_OUTPUT_CHARS = 10_000
_DEFAULT_TIMEOUT_SECONDS = 60
_SAFE_COMMANDS = {
    "cat",
    "echo",
    "find",
    "grep",
    "head",
    "ls",
    "pwd",
    "rg",
    "tail",
    "wc",
}
_UNSAFE_FIND_OPTIONS = {
    "-delete",
    "-exec",
    "-execdir",
    "-ok",
    "-okdir",
    "-fls",
    "-fprint",
    "-fprint0",
    "-fprintf",
}
_SHELL_METACHARACTERS = re.compile(r"[;&|<>`$()\n\r]")


def _get_permitted_root() -> Path:
    """Return the permitted directory boundary for file and execution capabilities."""
    user_cwd = os.environ.get("USER_CWD")
    if user_cwd:
        return Path(user_cwd).resolve()
    return Path.cwd().resolve()


def _resolve_path(path: str, enforce_root: bool = True) -> Path:
    """Resolve path relative to USER_CWD if set, otherwise current directory.

    Enforces that resolved path does not escape the permitted root boundary
    unless the owner explicitly enables both unrestricted-root and owner mode.
    """
    root = _get_permitted_root()
    target_path = Path(path)

    if not target_path.is_absolute():
        resolved = (root / target_path).resolve()
    else:
        resolved = target_path.resolve()

    owner_mode = os.environ.get("MORPHLING_OWNER_MODE", "false").lower() in ("true", "1")
    unrestricted_requested = os.environ.get("MORPHLING_UNRESTRICTED_ROOT", "").lower() in (
        "true",
        "1",
    )
    unrestricted = owner_mode and unrestricted_requested
    if enforce_root and not unrestricted:
        try:
            resolved.relative_to(root)
        except ValueError:
            raise PermissionError(f"Access denied: path '{path}' is outside permitted root '{root}'")

    return resolved


def _parse_allowlisted_command(command: str) -> list[str]:
    """Parse a command without invoking a shell and enforce path boundaries."""
    if _SHELL_METACHARACTERS.search(command):
        raise PermissionError("shell metacharacters are not allowed in allowlist mode")
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError as exc:
        raise PermissionError(f"invalid command quoting: {exc}") from exc
    if not tokens:
        raise ValueError("command must not be empty")

    executable = Path(tokens[0]).name
    if tokens[0] != executable or executable not in _SAFE_COMMANDS:
        raise PermissionError(
            f"command '{tokens[0]}' is not permitted in allowlist mode"
        )

    if executable == "find" and any(
        token in _UNSAFE_FIND_OPTIONS for token in tokens[1:]
    ):
        raise PermissionError("mutating find expressions are not allowed in allowlist mode")

    for token in tokens[1:]:
        # Resolve every argument, not just visibly path-shaped arguments.  A
        # bare relative name can still be a symlink (``cat link.txt``), and
        # resolving it here makes the boundary check symlink-aware before the
        # child process opens it.  Nonexistent words resolve beneath the root
        # and are harmlessly accepted as ordinary command arguments.
        candidate = token.split("=", 1)[1] if "=" in token else token
        _resolve_path(candidate)
    return tokens


@tool
def read_file(path: str) -> str:
    """Read the content of a file from the local filesystem.
    
    Args:
        path: The path to the file to read.
    """
    try:
        file_path = _resolve_path(path)
        if not file_path.exists():
            return f"Error: File not found at {path}"
        return file_path.read_text(encoding="utf-8")
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file on the local filesystem.
    
    Args:
        path: The path to the file to write.
        content: The text content to write.
    """
    try:
        file_path = _resolve_path(path)
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def list_directory(path: str = ".") -> str:
    """List files and directories in a given path.
    
    Args:
        path: The directory path to list (default: current directory).
    """
    try:
        dir_path = _resolve_path(path)

        if not dir_path.exists():
            return f"Error: Directory not found at {path}"
        if not dir_path.is_dir():
            return f"Error: {path} is not a directory"
            
        params = []
        for item in dir_path.iterdir():
            type_char = "d" if item.is_dir() else "-"
            params.append(f"{type_char} {item.name}")
            
        return "\n".join(sorted(params))
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error listing directory: {e}"


@tool
def run_command(command: str, working_directory: str = ".") -> str:
    """Run a shell command and return its combined stdout and stderr.

    Use this to install dependencies, run tests, compile code, or verify
    that code you have written actually works.  After writing files, call
    this tool to close the build-test-fix loop: run the tests, read the
    errors, fix the code, and run again until everything passes.

    Args:
        command: The shell command to run (e.g. "npm test", "python -m pytest",
                 "go build ./...").
        working_directory: Directory to run the command in.  Defaults to the
                           current project directory.
    """
    if os.environ.get("MORPHLING_SHELL_ENABLED", "false").lower() not in ("true", "1"):
        return "Error: Command execution is disabled by security policy"

    try:
        cwd = str(_resolve_path(working_directory))
        mode = os.environ.get("MORPHLING_SHELL_MODE", "allowlist").lower()
        if mode == "owner":
            if os.environ.get("MORPHLING_OWNER_MODE", "false").lower() not in ("true", "1"):
                return "Error: owner shell mode requires MORPHLING_OWNER_MODE=true"
            if os.environ.get("MORPHLING_UNRESTRICTED_ROOT", "false").lower() not in ("true", "1"):
                return "Error: owner shell mode requires MORPHLING_UNRESTRICTED_ROOT=true"
            invocation = command
            use_shell = True
        elif mode == "allowlist":
            invocation = _parse_allowlisted_command(command)
            use_shell = False
        else:
            return f"Error: unsupported MORPHLING_SHELL_MODE '{mode}'"

        result = subprocess.run(
            invocation,
            shell=use_shell,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=_DEFAULT_TIMEOUT_SECONDS,
        )

        output_parts: list[str] = []
        if result.stdout:
            output_parts.append(result.stdout)
        if result.stderr:
            output_parts.append(result.stderr)
        combined = "\n".join(output_parts).strip()

        # Truncate to avoid token explosion.
        if len(combined) > _MAX_OUTPUT_CHARS:
            half = _MAX_OUTPUT_CHARS // 2
            combined = (
                combined[:half]
                + f"\n\n... ({len(combined) - _MAX_OUTPUT_CHARS} chars truncated) ...\n\n"
                + combined[-half:]
            )

        exit_label = "SUCCESS" if result.returncode == 0 else f"FAILED (exit code {result.returncode})"
        return f"[{exit_label}]\n{combined}" if combined else f"[{exit_label}]"

    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Command exceeded {_DEFAULT_TIMEOUT_SECONDS}s limit: {command}"
    except Exception as e:
        return f"[ERROR] {e}"
