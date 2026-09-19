from pathlib import Path

from spine.artifacts import new_ticket
from spine.cli import main
from spine.initcmd import init_target


def test_run_prints_claim(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    capsys.readouterr()
    assert main(["run"]) == 0
    out = capsys.readouterr().out.strip()
    assert out.startswith("spine claim")
    assert "01-open-work" in out


def test_run_exits_2_on_hitl(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    capsys.readouterr()
    assert main(["run"]) == 2
    err = capsys.readouterr().err
    assert "error:" in err


def test_run_after_claim_prints_set_status(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    capsys.readouterr()
    assert main(["claim"]) == 0
    capsys.readouterr()
    assert main(["run"]) == 0
    out = capsys.readouterr().out.strip()
    assert out == "spine set-status docs/spine/tickets/01-open-work.md resolved"
    assert "set-status" in out
    assert "resolved" in out


def test_status_run_is_structured_plan(tmp_path: Path):
    from spine.query import status_payload

    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    payload = status_payload(tmp_path)
    assert payload["hitl"] is False
    assert payload["run"] == [
        {"cmd": "spine claim docs/spine/tickets/01-open-work.md", "hitl": False},
    ]
    again = status_payload(tmp_path)
    assert again["run"] == payload["run"]
    assert again["next"] == payload["next"]


def test_status_run_empty_when_hitl_only(tmp_path: Path):
    from spine.query import status_payload

    init_target(tmp_path)
    payload = status_payload(tmp_path)
    assert payload["run"] == []
    assert payload["hitl"] is True
    assert any("maps/map.md" in line for line in payload["next"])


def test_run_plan_not_inline_string_filter():
    import inspect

    from spine import query

    src = inspect.getsource(query.status_payload).replace(" ", "")
    assert 'startswith("spine")' not in src
    assert '"..."notin' not in src

