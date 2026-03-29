"""Centralized Candlelite Theme definition for AI-Staff-HQ.

This module provides the Single Source of Truth for the Candlelite color palette,
exporting definitions for both Rich (CLI) and Streamlit (Web) interfaces.
"""

from rich.theme import Theme

# Candlelite Color Palette
COLORS = {
    "bg": "#121212",        # Off-Black
    "text": "#EBD2BE",      # Warm Beige
    "accent": "#A6ACCD",    # Muted Lavender
    "success": "#98C379",   # Green
    "danger": "#E06C75",    # Red
}

# Rich CLI Theme
RICH_THEME = Theme({
    "success": COLORS["success"],
    "error": COLORS["danger"],
    "accent": COLORS["accent"],
    "text": COLORS["text"],
    "dim": f"dim {COLORS['text']}",
    "warning": f"bold {COLORS['text']}",
})

# Streamlit CSS
# Note: This injects CSS variables that should be used by the app.
STREAMLIT_CSS = f"""
<style>
    /* Candlelite Theme - Color Palette */
    :root {{
        --bg-color: {COLORS['bg']};
        --text-color: {COLORS['text']};
        --accent-primary: {COLORS['accent']};
        --accent-success: {COLORS['success']};
        --accent-danger: {COLORS['danger']};
        --card-bg: {COLORS['bg']};
        --border-color: {COLORS['accent']};
    }}

    /* Main App Background */
    .stApp {{
        background-color: var(--bg-color);
        color: var(--text-color);
    }}

    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-color) !important;
    }}

    /* Text elements */
    .stMarkdown, .stText, p, span, label {{
        color: var(--text-color) !important;
    }}

    /* Captions */
    .stCaption {{
        color: var(--accent-primary) !important;
    }}

    /* Text inputs */
    .stTextInput > div > div > input {{
        background-color: var(--bg-color);
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }}

    .stTextInput > div > div > input:focus {{
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 1px var(--accent-primary);
    }}

    /* Number inputs */
    .stNumberInput > div > div > input {{
        background-color: var(--bg-color);
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }}

    /* Select boxes */
    .stSelectbox > div > div > div {{
        background-color: var(--bg-color);
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }}

    /* Buttons - Primary */
    .stButton > button[kind="primary"] {{
        background-color: var(--accent-primary);
        color: var(--bg-color);
        border: none;
        font-weight: 600;
    }}

    .stButton > button[kind="primary"]:hover {{
        background-color: var(--accent-success);
        color: var(--bg-color);
    }}

    /* Buttons - Secondary */
    .stButton > button {{
        background-color: var(--bg-color);
        color: var(--accent-primary);
        border: 1px solid var(--accent-primary);
    }}

    .stButton > button:hover {{
        background-color: var(--accent-primary);
        color: var(--bg-color);
    }}

    /* Checkboxes */
    .stCheckbox {{
        color: var(--text-color) !important;
    }}

    /* Expanders */
    .streamlit-expanderHeader {{
        background-color: var(--bg-color);
        color: var(--text-color) !important;
        border: 1px solid var(--border-color);
    }}

    .streamlit-expanderContent {{
        background-color: var(--bg-color);
        border: 1px solid var(--border-color);
        border-top: none;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-color);
        border-right: 1px solid var(--border-color);
    }}

    section[data-testid="stSidebar"] * {{
        color: var(--text-color) !important;
    }}

    /* Success messages */
    .stSuccess {{
        background-color: var(--bg-color);
        color: var(--accent-success) !important;
        border-left: 4px solid var(--accent-success);
    }}

    /* Error messages */
    .stError {{
        background-color: var(--bg-color);
        color: var(--accent-danger) !important;
        border-left: 4px solid var(--accent-danger);
    }}

    /* Warning messages */
    .stWarning {{
        background-color: var(--bg-color);
        color: var(--text-color) !important;
        border-left: 4px solid var(--accent-danger);
    }}

    /* Spinner */
    .stSpinner > div {{
        border-top-color: var(--accent-primary) !important;
    }}

    /* Code blocks */
    code {{
        background-color: var(--bg-color);
        color: var(--accent-primary);
        border: 1px solid var(--border-color);
    }}

    /* JSON viewer */
    .stJson {{
        background-color: var(--bg-color);
        border: 1px solid var(--border-color);
    }}

    /* Dividers */
    hr {{
        border-color: var(--border-color);
    }}

    /* Links */
    a {{
        color: var(--accent-primary);
    }}

    a:hover {{
        color: var(--accent-success);
    }}
</style>
"""
