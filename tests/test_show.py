import json
from pathlib import Path

from spine.artifacts import new_ticket, new_work_item
from spine.cli import main
from spine.engine import advance
from spine.initcmd import init_target


def test_show_json_frontmatter(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    capsys.readouterr()
    assert main(["show", "01-open-work", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["file"].endswith("01-open-work.md")
    assert data["meta"]["Status"] == "open"
    assert "body" in data
    assert main(["show", "missing-item", "--json"]) == 1


def test_show_prints_the_last_reason(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship it")
    advance(tmp_path, str(wi.relative_to(tmp_path)), "doing", reason="because")
    capsys.readouterr()
    assert main(["show", wi.name]) == 0
    out = capsys.readouterr().out
    assert "reason: because" in out.splitlines()
    log = (tmp_path / ".spine" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ev = json.loads(log[-1])
    assert ev["reason"] == "because"
    assert ev["op"] == "status"
