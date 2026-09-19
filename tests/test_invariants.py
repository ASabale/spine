"""Cheap checks for the production invariants the phase tickets locked."""

import inspect
from pathlib import Path

from spine.artifacts import claim, new_ticket, new_work_item, resolve_artifact
from spine.errors import ClaimConflict
from spine.initcmd import init_target
from spine.query import next_lines, status_payload
from spine.store import CoordStore


def test_invariant_no_simultaneous_claims(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "One")
    claim(tmp_path, str(tk))
    monkeypatch.setenv("SPINE_USER", "bob")
    try:
        claim(tmp_path, str(tk))
        raise AssertionError("second claim must fail")
    except ClaimConflict:
        pass
    assert CoordStore(tmp_path).get_claim(str(tk.relative_to(tmp_path)))[0] == "ada"


def test_invariant_no_escape_from_target(tmp_path: Path):
    init_target(tmp_path)
    new_ticket(tmp_path, "Inside")
    outside = tmp_path / "nope.md"
    outside.write_text("x\n", encoding="utf-8")
    try:
        resolve_artifact(tmp_path, str(outside))
        raise AssertionError("escaped")
    except FileNotFoundError:
        pass


def test_invariant_engine_sqlite_free():
    import spine.engine as engine

    src = inspect.getsource(engine)
    assert "sqlite3" not in src
    assert "CoordStore" not in src


def test_invariant_human_and_machine_same_state(tmp_path: Path):
    init_target(tmp_path)
    new_ticket(tmp_path, "Open work")
    payload = status_payload(tmp_path)
    assert payload["next"] == next_lines(tmp_path)
    assert payload["run"][0]["cmd"] in "\n".join(payload["next"])
