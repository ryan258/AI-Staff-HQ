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
    st.title("AI-Staff-HQ Dashboard")
    st.caption("Phase 4: Autonomous Swarm & Interface")

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

    with st.sidebar.expander("Specialists", expanded=True):
        st.caption("Click to insert template:")
        for dept, names in list_specialists().items():
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

    st.subheader(f"Run: {selected_workflow_name}")
    
    topic = st.text_input("Topic or project", key="topic")
    if st.button("Run Workflow", type="primary", disabled=not topic.strip()):
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
            except Exception as exc:  # noqa: BLE001
                st.error(f"Workflow failed: {exc}")

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        st.success(f"Run complete (ID: {result.get('run_id')})")

        if result.get("results"):
            for item in result["results"]:
                specialist = item.get("specialist", "Specialist").replace("-", " ").title()
                with st.expander(f"Output: {specialist}", expanded=True):
                    st.markdown(item.get("output", ""))

        # Generic Result Display based on keys
        display_keys = [
            ("analysis", "Market Analysis"),
            ("strategy", "Creative Strategy"),
            ("spec", "Technical Spec"),
            ("technical_plan", "Technical Plan"),
            ("code", "Implementation"),
            ("qa_report", "QA Report"),
            ("strategy_plan", "Strategic Plan"),
            ("executive_brief", "Executive Brief"),
            ("final_output", "Final Output"),
        ]

        for key, title in display_keys:
            if val := result.get(key):
                with st.expander(title, expanded=True):
                    st.markdown(val)

        with st.expander("Full Step Log", expanded=False):
            st.json(result.get("steps", []))


if __name__ == "__main__":
    main()
