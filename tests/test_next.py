from pathlib import Path

import pytest

from spine.artifacts import board, claim, new_ticket, new_work_item, next_lines, read_meta, release, set_status, write_meta
from spine.cli import main
from spine.doctor import doctor
from spine.errors import ClaimConflict, InvalidTransition
from spine.initcmd import init_target


def test_ticket_set_status_resolved(tmp_path: Path):
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Name it")
    claim(tmp_path, str(tk))
    set_status(tmp_path, str(tk), "resolved")
    assert read_meta(tk)[0]["Status"] == "resolved"


def test_ticket_set_status_open_claimed_resolved(tmp_path: Path):
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Full lifecycle")
    set_status(tmp_path, str(tk), "claimed")
    assert read_meta(tk)[0]["Status"] == "claimed"
    set_status(tmp_path, str(tk), "open")
    assert read_meta(tk)[0]["Status"] == "open"
    set_status(tmp_path, str(tk), "resolved")
    assert read_meta(tk)[0]["Status"] == "resolved"


def test_ticket_set_status_rejects_unknown_and_illegal(tmp_path: Path):
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Guarded")
    with pytest.raises(InvalidTransition):
        set_status(tmp_path, str(tk), "doing")
    set_status(tmp_path, str(tk), "resolved")
    with pytest.raises(InvalidTransition):
        set_status(tmp_path, str(tk), "open")


def test_claim_sets_ticket_claimed(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Claim me")
    claim(tmp_path, str(tk))
    meta, _ = read_meta(tk)
    assert meta["Status"] == "claimed"
    assert meta["Owner"] == "ada"
    assert meta["Claimed-at"]
    with pytest.raises(ClaimConflict, match="already claimed"):
        claim(tmp_path, str(tk))


def test_release_returns_ticket_to_open(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Release me")
    claim(tmp_path, str(tk))
    release(tmp_path, str(tk))
    meta, _ = read_meta(tk)
    assert meta["Status"] == "open"
    assert not meta.get("Owner")


def test_cli_ticket_set_status(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    new_ticket(tmp_path, "Verb path")
    tk = "docs/spine/tickets/01-verb-path.md"
    assert main(["set-status", tk, "claimed"]) == 0
    assert read_meta(tmp_path / tk)[0]["Status"] == "claimed"
    assert main(["set-status", tk, "reviewing"]) == 3

def test_next_prefers_inflight_over_ticket(tmp_path: Path):
    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    wi = new_work_item(tmp_path, "Ship")
    set_status(tmp_path, str(wi), "doing")
    text = "\n".join(next_lines(tmp_path))
    assert "checking" in text
    assert "claim" not in text


def test_next_inflight_order_comes_from_contract():
    import inspect

    from spine import query
    from spine.model import packaged_contract

    assert packaged_contract().inflight == [
        "reviewing",
        "checking",
        "doing",
        "changes-requested",
    ]
    src = inspect.getsource(query.next_lines)
    assert '["reviewing"' not in src.replace(" ", "")
    assert "inflight" in src


def test_next_ready_does_not_beat_open_ticket(tmp_path: Path):
    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    new_work_item(tmp_path, "Later")
    joined = "\n".join(next_lines(tmp_path))
    assert "01-open-work" in joined
    assert "doing" not in joined


def test_next_empty_map(tmp_path: Path):
    init_target(tmp_path)
    text = "\n".join(next_lines(tmp_path))
    assert "maps/map.md" in text


def test_board_has_cwd_and_next(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    out = board(tmp_path)
    assert "## Next" in out
    assert f"cwd: {tmp_path}" in out


def test_doctor_non_target(tmp_path: Path):
    msgs = doctor(tmp_path, apply=False)
    assert any("spine init" in m for m in msgs)


def test_next_claimed_ticket_answer_and_resolve(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Open work")
    claim(tmp_path, str(tk))
    joined = "\n".join(next_lines(tmp_path))
    assert "Answer" in joined
    assert "01-open-work" in joined
    assert "resolved" in joined


def test_cli_next_prints_only_commands(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["next"]) == 0
    out = capsys.readouterr().out
    assert "maps/map.md" in out
    assert "## Work items" not in out
    assert "# spine status" not in out


def test_cli_next_json_run_keys(tmp_path: Path, monkeypatch, capsys):
    import json

    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["next", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["cwd"] == str(tmp_path)
    assert data["next"]
    assert "run" in data
    assert all(x.startswith("spine ") for x in data["run"])


def test_cli_status_json_has_board(tmp_path: Path, monkeypatch, capsys):
    import json

    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    new_ticket(tmp_path, "Open work")
    capsys.readouterr()
    assert main(["status", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert any("01-open-work" in x for x in data["next"])
    assert data["frontier"]
    assert data["tickets"]


def test_cli_bare_prints_board(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "## Next" in out
    assert f"cwd: {tmp_path}" in out


def test_cli_doctor_prints_next(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "ok" in out
    assert "## Next" in out


def test_cli_doctor_json(tmp_path: Path, monkeypatch, capsys):
    import json

    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["doctor", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert "messages" in data
    assert "next" in data
    assert "run" in data


def test_cli_claim_no_target_claims_open_ticket(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    tk = new_ticket(tmp_path, "Open work")
    capsys.readouterr()
    assert main(["claim"]) == 0
    meta, _ = read_meta(tk)
    assert meta["Status"] == "claimed"
    assert meta["Owner"] == "ada"


def test_cli_claim_no_target_errors_when_nothing_to_claim(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["claim"]) == 1
    err = capsys.readouterr().err
    assert "nothing to claim" in err


def test_cli_show_prints_artifact(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    new_ticket(tmp_path, "Open work")
    capsys.readouterr()
    assert main(["show", "01-open-work"]) == 0
    out = capsys.readouterr().out
    assert "Open work" in out
    assert "Type:" in out
    assert main(["show", "missing-item"]) == 1


def test_status_json_includes_user(tmp_path: Path, monkeypatch, capsys):
    import json

    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["status", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["user"] == "ada"


def test_cli_claim_no_target_does_not_steal_ready_item(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    tk = new_ticket(tmp_path, "Open work")
    wi = new_work_item(tmp_path, "Later")
    claim(tmp_path, str(tk))
    capsys.readouterr()
    assert main(["claim"]) == 1
    meta, _ = read_meta(wi)
    assert not meta.get("Owner")


def test_cli_prime_json(tmp_path: Path, monkeypatch, capsys):
    import json

    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["prime"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["user"] == "ada"
    assert "messages" in data
    assert "hitl" in data
    assert "run" in data


def test_cli_prime_report_only_keeps_stale_claim(tmp_path: Path, monkeypatch, capsys):
    import json
    from datetime import datetime, timedelta, timezone

    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    tk = new_ticket(tmp_path, "Stale claim")
    claim(tmp_path, str(tk))
    meta, body = read_meta(tk)
    meta["Claimed-at"] = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    write_meta(tk, meta, body)
    capsys.readouterr()
    assert main(["prime", "--report-only"]) == 8
    data = json.loads(capsys.readouterr().out)
    assert any("STALE" in m for m in data["messages"])
    meta2, _ = read_meta(tk)
    assert meta2["Owner"] == "ada"


def test_next_json_hitl_on_empty_map(tmp_path: Path, monkeypatch, capsys):
    import json

    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["next", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["hitl"] is True
    assert data["run"] == []
    assert any("spine new" in x or "maps/map.md" in x for x in data["next"])


def test_status_json_includes_version(tmp_path: Path, monkeypatch, capsys):
    import json

    from spine import __version__

    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    capsys.readouterr()
    assert main(["status", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["version"] == __version__
