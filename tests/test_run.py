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
