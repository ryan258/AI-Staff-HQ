"""File system capabilities for agents."""

import os
from pathlib import Path
from typing import List
from langchain_core.tools import tool


def _resolve_path(path: str) -> Path:
    """Resolve path relative to USER_CWD if set, otherwise current directory."""
    user_cwd = os.environ.get("USER_CWD")
    target_path = Path(path)
    
    if user_cwd and not target_path.is_absolute():
        return Path(user_cwd) / target_path
    
    return target_path


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
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def list_directory(path: str = ".") -> str:
    """List files and directories in a given path.
    
    Args:
        path: The directory path to list (default: current directory).
    """
    try:
        # Special case for "." when USER_CWD is set
        if path == "." and "USER_CWD" in os.environ:
             dir_path = Path(os.environ["USER_CWD"])
        else:
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
    except Exception as e:
        return f"Error listing directory: {e}"
