"""Streamlit dashboard for AI-Staff-HQ Phase 4 workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import streamlit as st

import sys
from pathlib import Path

# Add project root to path so we can import 'workflows'
# This handles the case where streamlit is run from the root
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from workflows.graphs.strategy_tech_handoff import run_strategy_tech_handoff
from workflows.graphs.strategic_planning import run_strategic_planning
from workflows.graphs.code_feature import run_code_feature
from workflows.graphs.cos_orchestration import run_cos_orchestration


BASE_DIR = Path(__file__).resolve().parents[1]
STAFF_DIR = BASE_DIR / "staff"


def list_specialists() -> Dict[str, List[str]]:
    """Return specialists grouped by department."""
    grouped = {}
    for dept_dir in sorted(STAFF_DIR.iterdir()):
        if not dept_dir.is_dir() or dept_dir.name.startswith("."):
            continue
        names = sorted(f.stem for f in dept_dir.rglob("*.yaml"))
        if names:
            grouped[dept_dir.name] = names
    return grouped


def main():
    st.set_page_config(page_title="AI-Staff-HQ", layout="wide")

    # Apply Candlelite Theme
    st.markdown("""
    <style>
        /* Candlelite Theme - Color Palette */
        :root {
            --bg-color: #121212;
            --text-color: #EBD2BE;
            --accent-primary: #A6ACCD;
            --accent-success: #98C379;
            --accent-danger: #E06C75;
            --card-bg: #121212;
            --border-color: #A6ACCD;
        }

        /* Main App Background */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-color);
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color) !important;
        }

        /* Text elements */
        .stMarkdown, .stText, p, span, label {
            color: var(--text-color) !important;
        }

        /* Captions */
        .stCaption {
            color: var(--accent-primary) !important;
        }

        /* Text inputs */
        .stTextInput > div > div > input {
            background-color: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }

        .stTextInput > div > div > input:focus {
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 1px var(--accent-primary);
        }

        /* Number inputs */
        .stNumberInput > div > div > input {
            background-color: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }

        /* Select boxes */
        .stSelectbox > div > div > div {
            background-color: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }

        /* Buttons - Primary */
        .stButton > button[kind="primary"] {
            background-color: var(--accent-primary);
            color: var(--bg-color);
            border: none;
            font-weight: 600;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: var(--accent-success);
            color: var(--bg-color);
        }

        /* Buttons - Secondary */
        .stButton > button {
            background-color: var(--bg-color);
            color: var(--accent-primary);
            border: 1px solid var(--accent-primary);
        }

        .stButton > button:hover {
            background-color: var(--accent-primary);
            color: var(--bg-color);
        }

        /* Checkboxes */
        .stCheckbox {
            color: var(--text-color) !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: var(--bg-color);
            color: var(--text-color) !important;
            border: 1px solid var(--border-color);
        }

        .streamlit-expanderContent {
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-top: none;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-color);
            border-right: 1px solid var(--border-color);
        }

        section[data-testid="stSidebar"] * {
            color: var(--text-color) !important;
        }

        /* Success messages */
        .stSuccess {
            background-color: var(--bg-color);
            color: var(--accent-success) !important;
            border-left: 4px solid var(--accent-success);
        }

        /* Error messages */
        .stError {
            background-color: var(--bg-color);
            color: var(--accent-danger) !important;
            border-left: 4px solid var(--accent-danger);
        }

        /* Spinner */
        .stSpinner > div {
            border-top-color: var(--accent-primary) !important;
        }

        /* Code blocks */
        code {
            background-color: var(--bg-color);
            color: var(--accent-primary);
            border: 1px solid var(--border-color);
        }

        /* JSON viewer */
        .stJson {
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
        }

        /* Dividers */
        hr {
            border-color: var(--border-color);
        }

        /* Links */
        a {
            color: var(--accent-primary);
        }

        a:hover {
            color: var(--accent-success);
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("AI-Staff-HQ Dashboard")
    st.caption("Phase 4: Autonomous Swarm & Interface")

    # Usage instructions
    with st.expander("ℹ️ How to Use", expanded=False):
        st.markdown("""
        ### Quick Start Guide

        1. **Select a Workflow** from the dropdown (Dynamic Orchestration is recommended)
        2. **Enter your topic/request** in the text box below
        3. **Configure settings** in the sidebar (optional)
        4. **Click "Run Workflow"** to execute

        ### What Each Workflow Does

        - **Dynamic Orchestration (Chief of Staff)**: The Chief of Staff analyzes your request, delegates to appropriate specialists, and synthesizes the results. Best for general requests.
        - **Strategy → Tech Handoff**: Market analysis → Technical planning → Executive brief
        - **Strategic Planning**: Market analysis → Creative strategy → Executive summary
        - **Code Feature Implementation**: Architecture → Implementation → QA review

        ### Reading Results

        After execution completes, you'll see:
        - **Final Synthesized Output** (for Dynamic Orchestration)
        - **Individual Specialist Outputs** (what each specialist produced)
        - **Execution Log** (detailed step-by-step workflow trace)

        ### Troubleshooting

        If no results appear:
        1. Check the **Raw Result Data** expander to see what was returned
        2. Review the **Full Execution Log** for errors
        3. Make sure your API keys are configured in `.env`
        """)

    # Initialize topic if not present
    if "topic" not in st.session_state:
        st.session_state["topic"] = ""

    # Workflow Selector (Main Column)
    workflow_map = {
        "Dynamic Orchestration (Chief of Staff)": run_cos_orchestration,
        "Strategy -> Tech Handoff": run_strategy_tech_handoff,
        "Strategic Planning": run_strategic_planning,
        "Code Feature Implementation": run_code_feature,
    }
    
    selected_workflow_name = st.selectbox(
        "Select Workflow",
        options=list(workflow_map.keys()),
        index=0  # Default to Dynamic CoS
    )

    # Sidebar configuration
    st.sidebar.header("Settings")
    auto_approve = st.sidebar.checkbox("Auto-approve handoffs", value=True)
    model_override = st.sidebar.text_input("Model override (optional)")
    temperature = st.sidebar.number_input("Temperature", min_value=0.0, max_value=1.0, step=0.1, value=0.7)



    st.subheader(f"Run: {selected_workflow_name}")
    
    topic = st.text_input("Topic or project", key="topic")

    with st.expander("Specialists"):
        st.caption("Click to insert template:")
        specialists_map = list_specialists()
        if specialists_map:
            cols = st.columns(len(specialists_map))
            for col, (dept, names) in zip(cols, specialists_map.items()):
                with col:
                    st.markdown(f"**{dept.title()}**")
                    for name in names:
                        if st.button(name, key=f"btn_{name}"):
                            current_topic = st.session_state.get("topic", "")
                            addition = name.replace('-', ' ').title()
                            # Add space if needed
                            if current_topic and not current_topic.endswith(" "):
                                current_topic += " "
                            st.session_state["topic"] = current_topic + addition
                            st.rerun()
    col1, col2 = st.columns([3, 1])
    with col1:
        run_button = st.button("Run Workflow", type="primary", disabled=not topic.strip())
    with col2:
        if st.button("Clear Results"):
            if "last_result" in st.session_state:
                del st.session_state["last_result"]
            st.rerun()

    if run_button:
        with st.spinner(f"Running {selected_workflow_name}..."):
            try:
                run_func = workflow_map[selected_workflow_name]
                result = run_func(
                    topic.strip(),
                    auto_approve=auto_approve,
                    model=model_override or None,
                    temperature=temperature,
                )
                st.session_state["last_result"] = result
                st.rerun()  # Force UI refresh to show results
            except Exception as exc:  # noqa: BLE001
                st.error(f"❌ Workflow failed: {exc}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        st.success(f"✓ Run complete (ID: {result.get('run_id', 'N/A')})")

        # Debug info - show what keys are in result
        st.caption(f"Result contains: {', '.join(result.keys())}")

        # Display final output first (most important for Dynamic Orchestration)
        if final_output := result.get("final_output"):
            with st.expander("📋 Final Synthesized Output", expanded=True):
                st.markdown(final_output)

        # Display individual specialist outputs
        if results_list := result.get("results"):
            st.subheader(f"Individual Specialist Outputs ({len(results_list)} total)")
            for idx, item in enumerate(results_list, 1):
                specialist = item.get("specialist", "Specialist").replace("-", " ").title()
                task = item.get("task", "")
                output = item.get("output", "")

                with st.expander(f"{idx}. {specialist}", expanded=False):
                    if task:
                        st.markdown(f"**Task:** {task}")
                        st.markdown("---")
                    st.markdown(output)
        else:
            # No results - check if there was an error
            if not result.get("final_output"):
                st.warning("⚠️ No outputs were generated. Check the step log below for details.")

        # Generic Result Display based on keys (for other workflows)
        display_keys = [
            ("analysis", "📊 Market Analysis"),
            ("strategy", "💡 Creative Strategy"),
            ("spec", "📐 Technical Spec"),
            ("technical_plan", "🔧 Technical Plan"),
            ("code", "💻 Implementation"),
            ("qa_report", "✅ QA Report"),
            ("strategy_plan", "📈 Strategic Plan"),
            ("executive_brief", "📄 Executive Brief"),
        ]

        for key, title in display_keys:
            if val := result.get(key):
                with st.expander(title, expanded=True):
                    st.markdown(val)

        # Step log - always show for debugging
        with st.expander("🔍 Full Execution Log", expanded=False):
            steps = result.get("steps", [])
            if steps:
                st.caption(f"{len(steps)} steps recorded")
                st.json(steps)
            else:
                st.warning("No steps were recorded")

        # Raw result viewer for debugging
        with st.expander("🐛 Raw Result Data (Debug)", expanded=False):
            st.json(result)


if __name__ == "__main__":
    main()
