"""Lightweight LangGraph runner for AI-Staff-HQ multi-agent workflows."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, END

from tools.engine.core import load_specialist


class GraphState(TypedDict, total=False):
    """State passed between graph nodes."""

    topic: str
    inputs: Dict[str, Any]
    analysis: str
    technical_plan: str
    executive_brief: str
    
    # keys for expanded workflows
    strategy: str
    spec: str
    code: str
    qa_report: str
    strategy_plan: str
    final_output: str
    
    # keys for dynamic looping
    queue: List[Dict[str, str]]
    results: List[Dict[str, str]]
    
    approvals: List[str]
    steps: List[Dict[str, Any]]
    run_id: str


AgentLoader = Callable[[str, Path, Optional[str], Optional[float], Optional[str]], Any]
ApprovalHandler = Callable[[str, GraphState], bool]
PromptBuilder = Callable[[GraphState], str]


def _default_agent_loader(
    specialist_slug: str,
    staff_dir: Path,
    model_override: Optional[str],
    temperature: Optional[float],
    session_id: Optional[str],
):
    return load_specialist(
        specialist_slug,
        staff_dir,
        model_override=model_override,
        temperature=temperature,
        session_id=session_id
    )


class GraphRunner:
    """Orchestrates langgraph graphs with logging and approvals."""

    def __init__(
        self,
        staff_dir: Path,
        *,
        model_override: Optional[str] = None,
        temperature: Optional[float] = None,
        approval_handler: Optional[ApprovalHandler] = None,
        auto_approve: bool = True,
        log_dir: Optional[Path] = None,
        agent_loader: Optional[AgentLoader] = None,
    ):
        self.staff_dir = staff_dir
        self.model_override = model_override
        self.temperature = temperature
        self.approval_handler = approval_handler
        self.auto_approve = auto_approve
        self.log_dir = log_dir or Path("logs") / "graphs"
        self.agent_loader = agent_loader or _default_agent_loader
        self._agent_cache: Dict[str, Any] = {}

    def get_agent(self, specialist_slug: str, session_id: Optional[str] = None):
        """Memoize specialist agents within a run to reduce initialization overhead."""
        # Use :: separator to avoid ambiguity with timestamps or colons in slugs
        cache_key = f"{specialist_slug}::{session_id}" if session_id else specialist_slug
        
        if cache_key not in self._agent_cache:
            agent = self.agent_loader(
                specialist_slug,
                self.staff_dir,
                self.model_override,
                self.temperature,
                session_id,
            )
            self._agent_cache[cache_key] = agent
        return self._agent_cache[cache_key]

    def record_step(self, state: GraphState, name: str, detail: Dict[str, Any]) -> None:
        """Append a structured log entry to the state."""
        steps = state.setdefault("steps", [])
        steps.append(
            {
                "step": name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **detail,
            }
        )

    def require_approval(self, gate_name: str, state: GraphState) -> bool:
        """Check for approval before continuing."""
        if self.approval_handler:
            return bool(self.approval_handler(gate_name, state))
        if self.auto_approve:
            return True

        response = input(f"[Approve] {gate_name}? (y/N): ").strip().lower()
        return response in {"y", "yes"}

    def make_agent_node(
        self,
        *,
        specialist_slug: str,
        state_key: str,
        prompt_builder: PromptBuilder,
        step_name: Optional[str] = None,
    ) -> Callable[[GraphState], GraphState]:
        """Create a graph node that queries a specialist and stores the output."""

        def node(state: GraphState) -> GraphState:
            # Use run_id as session_id for unified logging
            run_id = state.get("run_id")
            # Use public method
            agent = self.get_agent(specialist_slug, session_id=run_id)
            
            prompt = prompt_builder(state)
            response = agent.query(prompt)
            updated_state: GraphState = {**state, state_key: response}
            self.record_step(
                updated_state,
                step_name or specialist_slug,
                {
                    "specialist": specialist_slug,
                    "prompt": prompt,
                    "output_key": state_key,
                },
            )
            return updated_state

        return node

    def make_approval_node(self, gate_name: str) -> Callable[[GraphState], GraphState]:
        """Create a graph node that enforces human approval."""

        def node(state: GraphState) -> GraphState:
            approved = self.require_approval(gate_name, state)
            self.record_step(
                state,
                gate_name,
                {"approved": approved},
            )
            if not approved:
                raise RuntimeError(f"Approval denied at gate: {gate_name}")
            approvals = state.setdefault("approvals", [])
            approvals.append(gate_name)
            return state

        return node

    def run_graph(
        self,
        graph: Any,
        initial_state: GraphState,
    ) -> GraphState:
        """Execute a compiled graph and persist structured logs."""
        state = dict(initial_state)
        # Ensure ID format matches tools.engine.state (UTC timestamp + hex UUID path safe)
        if "run_id" not in state:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            short_uuid = uuid.uuid4().hex[:8]
            state["run_id"] = f"{timestamp}_{short_uuid}"

        result: GraphState = graph.invoke(state)
        self._persist_log(result)
        return result

    def _persist_log(self, state: GraphState) -> None:
        """Write run metadata and steps to disk."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        run_id = state.get("run_id", "unknown")
        log_path = self.log_dir / f"{run_id}.json"
        log = {
            "run_id": run_id,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "steps": state.get("steps", []),
            "state": {k: v for k, v in state.items() if k not in {"steps"}},
        }
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)


def build_state_graph() -> StateGraph:
    """Helper to start a typed StateGraph."""
    return StateGraph(GraphState)
