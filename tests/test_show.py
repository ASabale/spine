from pathlib import Path
import json

from spine.artifacts import new_ticket
from spine.cli import main
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
