import json
from pathlib import Path

import pytest

from spine.artifacts import new_ticket, new_work_item, read_meta, set_status
from spine.cli import main
from spine.errors import HumanInterventionRequired
from spine.events import content_revision
from spine.initcmd import init_target


def _to_reviewing(root: Path, wi: Path) -> None:
    set_status(root, str(wi), "doing")
    set_status(root, str(wi), "checking")
    (root / ".spine/evals" / f"{wi.stem}.md").write_text(
        f'passed: true\ncommand: uv run pytest -q\nwhen: "2026-09-19T00:00:00+00:00"\nrevision: {content_revision(wi)}\n',
        encoding="utf-8",
    )
    set_status(root, str(wi), "reviewing")
    (root / ".spine/reviews" / f"{wi.stem}.md").write_text(
        f'verdict: approve\nby: ada\nwhen: "2026-09-19T00:00:00+00:00"\nrevision: {content_revision(wi)}\nevidence: two-axis pass\n',
        encoding="utf-8",
    )


def test_human_gate_blocks_work_item_writes(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship it")
    _to_reviewing(tmp_path, wi)
    monkeypatch.delenv("SPINE_HUMAN", raising=False)

    with pytest.raises(HumanInterventionRequired):
        new_work_item(tmp_path, "Should not exist")
    assert not (tmp_path / "docs/spine/work-items/02-should-not-exist.md").exists()
    assert main(["new", "work-item", "--title", "From CLI"]) == 6
    assert not (tmp_path / "docs/spine/work-items/02-from-cli.md").exists()

    with pytest.raises(HumanInterventionRequired):
        set_status(tmp_path, str(wi), "done")
    assert read_meta(wi)[0]["Status"] == "reviewing"

    ticket = new_ticket(tmp_path, "A ticket")
    set_status(tmp_path, str(ticket), "resolved")
    assert read_meta(ticket)[0]["Status"] == "resolved"


def test_done_event_records_human(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship it")
    _to_reviewing(tmp_path, wi)
    set_status(tmp_path, str(wi), "done")
    lines = (tmp_path / ".spine" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    done = json.loads(lines[-1])
    assert done["from"] == "reviewing"
    assert done["to"] == "done"
    assert done["human"] is True
    earlier = [json.loads(line) for line in lines[:-1]]
    assert earlier
    assert all("human" not in ev for ev in earlier)
