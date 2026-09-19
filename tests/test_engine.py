from pathlib import Path

from spine.artifacts import new_work_item, read_meta, set_status
from spine.cli import main
from spine.engine import advance
from spine.errors import InvalidTransition
from spine.initcmd import init_target


def test_advance_idempotent(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    first = advance(tmp_path, str(wi), "doing")
    assert first.changed is True
    assert first.status == "doing"
    assert first.previous == "ready"
    second = advance(tmp_path, str(wi), "doing")
    assert second.changed is False
    assert second.status == "doing"
    assert read_meta(wi)[0]["Status"] == "doing"


def test_cli_illegal_transition_exits_3(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    assert main(["new", "work-item", "--title", "X"]) == 0
    assert main(["set-status", "01-x", "done"]) == 3


def test_advance_unknown_status_is_invalid_transition(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    try:
        advance(tmp_path, str(wi), "bogus")
        raise AssertionError("expected InvalidTransition")
    except InvalidTransition:
        pass
