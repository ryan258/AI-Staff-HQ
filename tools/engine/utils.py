"""Shared utility functions."""

from pathlib import Path
import re

def normalize_slug(text: str) -> str:
    """
    Normalize text into a consistent slug format.
    
    Args:
        text: Input text (e.g. "Market Analyst", "market-analyst", "Tech/Toolmaker")
        
    Returns:
        Kebab-case slug (e.g. "market-analyst")
    """
    # Remove file extension if present
    text = Path(text).stem
    
    # Convert to lower case
    text = text.lower()
    
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    
    # Remove non-alphanumeric characters (except hyphens)
    text = re.sub(r'[^a-z0-9-]', '', text)
    
    # Strip leading/trailing hyphens
    text = text.strip('-')
    
    return text

def get_project_root() -> Path:
    """Get the absolute path to the project root (ai-staff-hq)."""
    # Assuming this file is in tools/engine/utils.py
    # root is 3 levels up
    return Path(__file__).resolve().parent.parent.parent
