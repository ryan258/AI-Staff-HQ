"""Streamlit dashboard for AI-Staff-HQ Phase 4 workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import streamlit as st

from workflows.graphs.strategy_tech_handoff import run_strategy_tech_handoff


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


def run_workflow(topic: str, auto_approve: bool, model: str | None, temperature: float | None):
    """Execute the Strategy -> Tech graph and return results."""
    return run_strategy_tech_handoff(
        topic,
        auto_approve=auto_approve,
        model=model,
        temperature=temperature,
    )


def main():
    st.set_page_config(page_title="AI-Staff-HQ", layout="wide")
    st.title("AI-Staff-HQ Dashboard")
    st.caption("Phase 4: Autonomous Swarm & Interface")

    # Sidebar configuration
    st.sidebar.header("Settings")
    auto_approve = st.sidebar.checkbox("Auto-approve handoffs", value=True)
    model_override = st.sidebar.text_input("Model override (optional)")
    temperature = st.sidebar.number_input("Temperature", min_value=0.0, max_value=1.0, step=0.1, value=0.7)

    with st.sidebar.expander("Specialists"):
        for dept, names in list_specialists().items():
            st.markdown(f"**{dept}**")
            st.write(", ".join(names))

    st.subheader("Run Strategy → Tech → Executive Brief")
    topic = st.text_input("Topic or project")
    if st.button("Run Workflow", type="primary", disabled=not topic.strip()):
        with st.spinner("Running workflow..."):
            try:
                result = run_workflow(
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

        cols = st.columns(3)
        if result.get("analysis"):
            cols[0].markdown("### Market Analysis")
            cols[0].markdown(result["analysis"])
        if result.get("technical_plan"):
            cols[1].markdown("### Technical Plan")
            cols[1].markdown(result["technical_plan"])
        if result.get("executive_brief"):
            cols[2].markdown("### Executive Brief")
            cols[2].markdown(result["executive_brief"])

        with st.expander("Step Log"):
            st.json(result.get("steps", []))


if __name__ == "__main__":
    main()
