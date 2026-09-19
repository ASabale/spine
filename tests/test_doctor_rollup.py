from pathlib import Path

from spine.artifacts import new_ticket, new_work_item, read_meta, write_meta
from spine.cli import main
from spine.doctor import doctor, doctor_ok
from spine.events import append_event
from spine.initcmd import init_target


def test_doctor_reports_and_clears_missing_blocker(tmp_path: Path):
    init_target(tmp_path)
    later = new_ticket(tmp_path, "Later")
    meta, body = read_meta(later)
    meta["Blocked by"] = "99"
    write_meta(later, meta, body)
    msgs = doctor(tmp_path, apply=False)
    assert any("BROKEN blocker" in m and later.name in m for m in msgs)
    meta, _ = read_meta(later)
    assert meta.get("Blocked by") == "99"
    msgs = doctor(tmp_path, apply=True)
    assert any("FIX cleared Blocked by" in m for m in msgs)
    meta, _ = read_meta(later)
    assert not (meta.get("Blocked by") or "").strip()


def test_doctor_keeps_existing_blocker(tmp_path: Path):
    init_target(tmp_path)
    new_ticket(tmp_path, "First")
    later = new_ticket(tmp_path, "Later")
    meta, body = read_meta(later)
    meta["Blocked by"] = "01"
    write_meta(later, meta, body)
    doctor(tmp_path, apply=True)
    meta, _ = read_meta(later)
    assert meta.get("Blocked by") == "01"


def test_doctor_keeps_blocker_named_by_filename(tmp_path: Path):
    init_target(tmp_path)
    first = new_ticket(tmp_path, "First")
    later = new_ticket(tmp_path, "Later")
    meta, body = read_meta(later)
    meta["Blocked by"] = first.name
    write_meta(later, meta, body)
    doctor(tmp_path, apply=True)
    meta, _ = read_meta(later)
    assert meta.get("Blocked by") == first.name


def test_doctor_keeps_blocker_named_by_path(tmp_path: Path):
    init_target(tmp_path)
    first = new_ticket(tmp_path, "First")
    later = new_ticket(tmp_path, "Later")
    rel = str(first.relative_to(tmp_path))
    meta, body = read_meta(later)
    meta["Blocked by"] = rel
    write_meta(later, meta, body)
    doctor(tmp_path, apply=True)
    meta, _ = read_meta(later)
    assert meta.get("Blocked by") == rel


def test_doctor_clears_resolved_blocker(tmp_path: Path):
    init_target(tmp_path)
    first = new_ticket(tmp_path, "First")
    later = new_ticket(tmp_path, "Later")
    meta, body = read_meta(first)
    meta["Status"] = "resolved"
    write_meta(first, meta, body)
    meta, body = read_meta(later)
    meta["Blocked by"] = "01"
    write_meta(later, meta, body)
    msgs = doctor(tmp_path, apply=False)
    assert any("resolved" in m.lower() and later.name in m for m in msgs)
    meta, _ = read_meta(later)
    assert meta.get("Blocked by") == "01"
    msgs = doctor(tmp_path, apply=True)
    assert any("FIX cleared Blocked by" in m for m in msgs)
    meta, _ = read_meta(later)
    assert not (meta.get("Blocked by") or "").strip()


def test_doctor_resets_unknown_work_item_status(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI")
    meta, body = read_meta(wi)
    meta["Status"] = "backlog"
    write_meta(wi, meta, body)
    msgs = doctor(tmp_path, apply=False)
    assert any("unknown status backlog" in m and wi.name in m for m in msgs)
    meta, _ = read_meta(wi)
    assert meta["Status"] == "backlog"
    msgs = doctor(tmp_path, apply=True)
    assert any("FIX" in m and "status" in m.lower() and wi.name in m for m in msgs)
    meta, _ = read_meta(wi)
    assert meta["Status"] == "ready"
    msgs = doctor(tmp_path, apply=True)
    assert not any("FIX" in m and "status" in m.lower() and wi.name in m for m in msgs)


def test_doctor_resets_illegal_ticket_status(tmp_path: Path):
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Name it")
    meta, body = read_meta(tk)
    meta["Status"] = "doing"
    write_meta(tk, meta, body)
    msgs = doctor(tmp_path, apply=True)
    assert any("FIX" in m and "status" in m.lower() and tk.name in m for m in msgs)
    meta, _ = read_meta(tk)
    assert meta["Status"] == "open"


def test_doctor_restores_status_from_event_log(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI")
    append_event(
        tmp_path,
        from_status="ready",
        to_status="doing",
        spec=wi.name,
    )
    meta, body = read_meta(wi)
    meta["Status"] = "checking"
    write_meta(wi, meta, body)
    msgs = doctor(tmp_path, apply=False)
    assert any("event" in m.lower() and wi.name in m for m in msgs)
    meta, _ = read_meta(wi)
    assert meta["Status"] == "checking"
    msgs = doctor(tmp_path, apply=True)
    assert any("FIX" in m and "event" in m.lower() and wi.name in m for m in msgs)
    meta, _ = read_meta(wi)
    assert meta["Status"] == "doing"
    msgs = doctor(tmp_path, apply=True)
    assert not any("FIX" in m and "event" in m.lower() and wi.name in m for m in msgs)


def test_doctor_ok_true_after_apply_repairs_blocker(tmp_path: Path):
    init_target(tmp_path)
    later = new_ticket(tmp_path, "Later")
    meta, body = read_meta(later)
    meta["Blocked by"] = "99"
    write_meta(later, meta, body)
    assert doctor_ok(doctor(tmp_path, apply=False)) is False
    assert doctor_ok(doctor(tmp_path, apply=True)) is True


def test_cli_doctor_report_only_exits_8(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    later = new_ticket(tmp_path, "Later")
    meta, body = read_meta(later)
    meta["Blocked by"] = "99"
    write_meta(later, meta, body)
    assert main(["doctor", "--report-only"]) == 8


def test_cli_doctor_apply_exits_0_after_repair(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    later = new_ticket(tmp_path, "Later")
    meta, body = read_meta(later)
    meta["Blocked by"] = "99"
    write_meta(later, meta, body)
    assert main(["doctor"]) == 0
    meta, _ = read_meta(later)
    assert not (meta.get("Blocked by") or "").strip()


def test_doctor_fix_line_has_before_after_why(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI")
    meta, body = read_meta(wi)
    meta["Status"] = "backlog"
    write_meta(wi, meta, body)
    msgs = doctor(tmp_path, apply=True)
    fix = next(m for m in msgs if m.startswith("FIX status") and wi.name in m)
    assert "backlog" in fix
    assert "ready" in fix
    assert "(" in fix and ")" in fix
