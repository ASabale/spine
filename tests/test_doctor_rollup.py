from pathlib import Path

from spine.artifacts import new_ticket, read_meta, write_meta
from spine.doctor import doctor
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

