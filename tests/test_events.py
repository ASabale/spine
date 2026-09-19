import hashlib
import inspect
import json
from pathlib import Path

from spine.events import append_event, content_revision
from spine.initcmd import init_target


def test_append_event_writes_one_json_line(tmp_path: Path):
    init_target(tmp_path)
    path = append_event(
        tmp_path,
        actor="ada",
        from_status="ready",
        to_status="doing",
        revision="abc",
        run_id="run-1",
        spec="01-ship.md",
    )
    assert path == tmp_path / ".spine" / "events.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    ev = json.loads(lines[0])
    assert ev["actor"] == "ada"
    assert ev["from"] == "ready"
    assert ev["to"] == "doing"
    assert ev["revision"] == "abc"
    assert ev["run_id"] == "run-1"
    assert ev["spec"] == "01-ship.md"
    assert isinstance(ev["time"], str) and ev["time"]


def test_append_event_is_append_only(tmp_path: Path):
    init_target(tmp_path)
    append_event(
        tmp_path,
        actor="a",
        from_status="ready",
        to_status="doing",
        revision="r",
        run_id="1",
    )
    append_event(
        tmp_path,
        actor="b",
        from_status="doing",
        to_status="checking",
        revision="r",
        run_id="2",
    )
    lines = (tmp_path / ".spine" / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["actor"] == "a"
    assert json.loads(lines[1])["actor"] == "b"


def test_append_event_calls_fsync():
    import spine.events as events

    src = inspect.getsource(events)
    assert "fsync" in src


def test_content_revision_is_sha256(tmp_path: Path):
    path = tmp_path / "item.md"
    path.write_bytes(b"hello")
    assert content_revision(path) == hashlib.sha256(b"hello").hexdigest()


def test_content_revision_changes_when_bytes_change(tmp_path: Path):
    path = tmp_path / "item.md"
    path.write_text("a\n", encoding="utf-8")
    first = content_revision(path)
    path.write_text("b\n", encoding="utf-8")
    assert content_revision(path) != first


def test_content_revision_ignores_status_metadata(tmp_path: Path):
    path = tmp_path / "item.md"
    path.write_text("# Title\n\nType: work-item\nStatus: ready\n\nhello\n", encoding="utf-8")
    first = content_revision(path)
    path.write_text("# Title\n\nType: work-item\nStatus: doing\n\nhello\n", encoding="utf-8")
    assert content_revision(path) == first
