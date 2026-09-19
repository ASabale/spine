from pathlib import Path

from spine.artifacts import claim, new_work_item, read_meta, set_status, write_meta
from spine.doctor import doctor
from spine.errors import ClaimConflict
from spine.events import content_revision
from spine.initcmd import init_target
from spine.model import load_contract
from spine.query import status_payload


REPO = Path(__file__).resolve().parent.parent


def test_this_repo_is_a_spine_target():
    c = load_contract(REPO)
    assert c.version == 1
    assert c.inflight
    payload = status_payload(REPO)
    assert payload["cwd"] == str(REPO)
    assert "run" in payload
    assert "next" in payload


def test_dogfood_full_route_crash_and_second_worker(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship the route")
    claim(tmp_path, str(wi))
    monkeypatch.setenv("SPINE_USER", "bob")
    try:
        claim(tmp_path, str(wi))
        raise AssertionError("bob must not steal ada's claim")
    except ClaimConflict:
        pass
    monkeypatch.setenv("SPINE_USER", "ada")
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "checking")
    meta, body = read_meta(wi)
    meta["Status"] = "ready"
    write_meta(wi, meta, body)
    assert read_meta(wi)[0]["Status"] == "ready"
    msgs = doctor(tmp_path, apply=True)
    assert any("FIX" in m and "event" in m.lower() for m in msgs)
    assert read_meta(wi)[0]["Status"] == "checking"
    digest = content_revision(wi)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(
        "passed: true\n"
        "command: uv run pytest -q\n"
        'when: "2026-09-19T00:00:00+00:00"\n'
        f"revision: {digest}\n",
        encoding="utf-8",
    )
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(
        "verdict: approve\n"
        "by: ada\n"
        'when: "2026-09-19T00:00:00+00:00"\n'
        f"revision: {digest}\n"
        "evidence: two-axis pass\n",
        encoding="utf-8",
    )
    set_status(tmp_path, str(wi), "done")
    assert read_meta(wi)[0]["Status"] == "done"
    log = (tmp_path / ".spine/events.jsonl").read_text(encoding="utf-8")
    assert "checking" in log
    assert "done" in log
