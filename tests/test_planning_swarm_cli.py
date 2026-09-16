"""Provider-free checks for the public planning CLI outcome contract."""

import pytest
from workflows import planning_swarm


@pytest.mark.parametrize("status, expected", [("COMPLETED", 0), ("FAILED", 1), ("BLOCKED", 1), ("UNKNOWN", 1)])
def test_cli_exit_reflects_terminal_outcome(monkeypatch, capsys, status, expected):
    monkeypatch.setattr("sys.argv", ["planning_swarm.py", "brief"])
    monkeypatch.setattr(planning_swarm, "run_planning_swarm", lambda *args, **kwargs: {
        "status": status, "final_output": "retained result",
    })
    assert planning_swarm.main() == expected
    assert capsys.readouterr().out == "retained result\n"
