"""File system and command execution capabilities for agents.

These tools are handed to tool-enabled specialists (e.g. Morphling). Because the
agent decides what to run from model output, every operation is contained to a
single workspace directory and shell commands are screened against a denylist of
destructive patterns. The sole operator can widen the boundary with environment
variables (see ``_sandbox_enabled`` / ``_shell_enabled``).
"""

import os
import re
import subprocess
from pathlib import Path

from langchain_core.tools import tool

# Limits for run_command output to prevent token explosion.
_MAX_OUTPUT_CHARS = 10_000
_DEFAULT_TIMEOUT_SECONDS = 60

# Environment toggles (sole-operator escape hatches).
_DISABLE_SANDBOX_ENV = "AISTAFF_DISABLE_SANDBOX"  # "1" => no path containment
_DISABLE_SHELL_ENV = "AISTAFF_DISABLE_SHELL"  # "1" => run_command refuses
_WORKSPACE_ENV = "AISTAFF_WORKSPACE"  # explicit sandbox root override

# Shell commands matching any of these are always refused, even with the sandbox
# disabled. These are catastrophic / system-level operations an agent has no
# business issuing autonomously.
_DESTRUCTIVE_PATTERNS = (
    r"\brm\s+(-[a-z]*\s+)*(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r)",  # rm -rf and variants
    r"\bmkfs\b",
    r"\bdd\b\s+if=",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bhalt\b",
    r"\b:\(\)\s*\{",  # fork bomb :(){ :|:& };:
    r">\s*/dev/sd[a-z]",
    r"\bchmod\s+-R\s+777\s+/",
    r"\bsudo\b",
    r"\bmv\b\s+\S+\s+/dev/null",
    r"\b(curl|wget)\b.*\|\s*(sudo\s+)?(ba)?sh\b",  # curl ... | sh
)
_DESTRUCTIVE_RE = re.compile("|".join(_DESTRUCTIVE_PATTERNS), re.IGNORECASE)


class SandboxViolation(Exception):
    """Raised when an operation would escape the agent workspace."""


def _sandbox_enabled() -> bool:
    return os.environ.get(_DISABLE_SANDBOX_ENV, "").strip() not in {"1", "true", "yes"}


def _shell_enabled() -> bool:
    return os.environ.get(_DISABLE_SHELL_ENV, "").strip() not in {"1", "true", "yes"}


def _workspace_root() -> Path:
    """The directory all agent file operations are contained within."""
    explicit = os.environ.get(_WORKSPACE_ENV)
    if explicit:
        return Path(explicit).expanduser().resolve()
    user_cwd = os.environ.get("USER_CWD")
    if user_cwd:
        return Path(user_cwd).expanduser().resolve()
    return Path.cwd().resolve()


def _resolve_path(path: str) -> Path:
    """Resolve ``path`` against the workspace root, enforcing containment.

    Relative paths are joined to the workspace root. Absolute paths are honored
    but must still resolve to a location inside the root. Raises
    ``SandboxViolation`` when containment is enabled and the target escapes.
    """
    root = _workspace_root()
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate

    # Resolve symlinks / .. without requiring the path to exist.
    resolved = candidate.resolve()

    if _sandbox_enabled() and not _is_within(resolved, root):
        raise SandboxViolation(
            f"Path '{path}' resolves outside the agent workspace ({root}). "
            f"Set {_DISABLE_SANDBOX_ENV}=1 to allow operations outside the workspace."
        )
    return resolved


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


@tool
def read_file(path: str) -> str:
    """Read the content of a file from the agent workspace.

    Args:
        path: The path to the file to read (contained to the workspace).
    """
    try:
        file_path = _resolve_path(path)
        if not file_path.exists():
            return f"Error: File not found at {path}"
        return file_path.read_text(encoding="utf-8")
    except SandboxViolation as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file in the agent workspace.

    Args:
        path: The path to the file to write (contained to the workspace).
        content: The text content to write.
    """
    try:
        file_path = _resolve_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except SandboxViolation as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def list_directory(path: str = ".") -> str:
    """List files and directories in a given path within the workspace.

    Args:
        path: The directory path to list (default: workspace root).
    """
    try:
        dir_path = _resolve_path(path)
        if not dir_path.exists():
            return f"Error: Directory not found at {path}"
        if not dir_path.is_dir():
            return f"Error: {path} is not a directory"

        entries = []
        for item in dir_path.iterdir():
            type_char = "d" if item.is_dir() else "-"
            entries.append(f"{type_char} {item.name}")

        return "\n".join(sorted(entries))
    except SandboxViolation as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error listing directory: {e}"


def _screen_command(command: str) -> str | None:
    """Return a refusal message if the command is disallowed, else None."""
    if not command.strip():
        return "Error: empty command."
    if _DESTRUCTIVE_RE.search(command):
        return (
            "Error: command refused by safety policy (matches a destructive "
            "pattern such as recursive delete, disk write, privilege escalation, "
            "or remote pipe-to-shell)."
        )
    return None


@tool
def run_command(command: str, working_directory: str = ".") -> str:
    """Run a shell command and return its combined stdout and stderr.

    Use this to install dependencies, run tests, compile code, or verify
    that code you have written actually works.  After writing files, call
    this tool to close the build-test-fix loop: run the tests, read the
    errors, fix the code, and run again until everything passes.

    The command runs inside the agent workspace and is screened against a
    safety denylist. Catastrophic or system-level commands are refused.

    Args:
        command: The shell command to run (e.g. "npm test", "python -m pytest",
                 "go build ./...").
        working_directory: Directory to run the command in.  Defaults to the
                           workspace root and is contained within it.
    """
    if not _shell_enabled():
        return (
            f"Error: shell execution is disabled ({_DISABLE_SHELL_ENV} is set). "
            "Enable it to run commands."
        )

    refusal = _screen_command(command)
    if refusal:
        return refusal

    try:
        cwd = str(_resolve_path(working_directory))
    except SandboxViolation as e:
        return f"Error: {e}"

    try:
        result = subprocess.run(
            command,
            shell=True,
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
