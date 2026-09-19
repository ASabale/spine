from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from spine.artifacts import board, claim, link, new_ticket, new_work_item, read_meta, release, set_status, write_meta
from spine.cli import main
from spine.doctor import doctor
from spine.initcmd import init_target
from spine.model import load_contract


def test_contract_happy_path():
    c = load_contract()
    assert c.allowed("ready", "doing")
    assert not c.allowed("ready", "done")
    assert "reviewing" in c.software_required()


def test_init_and_machine(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    notes = init_target(tmp_path)
    assert (tmp_path / "docs/spine/README.md").exists()
    assert (tmp_path / "docs/spine/maps/map.md").exists()
    assert (tmp_path / ".spine/evals").is_dir()
    assert (tmp_path / ".agents/skills/wayfind/SKILL.md").exists()
    assert (tmp_path / ".claude/skills/build/SKILL.md").exists()
    assert ".spine/" in (tmp_path / ".gitignore").read_text()
    assert "mattpocock/skills" in (tmp_path / "docs/spine/wires.yaml").read_text()
    assert notes

    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "checking")
    with pytest.raises(ValueError):
        set_status(tmp_path, str(wi), "done")
    with pytest.raises(ValueError, match="evals"):
        set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text("ok\n", encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    set_status(tmp_path, str(wi), "changes-requested")
    set_status(tmp_path, str(wi), "doing")

    tk = new_ticket(tmp_path, "Name the thing")
    claim(tmp_path, str(tk))
    msgs = doctor(tmp_path)
    assert msgs


def test_cli_init(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    assert main(["status"]) == 0
    assert main(["new", "work-item", "--title", "First"]) == 0
    assert main(["set-status", "01-first", "doing"]) == 0
    assert main(["doctor"]) == 0
    assert main(["wire", "--pack", "mattpocock/skills"]) == 0


def test_cli_new_ticket_and_work_item(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    assert main(["new", "--title", "Both", "--ticket", "--work-item"]) == 0
    assert (tmp_path / "docs/spine/tickets/01-both.md").exists()
    assert (tmp_path / "docs/spine/work-items/01-both.md").exists()


def test_new_paths(tmp_path: Path):
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Decide license")
    wi = new_work_item(tmp_path, "Build init")
    assert tk.parent.name == "tickets"
    assert wi.parent.name == "work-items"
    assert "docs/spine" in str(tk)
    meta, _ = read_meta(tk)
    assert "Blocked by" in meta


def test_claim_conflict_and_release(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Claim me")
    claim(tmp_path, str(wi))
    monkeypatch.setenv("SPINE_USER", "bob")
    with pytest.raises(ValueError, match="already claimed"):
        claim(tmp_path, str(wi))
    release(tmp_path, str(wi))
    claim(tmp_path, str(wi))
    meta, _ = read_meta(wi)
    assert meta["Owner"] == "bob"


def test_doctor_releases_stale_claim(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Stale")
    claim(tmp_path, str(wi))
    meta, body = read_meta(wi)
    old = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    meta["Claimed-at"] = old
    write_meta(wi, meta, body)
    msgs = doctor(tmp_path, apply=True)
    assert any("STALE" in m or "FIX released" in m for m in msgs)
    meta, _ = read_meta(wi)
    assert not meta.get("Owner")


def test_link_bidirectional_and_doctor_drops_dangling(tmp_path: Path):
    init_target(tmp_path)
    a = new_work_item(tmp_path, "Alpha")
    b = new_work_item(tmp_path, "Beta")
    link(tmp_path, str(a), str(b))
    ma, _ = read_meta(a)
    mb, _ = read_meta(b)
    assert "work-items/02-beta.md" in ma["Links"] or "02-beta" in ma["Links"]
    assert "01-alpha" in mb["Links"]
    b.unlink()
    doctor(tmp_path, apply=True)
    ma, _ = read_meta(a)
    assert "02-beta" not in (ma.get("Links") or "")


def test_identity_prefers_spine_user(monkeypatch):
    from spine.artifacts import identity

    monkeypatch.setenv("SPINE_USER", "ada")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "git-author")
    monkeypatch.setenv("USER", "os-user")
    assert identity() == "ada"


def test_non_software_doing_to_done(tmp_path: Path):
    init_target(tmp_path)
    note = tmp_path / "note.md"
    note.write_text("ok\n", encoding="utf-8")
    wi = new_work_item(tmp_path, "Write a note", "default")
    meta, body = read_meta(wi)
    meta["Deliverable"] = "note.md"
    write_meta(wi, meta, body)
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "done")
    meta, _ = read_meta(wi)
    assert meta["Status"] == "done"


def test_non_software_doing_to_done_needs_deliverable(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Write a note", "default")
    set_status(tmp_path, str(wi), "doing")
    with pytest.raises(ValueError, match="Deliverable"):
        set_status(tmp_path, str(wi), "done")


def test_software_doing_to_done_rejected(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    with pytest.raises(ValueError):
        set_status(tmp_path, str(wi), "done")


def test_doctor_gitignore_is_report_only(tmp_path: Path):
    init_target(tmp_path)
    (tmp_path / ".gitignore").write_text("# other\n", encoding="utf-8")
    msgs = doctor(tmp_path, apply=True)
    assert any("REPORT gitignore" in m for m in msgs)
    assert ".spine/" not in (tmp_path / ".gitignore").read_text()


def test_board_shows_next_gate_and_frontier(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    new_ticket(tmp_path, "Open unblocked")
    blocked = new_ticket(tmp_path, "Later")
    meta, body = read_meta(blocked)
    meta["Blocked by"] = "01"
    write_meta(blocked, meta, body)
    text = board(tmp_path)
    assert "next=checking" in text
    assert "## Frontier" in text
    assert "01-open-unblocked.md" in text
    assert "02-later.md" not in text.split("## Frontier")[1]


def test_doctor_reports_contract_version_skew(tmp_path: Path):
    init_target(tmp_path)
    path = tmp_path / "docs/spine/contract.yaml"
    path.write_text(path.read_text().replace("version: 1", "version: 99"), encoding="utf-8")
    msgs = doctor(tmp_path, apply=False)
    assert any("contract version 99" in m for m in msgs)


def test_new_ticket_and_work_item_flags(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    assert main(["new", "--title", "Both", "--ticket", "--work-item"]) == 0
    assert (tmp_path / "docs/spine/tickets/01-both.md").exists()
    assert (tmp_path / "docs/spine/work-items/01-both.md").exists()


def test_software_needs_eval_and_review_proof(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "checking")
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text("eval\n", encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    with pytest.raises(ValueError, match="reviews"):
        set_status(tmp_path, str(wi), "done")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text("ship\n", encoding="utf-8")
    set_status(tmp_path, str(wi), "done")
    meta, _ = read_meta(wi)
    assert meta["Status"] == "done"


def test_doctor_reports_missing_spec_files(tmp_path: Path):
    init_target(tmp_path)
    (tmp_path / "docs/spine/README.md").unlink()
    msgs = doctor(tmp_path, apply=False)
    assert any("missing spec file" in m and "README.md" in m for m in msgs)


def test_install_cmd_uses_wired_skills():
    from spine.evolve import install_cmd, skills_for_pack, load_wires

    wires = load_wires(Path("/nonexistent-spine-root"))
    pack = wires["default_pack"]
    skills = skills_for_pack(wires, pack)
    cmd = install_cmd(pack, skills)
    assert "mattpocock/skills" in cmd
    assert "-s" in cmd
    assert "wayfinder" in cmd
    assert "code-review" in cmd
    assert "grill-with-docs" in cmd
    assert "handoff" in cmd
    from spine.evolve import pack_jobs
    jobs = pack_jobs(wires)
    packs = [p for p, _ in jobs]
    assert "vercel-labs/skills" in packs
    assert "obra/superpowers" in packs
    assert "anthropics/skills" in packs

