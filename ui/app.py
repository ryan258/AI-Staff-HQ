"""Streamlit dashboard for AI-Staff-HQ Phase 4 workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import streamlit as st

import sys

# Add project root to path so we can import 'workflows'
# This handles the case where streamlit is run from the root
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from tools.engine.roster import list_specialists_by_department
from workflows.graphs.strategy_tech_handoff import run_strategy_tech_handoff
from workflows.graphs.strategic_planning import run_strategic_planning
from workflows.graphs.code_feature import run_code_feature
from workflows.graphs.cos_orchestration import run_cos_orchestration
from workflows.planning_swarm import run_planning_swarm


BASE_DIR = Path(__file__).resolve().parents[1]
STAFF_DIR = BASE_DIR / "staff"


def list_specialists(include_experimental: bool = False) -> Dict[str, List[str]]:
    """Return specialists grouped by department for the chosen tiers."""
    tiers = ("active", "experimental") if include_experimental else ("active",)
    return list_specialists_by_department(STAFF_DIR, tiers=tiers)


def main():
    st.set_page_config(page_title="AI-Staff-HQ", layout="wide")

    # Apply Candlelite Theme
    from ui.theme import STREAMLIT_CSS
    st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)

    st.title("AI-Staff-HQ Dashboard")
    st.caption("Phase 4: Autonomous Swarm & Interface")

    # Usage instructions
    with st.expander("ℹ️ How to Use", expanded=False):
        st.markdown("""
        ### Quick Start Guide

        1. **Select a Workflow** from the dropdown (Flagship Planning Swarm is recommended)
        2. **Enter your topic/request** in the text box below
        3. **Configure settings** in the sidebar (optional)
        4. **Click "Run Workflow"** to execute

        ### What Each Workflow Does

        - **Flagship Planning Swarm**: Uses the small active roster to turn vague briefs into a high-quality structured plan. This is the default path.
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
        "Flagship Planning Swarm": run_planning_swarm,
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
    include_experimental = st.sidebar.checkbox("Include experimental staff", value=False)



    st.subheader(f"Run: {selected_workflow_name}")
    
    topic = st.text_input("Topic or project", key="topic")

    with st.expander("Specialists"):
        st.caption("Active roster suggestions. Experimental staff are opt-in.")
        specialists_map = list_specialists(include_experimental=include_experimental)
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
                run_kwargs = {
                    "auto_approve": auto_approve,
                    "model": model_override or None,
                    "temperature": temperature,
                }
                if selected_workflow_name in {
                    "Flagship Planning Swarm",
                    "Dynamic Orchestration (Chief of Staff)",
                }:
                    run_kwargs["include_experimental"] = include_experimental

                result = run_func(topic.strip(), **run_kwargs)
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
        if result.get("log_path"):
            st.caption(f"Log file: {result['log_path']}")

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
