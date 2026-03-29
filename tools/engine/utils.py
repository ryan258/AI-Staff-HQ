"""Shared utility functions."""

from pathlib import Path
import re


_PROMPT_LABELS = (
    "USER BRIEF:",
    "ORIGINAL USER BRIEF:",
    "Feature Request:",
    "Request:",
    "Topic:",
    "TASK:",
    "Brief:",
)

_PROMPT_STOP_PREFIXES = (
    "AVAILABLE SPECIALISTS:",
    "CRITICAL REQUIREMENTS:",
    "FEW-SHOT EXAMPLES:",
    "Please complete this task.",
    "Break this request into specific, atomic tasks.",
    "Return ONLY a JSON array",
    "--- CONTEXT",
    "### Output from",
)


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


def extract_semantic_subject(text: str, *, fallback: str = "untitled") -> str:
    """Extract the most meaningful subject phrase from a prompt-like string."""
    raw_text = str(text or "").strip()
    if not raw_text:
        return fallback

    lines = [line.strip() for line in raw_text.splitlines()]

    def collect_from(start_index: int, initial: str = "") -> str:
        collected = [initial.strip()] if initial.strip() else []
        for line in lines[start_index:]:
            stripped = line.strip()
            if not stripped:
                if collected:
                    break
                continue
            if stripped in _PROMPT_LABELS:
                if collected:
                    break
                continue
            if any(stripped.startswith(prefix) for prefix in _PROMPT_STOP_PREFIXES):
                if collected:
                    break
                continue
            collected.append(stripped)
        return " ".join(part for part in collected if part).strip()

    for index, line in enumerate(lines):
        for label in _PROMPT_LABELS:
            if line.startswith(label):
                inline = line[len(label):].strip()
                subject = collect_from(index + 1, inline)
                if subject:
                    return subject

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if any(stripped.startswith(prefix) for prefix in _PROMPT_STOP_PREFIXES):
            continue
        if stripped in _PROMPT_LABELS:
            continue
        return stripped

    return fallback


def semantic_slug(text: str, *, fallback: str = "untitled", max_length: int = 56) -> str:
    """Create a readable slug from free-form text for filenames and labels."""
    collapsed = re.sub(r"\s+", " ", extract_semantic_subject(text, fallback=fallback)).strip()
    if not collapsed:
        return fallback

    first_line = collapsed.splitlines()[0].strip()
    slug = normalize_slug(first_line)
    if not slug:
        return fallback

    if len(slug) <= max_length:
        return slug

    trimmed = slug[:max_length].rstrip("-")
    split_at = trimmed.rfind("-")
    if split_at >= max_length // 2:
        trimmed = trimmed[:split_at]

    return trimmed.rstrip("-") or fallback


def build_semantic_run_filename(
    *,
    run_id: str,
    subject: str,
    workflow_name: str | None = None,
    extension: str,
) -> str:
    """Build a readable, collision-safe filename for a workflow run log."""
    parts = []

    if workflow_name:
        parts.append(semantic_slug(workflow_name, fallback="workflow", max_length=28))

    parts.append(semantic_slug(subject, fallback="run"))
    parts.append(run_id or "unknown")

    suffix = extension if extension.startswith(".") else f".{extension}"
    return "__".join(parts) + suffix

def get_project_root() -> Path:
    """Get the absolute path to the project root (ai-staff-hq)."""
    # Assuming this file is in tools/engine/utils.py
    # root is 3 levels up
    return Path(__file__).resolve().parent.parent.parent
