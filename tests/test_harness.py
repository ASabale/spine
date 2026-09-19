from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from spine.artifacts import (
    claim,
    new_ticket,
    new_work_item,
    read_meta,
    release,
    resolve_artifact,
    set_status,
)
from spine.errors import ClaimConflict
from spine.initcmd import init_target
from spine.query import next_lines
from spine.store import CoordStore


def test_resolve_rejects_path_escape(tmp_path: Path):
    init_target(tmp_path)
    new_ticket(tmp_path, "Inside")
    outside = tmp_path / "secret.md"
    outside.write_text("nope\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        resolve_artifact(tmp_path, str(outside))
    with pytest.raises(FileNotFoundError):
        resolve_artifact(tmp_path, "secret.md")
    inside = resolve_artifact(tmp_path, "01-inside")
    assert inside.parent.name == "tickets"


def test_concurrent_mint_unique_ids(tmp_path: Path):
    init_target(tmp_path)
    n = 20
    barrier = threading.Barrier(n)
    errors: list[BaseException] = []

    def worker(i: int) -> None:
        try:
            barrier.wait()
            new_work_item(tmp_path, f"Item {i}")
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    files = sorted((tmp_path / "docs/spine/work-items").glob("*.md"))
    assert len(files) == n
    nums = [int(p.name.split("-", 1)[0]) for p in files]
    assert len(set(nums)) == n


def test_fifty_workers_one_winner(tmp_path: Path, monkeypatch):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Hot")
    monkeypatch.setattr(
        "spine.artifacts.identity", lambda: threading.current_thread().name
    )
    n = 50
    barrier = threading.Barrier(n)
    winners: list[str] = []
    losers: list[str] = []
    lock = threading.Lock()

    def worker() -> None:
        barrier.wait()
        try:
            claim(tmp_path, str(wi))
            with lock:
                winners.append(threading.current_thread().name)
        except ClaimConflict:
            with lock:
                losers.append(threading.current_thread().name)

    threads = [
        threading.Thread(target=worker, name=f"w{i:02d}") for i in range(n)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(winners) == 1
    assert len(losers) == n - 1
    meta, _ = read_meta(wi)
    assert meta["Owner"] == winners[0]
    rel = str(wi.relative_to(tmp_path))
    assert CoordStore(tmp_path).get_claim(rel)[0] == winners[0]



def test_fifty_workers_claim_advance_release(tmp_path: Path, monkeypatch):
    init_target(tmp_path)
    items = [new_work_item(tmp_path, f"Work {i:02d}") for i in range(50)]
    monkeypatch.setattr(
        "spine.artifacts.identity", lambda: threading.current_thread().name
    )
    barrier = threading.Barrier(50)
    errors: list[str] = []

    def worker(path: Path) -> None:
        barrier.wait()
        try:
            claim(tmp_path, str(path))
            set_status(tmp_path, str(path), "doing")
            set_status(tmp_path, str(path), "checking")
            release(tmp_path, str(path))
        except BaseException as exc:  # noqa: BLE001
            errors.append(f"{path.name}: {exc}")


    threads = [
        threading.Thread(target=worker, args=(path,), name=f"w{i:02d}") for i, path in enumerate(items)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    owners = []
    for path in items:
        meta, _ = read_meta(path)
        assert meta["Status"] == "checking"
        owners.append(meta.get("Owner") or "")
        assert not meta.get("Owner")
    store = CoordStore(tmp_path)
    for path in items:
        assert store.get_claim(str(path.relative_to(tmp_path))) is None
    log = tmp_path / ".spine" / "events.jsonl"
    lines = [ln for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 100
    for ln in lines:
        json.loads(ln)


def test_next_and_claim_at_100k(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    folder = tmp_path / "docs/spine/work-items"
    (folder / "000000-hot.md").write_text(
        "# Hot\n\nType: work-item\nProfile: software\nStatus: reviewing\n"
        "Owner: \nClaimed-at: \nLinks: \nDeliverable: \n\n## Intent\n\nhot\n",
        encoding="utf-8",
    )
    done = (
        "# n\n\nType: work-item\nProfile: software\nStatus: done\n"
        "Owner: \nClaimed-at: \nLinks: \nDeliverable: \n\n## Intent\n\nn\n"
    )
    for i in range(1, 100_000):
        (folder / f"{i:06d}-bulk.md").write_text(done, encoding="utf-8")
    t0 = time.perf_counter()
    lines = next_lines(tmp_path)
    next_ms = (time.perf_counter() - t0) * 1000
    assert any("reviews" in line or "set-status" in line for line in lines), lines
    assert next_ms < 500, f"next took {next_ms:.1f}ms"
    tk = new_ticket(tmp_path, "Claim bench")
    t0 = time.perf_counter()
    claim(tmp_path, str(tk))
    claim_ms = (time.perf_counter() - t0) * 1000
    assert claim_ms < 100, f"claim took {claim_ms:.1f}ms"
    assert read_meta(tk)[0]["Owner"] == "ada"

