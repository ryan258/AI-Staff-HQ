#!/usr/bin/env python3
"""Rename legacy opaque log filenames to semantic names."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.engine.config import get_config
from tools.engine.utils import build_semantic_run_filename, extract_semantic_subject, normalize_slug


LEGACY_MARKDOWN_RE = re.compile(r"^\d{8}_\d{6}_[0-9a-f]{8}(?:_task_[A-Za-z0-9_-]+)?\.md$")
LEGACY_GRAPH_RE = re.compile(r"^\d{8}_\d{6}_[0-9a-f]{8}\.json$")
SESSION_HEADER_RE = re.compile(r"^# Session Log:\s*(.+)$", re.MULTILINE)
SPECIALIST_HEADER_RE = re.compile(r"^\*\*Specialist:\*\*\s*(.+)$", re.MULTILINE)
USER_BLOCK_RE = re.compile(r"### User\s*\n(.*?)(?:\n### Assistant|\Z)", re.DOTALL)


@dataclass
class RenameProposal:
    """Represents one filesystem rename."""

    source: Path
    target: Path


def parse_markdown_metadata(path: Path) -> tuple[str, str, str]:
    """Extract session id, specialist slug, and subject from a markdown log."""
    text = path.read_text(encoding="utf-8")

    session_match = SESSION_HEADER_RE.search(text)
    specialist_match = SPECIALIST_HEADER_RE.search(text)
    user_match = USER_BLOCK_RE.search(text)

    session_id = (session_match.group(1).strip() if session_match else path.stem)
    specialist_name = specialist_match.group(1).strip() if specialist_match else "specialist"
    specialist_slug = normalize_slug(specialist_name) or "specialist"
    subject = extract_semantic_subject(user_match.group(1) if user_match else text, fallback=session_id)

    return session_id, specialist_slug, subject


def infer_graph_workflow_name(payload: dict) -> str:
    """Infer a human-readable workflow name from graph log state."""
    state = payload.get("state", {})
    workflow_name = state.get("workflow_name")
    if workflow_name:
        return str(workflow_name)

    if state.get("user_brief"):
        return "planning-swarm"
    if state.get("strategy_plan") and state.get("results") is not None:
        return "cos-orchestration"
    if state.get("analysis") and state.get("technical_plan") and state.get("executive_brief"):
        return "strategy-tech-handoff"
    if state.get("analysis") and state.get("strategy") and state.get("executive_brief"):
        return "strategic-planning"
    if state.get("spec") and state.get("code") and state.get("qa_report"):
        return "code-feature"

    return "graph-run"


def parse_graph_metadata(path: Path) -> tuple[str, str, str]:
    """Extract run id, workflow name, and subject from a graph JSON log."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    state = payload.get("state", {})

    run_id = str(payload.get("run_id") or state.get("run_id") or path.stem)
    workflow_name = infer_graph_workflow_name(payload)
    subject = (
        state.get("log_title")
        or state.get("user_brief")
        or state.get("topic")
        or next((step.get("brief") for step in payload.get("steps", []) if step.get("brief")), "")
        or run_id
    )
    subject = extract_semantic_subject(str(subject), fallback=run_id)

    return run_id, workflow_name, subject


def build_markdown_proposal(path: Path) -> RenameProposal | None:
    """Build a semantic rename proposal for a legacy markdown log."""
    if not LEGACY_MARKDOWN_RE.match(path.name):
        return None

    session_id, specialist_slug, subject = parse_markdown_metadata(path)
    target = path.with_name(
        build_semantic_run_filename(
            run_id=session_id,
            subject=subject,
            workflow_name=specialist_slug,
            extension=".md",
        )
    )
    if target == path:
        return None
    return RenameProposal(source=path, target=target)


def build_graph_proposal(path: Path) -> RenameProposal | None:
    """Build a semantic rename proposal for a legacy graph log."""
    if not LEGACY_GRAPH_RE.match(path.name):
        return None

    run_id, workflow_name, subject = parse_graph_metadata(path)
    target = path.with_name(
        build_semantic_run_filename(
            run_id=run_id,
            subject=subject,
            workflow_name=workflow_name,
            extension=".json",
        )
    )
    if target == path:
        return None
    return RenameProposal(source=path, target=target)


def gather_proposals(workspace_md_dir: Path, graph_dir: Path, home_md_dir: Path) -> list[RenameProposal]:
    """Collect rename proposals across all supported legacy log locations."""
    proposals: list[RenameProposal] = []

    if workspace_md_dir.exists():
        for path in sorted(workspace_md_dir.glob("*.md")):
            proposal = build_markdown_proposal(path)
            if proposal:
                proposals.append(proposal)

    if graph_dir.exists():
        for path in sorted(graph_dir.glob("*.json")):
            proposal = build_graph_proposal(path)
            if proposal:
                proposals.append(proposal)

    if home_md_dir.exists():
        for path in sorted(home_md_dir.glob("*.md")):
            proposal = build_markdown_proposal(path)
            if proposal:
                proposals.append(proposal)

    return proposals


def apply_proposals(proposals: Iterable[RenameProposal], dry_run: bool = False) -> tuple[int, int]:
    """Apply or print rename proposals."""
    renamed = 0
    skipped = 0

    for proposal in proposals:
        if proposal.target.exists():
            print(f"SKIP {proposal.source} -> {proposal.target} (target exists)")
            skipped += 1
            continue

        print(f"RENAME {proposal.source} -> {proposal.target}")
        if not dry_run:
            proposal.source.rename(proposal.target)
        renamed += 1

    return renamed, skipped


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    config = get_config()

    parser = argparse.ArgumentParser(description="Rename legacy opaque log filenames to semantic names.")
    parser.add_argument(
        "--workspace-md-dir",
        type=Path,
        default=PROJECT_ROOT / "logs",
        help="Directory containing workspace markdown logs",
    )
    parser.add_argument(
        "--graph-dir",
        type=Path,
        default=PROJECT_ROOT / "logs" / "graphs",
        help="Directory containing graph JSON logs",
    )
    parser.add_argument(
        "--home-md-dir",
        type=Path,
        default=config.log_dir,
        help="Directory containing user-home markdown logs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print proposed renames without changing files",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    args = build_parser().parse_args()
    proposals = gather_proposals(args.workspace_md_dir, args.graph_dir, args.home_md_dir)
    renamed, skipped = apply_proposals(proposals, dry_run=args.dry_run)
    print(f"\nProcessed {len(proposals)} legacy logs: {renamed} renamed, {skipped} skipped")


if __name__ == "__main__":
    main()
