"""Token counting and budgeting helpers.

Centralizes token math so "max_context_tokens" actually means tokens. Uses
tiktoken (already a dependency) with a cheap character-based fallback if an
encoding can't be loaded.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

# Rough fallback ratio when tiktoken is unavailable (~4 chars/token for English).
_CHARS_PER_TOKEN = 4


@lru_cache(maxsize=4)
def _encoding(model_hint: str = "cl100k_base"):
    """Return a tiktoken encoding, or None if tiktoken can't be used."""
    try:
        import tiktoken

        try:
            return tiktoken.get_encoding(model_hint)
        except Exception:
            return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def count_tokens(text: str) -> int:
    """Count tokens in a string (tiktoken when available, else estimated)."""
    if not text:
        return 0
    enc = _encoding()
    if enc is not None:
        return len(enc.encode(text))
    return max(1, len(text) // _CHARS_PER_TOKEN)


def message_tokens(message: Any) -> int:
    """Approximate token count for a LangChain message (content + small overhead)."""
    content = getattr(message, "content", message)
    if not isinstance(content, str):
        content = str(content)
    # +4 to loosely account for role/formatting overhead per message.
    return count_tokens(content) + 4


def truncate_to_tokens(text: str, max_tokens: int, *, suffix: str = "... [truncated]") -> str:
    """Truncate ``text`` so it fits within ``max_tokens`` tokens.

    Returns the text unchanged when it already fits. The ``suffix`` marker is
    appended (and counted toward the budget) when truncation occurs.
    """
    if max_tokens <= 0 or not text:
        return text
    enc = _encoding()
    if enc is not None:
        tokens = enc.encode(text)
        if len(tokens) <= max_tokens:
            return text
        suffix_tokens = len(enc.encode(suffix))
        keep = max(0, max_tokens - suffix_tokens)
        return enc.decode(tokens[:keep]) + suffix

    # Fallback: approximate with characters.
    max_chars = max_tokens * _CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - len(suffix))] + suffix
