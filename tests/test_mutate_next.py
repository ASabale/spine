import json
from pathlib import Path

from spine.artifacts import new_ticket, new_work_item
from spine.cli import main
from spine.initcmd import init_target

def test_claim_prints_next(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    capsys.readouterr()
    assert main(["claim"]) == 0
    out = capsys.readouterr().out
    assert "## Next" in out
    assert "resolved" in out or "Answer" in out


def test_claim_json_prints_payload(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    capsys.readouterr()
    assert main(["claim", "--json"]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "run" in data
    assert "next" in data
    assert "user" in data
    assert "## Next" not in out


def test_set_status_prints_next(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    new_work_item(tmp_path, "Ship")
    capsys.readouterr()
    assert main(["set-status", "docs/spine/work-items/01-ship.md", "doing"]) == 0
    out = capsys.readouterr().out
    assert "## Next" in out
    assert "checking" in out


def test_set_status_json_prints_payload(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    new_work_item(tmp_path, "Ship")
    capsys.readouterr()
    assert main(["set-status", "docs/spine/work-items/01-ship.md", "doing", "--json"]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "run" in data
    assert "next" in data
    assert "user" in data
    assert "## Next" not in out


def test_new_prints_next(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    capsys.readouterr()
    assert main(["new", "ticket", "--title", "X"]) == 0
    out = capsys.readouterr().out
    assert "## Next" in out
    assert "claim" in out


def test_new_json_prints_payload(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    capsys.readouterr()
    assert main(["new", "ticket", "--title", "X", "--json"]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "run" in data
    assert "next" in data
    assert "## Next" not in out


def test_release_prints_next(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Open work")
    assert main(["claim", str(tk)]) == 0
    capsys.readouterr()
    assert main(["release", str(tk)]) == 0
    out = capsys.readouterr().out
    assert "## Next" in out
    assert "claim" in out


def test_release_json_prints_payload(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Open work")
    assert main(["claim", str(tk)]) == 0
    capsys.readouterr()
    assert main(["release", str(tk), "--json"]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "run" in data
    assert "next" in data
    assert "## Next" not in out


def test_link_prints_next(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    a = new_ticket(tmp_path, "Alpha")
    b = new_ticket(tmp_path, "Beta")
    capsys.readouterr()
    assert main(["link", str(a), str(b)]) == 0
    out = capsys.readouterr().out
    assert "linked" in out
    assert "## Next" in out


def test_link_json_prints_payload(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    a = new_ticket(tmp_path, "Alpha")
    b = new_ticket(tmp_path, "Beta")
    capsys.readouterr()
    assert main(["link", str(a), str(b), "--json"]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "run" in data
    assert "next" in data
    assert "## Next" not in out
