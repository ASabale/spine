from pathlib import Path

import pytest

from spine.artifacts import new_work_item, read_meta, set_status, write_meta
from spine.cli import main
from spine.errors import ReviewInvalid
from spine.events import content_revision
from spine.initcmd import init_target


def _proofs(root: Path, wi: Path, *, by: str) -> None:
    (root / ".spine/evals" / f"{wi.stem}.md").write_text(
        f'passed: true\ncommand: uv run pytest -q\nwhen: "2026-09-19T00:00:00+00:00"\nrevision: {content_revision(wi)}\n',
        encoding="utf-8",
    )
    (root / ".spine/reviews" / f"{wi.stem}.md").write_text(
        f'verdict: approve\nby: {by}\nwhen: "2026-09-19T00:00:00+00:00"\nrevision: {content_revision(wi)}\nevidence: two-axis pass\n',
        encoding="utf-8",
    )


def _to_reviewing(root: Path, wi: Path, *, by: str) -> None:
    set_status(root, str(wi), "doing")
    set_status(root, str(wi), "checking")
    _proofs(root, wi, by=by)
    set_status(root, str(wi), "reviewing")


def _set_owner(wi: Path, owner: str) -> None:
    meta, body = read_meta(wi)
    meta["Owner"] = owner
    write_meta(wi, meta, body)


def test_software_owner_cannot_approve(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    _to_reviewing(tmp_path, wi, by="ada")
    _set_owner(wi, "ada")
    with pytest.raises(ReviewInvalid, match="self-approval"):
        set_status(tmp_path, str(wi), "done")
    assert read_meta(wi)[0]["Status"] == "reviewing"
    assert main(["set-status", wi.name, "done"]) == 5
    assert read_meta(wi)[0]["Status"] == "reviewing"


def test_software_other_reviewer_reaches_done(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    _to_reviewing(tmp_path, wi, by="bob")
    _set_owner(wi, "ada")
    set_status(tmp_path, str(wi), "done")
    assert read_meta(wi)[0]["Status"] == "done"


def test_non_software_owner_may_approve(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Write a note", "default")
    _to_reviewing(tmp_path, wi, by="ada")
    _set_owner(wi, "ada")
    set_status(tmp_path, str(wi), "done")
    assert read_meta(wi)[0]["Status"] == "done"


def test_software_self_approval_can_be_turned_on(tmp_path: Path):
    init_target(tmp_path)
    contract = tmp_path / "docs/spine/contract.yaml"
    text = contract.read_text(encoding="utf-8").replace(
        "self_approval: false", "self_approval: true", 1
    )
    contract.write_text(text, encoding="utf-8")
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    _to_reviewing(tmp_path, wi, by="ada")
    _set_owner(wi, "ada")
    set_status(tmp_path, str(wi), "done")
    assert read_meta(wi)[0]["Status"] == "done"
