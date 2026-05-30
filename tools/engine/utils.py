"""Shared utility functions."""

from pathlib import Path
import json
import re
from typing import Any, List, Optional


_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _iter_balanced_arrays(text: str):
    """Yield substrings that look like balanced top-level JSON arrays.

    Scans character-by-character tracking bracket depth while respecting string
    literals and escapes, so nested arrays and brackets inside strings do not
    confuse extraction (unlike a naive first-``[`` / last-``]`` slice).
    """
    depth = 0
    start = -1
    in_string = False
    escaped = False
    for i, ch in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "[":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "]":
            if depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    yield text[start : i + 1]
                    start = -1


def extract_json_array(text: str) -> Optional[List[Any]]:
    """Best-effort extraction of a JSON array from a model response.

    Handles markdown code fences, surrounding prose, and nested/bracketed
    content. Returns the first substring that parses to a ``list``, or ``None``
    if nothing valid is found.
    """
    if not text:
        return None

    candidates: List[str] = []

    # Prefer fenced blocks (most reliable when the model cooperates).
    for fenced in _CODE_FENCE_RE.findall(text):
        candidates.append(fenced.strip())

    # Then any balanced array found anywhere in the raw text.
    candidates.extend(_iter_balanced_arrays(text))

    for candidate in candidates:
        for snippet in (candidate, *_iter_balanced_arrays(candidate)):
            try:
                parsed = json.loads(snippet)
            except (json.JSONDecodeError, ValueError):
                continue
            if isinstance(parsed, list):
                return parsed

    return None


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

_SECRET_PATTERNS = (
    # Provider API keys (OpenAI/OpenRouter sk-..., Anthropic sk-ant-...)
    re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{16,}\b"),
    # AWS access key IDs
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    # GitHub tokens
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    # Bearer tokens in headers
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{16,}"),
    # key=value / "key": "value" pairs naming a secret
    re.compile(
        r"(?i)(api[_-]?key|secret|token|password|passwd|authorization)"
        r"(\"?\s*[:=]\s*\"?)([^\s\"',}]{6,})"
    ),
)

_REDACTED = "[REDACTED]"

_SECRET_KEY_RE = re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|authorization|bearer)")


def redact_secrets(value: Any) -> Any:
    """Redact likely secrets from strings (and recursively from dicts/lists).

    Scrubs provider API keys, cloud credentials, bearer tokens, and
    ``key=value`` pairs whose key names a secret, before data is written to
    persistent logs. Dict values are also redacted when their key names a
    secret. Non-string scalars pass through unchanged.
    """
    if isinstance(value, str):
        redacted = value
        for pattern in _SECRET_PATTERNS:
            if pattern.groups >= 3:
                redacted = pattern.sub(rf"\1\2{_REDACTED}", redacted)
            else:
                redacted = pattern.sub(_REDACTED, redacted)
        return redacted
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            if isinstance(k, str) and isinstance(v, str) and _SECRET_KEY_RE.search(k):
                result[k] = _REDACTED
            else:
                result[k] = redact_secrets(v)
        return result
    if isinstance(value, (list, tuple)):
        return type(value)(redact_secrets(v) for v in value)
    return value


def get_project_root() -> Path:
    """Get the absolute path to the project root (ai-staff-hq)."""
    # Assuming this file is in tools/engine/utils.py
    # root is 3 levels up
    return Path(__file__).resolve().parent.parent.parent
