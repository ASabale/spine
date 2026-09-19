from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

from spine.artifacts import claim, new_work_item, read_meta, write_meta
from spine.cli import main
from spine.initcmd import init_target


def test_prime_report_only_keeps_stale_owner(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Stale")
    claim(tmp_path, str(wi))
    meta, body = read_meta(wi)
    meta["Claimed-at"] = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    write_meta(wi, meta, body)
    capsys.readouterr()
    assert main(["prime", "--report-only"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert any("STALE" in m for m in data["messages"])
    meta, _ = read_meta(wi)
    assert meta.get("Owner") == "ada"



def test_prime_ok_true_after_init(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    capsys.readouterr()
    assert main(["prime"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert "version" in data


def test_prime_ok_false_on_broken_blocker(tmp_path: Path, monkeypatch, capsys):
    from spine.artifacts import new_ticket, write_meta, read_meta

    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    later = new_ticket(tmp_path, "Later")
    meta, body = read_meta(later)
    meta["Blocked by"] = "99"
    write_meta(later, meta, body)
    capsys.readouterr()
    assert main(["prime", "--report-only"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is False
    assert any("BROKEN" in m for m in data["messages"])


def test_prime_json_inited_true_after_init(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    capsys.readouterr()
    assert main(["prime"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["inited"] is True


def test_prime_json_includes_cwd(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    capsys.readouterr()
    assert main(["prime"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert Path(data["cwd"]).resolve() == tmp_path.resolve()


def test_prime_report_only_inited_false_on_empty_dir(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    capsys.readouterr()
    assert main(["prime", "--report-only"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["inited"] is False
    assert data["ok"] is False
