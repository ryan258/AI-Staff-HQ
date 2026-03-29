"""Tests for Candlelite theme semantics."""

from ui.theme import RICH_THEME, STREAMLIT_CSS


def test_warning_style_differs_from_accent_style():
    """Warnings should be visually distinct from generic accents."""
    assert str(RICH_THEME.styles["warning"]) != str(RICH_THEME.styles["accent"])


def test_streamlit_css_styles_warning_messages():
    """Streamlit warnings should have explicit Candlelite styling."""
    assert ".stWarning" in STREAMLIT_CSS
    assert "border-left: 4px solid var(--accent-danger);" in STREAMLIT_CSS
