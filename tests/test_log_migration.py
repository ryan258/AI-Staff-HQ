"""Tests for legacy log migration helpers."""

import json

from tools.migrate_legacy_logs import build_graph_proposal, build_markdown_proposal


def test_build_markdown_proposal_uses_user_brief(tmp_path):
    """Legacy markdown migration should derive the subject from the embedded brief."""
    path = tmp_path / "20260329_023524_9c2c8515.md"
    path.write_text(
        """# Session Log: 20260329_023524_9c2c8515
**Specialist:** Chief of Staff
**Model:** mock/model

## Interaction @ 2026-03-29T02:35:46.439574+00:00
### User
You are coordinating a swarm of AI specialists to complete a complex request.

USER BRIEF:
R.I.P. Tequila is a parody liquor brand with a skeleton mob boss mascot.

AVAILABLE SPECIALISTS:
copywriter, chief-of-staff

### Assistant
[]
""",
        encoding="utf-8",
    )

    proposal = build_markdown_proposal(path)

    assert proposal is not None
    assert proposal.target.name == (
        "chief-of-staff__rip-tequila-is-a-parody-liquor-brand-with-a-skeleton__20260329_023524_9c2c8515.md"
    )


def test_build_markdown_proposal_preserves_task_session_suffix(tmp_path):
    """Task logs should keep their task suffix in the semantic filename."""
    path = tmp_path / "20260329_023524_9c2c8515_task_2.md"
    path.write_text(
        """# Session Log: 20260329_023524_9c2c8515_task_2
**Specialist:** Copywriter
**Model:** mock/model

## Interaction @ 2026-03-29T02:36:15.749083+00:00
### User
TASK: Write a premium sounding product description for a limited edition bottle.

### Assistant
Done
""",
        encoding="utf-8",
    )

    proposal = build_markdown_proposal(path)

    assert proposal is not None
    assert proposal.target.name == (
        "copywriter__write-a-premium-sounding-product-description-for-a__20260329_023524_9c2c8515_task_2.md"
    )


def test_build_graph_proposal_uses_brief_and_workflow(tmp_path):
    """Legacy graph migration should infer workflow and subject from JSON content."""
    path = tmp_path / "20260329_023524_9c2c8515.json"
    path.write_text(
        json.dumps(
            {
                "run_id": "20260329_023524_9c2c8515",
                "steps": [
                    {
                        "step": "planning",
                        "brief": "R.I.P. Tequila is a parody liquor brand with a skeleton mob boss mascot.",
                    }
                ],
                "state": {
                    "user_brief": "R.I.P. Tequila is a parody liquor brand with a skeleton mob boss mascot.",
                },
            }
        ),
        encoding="utf-8",
    )

    proposal = build_graph_proposal(path)

    assert proposal is not None
    assert proposal.target.name == (
        "planning-swarm__rip-tequila-is-a-parody-liquor-brand-with-a-skeleton__20260329_023524_9c2c8515.json"
    )
