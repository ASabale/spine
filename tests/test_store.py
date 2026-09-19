from pathlib import Path

import pytest

from spine.errors import ClaimConflict
from spine.initcmd import init_target
from spine.store import CoordStore, FileStore



def test_filestore_roundtrip(tmp_path: Path):
    init_target(tmp_path)
    store = FileStore(tmp_path)
    path = tmp_path / "docs/spine/work-items/01-note.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    store.save(path, {"Type": "work-item", "Status": "ready"}, "## Intent\n\nnote\n")
    meta, body = store.load(path)
    assert meta["Status"] == "ready"
    assert "note" in body
    assert store.exists(path)
    listed = store.list_md(path.parent)
    assert path in listed


def test_filestore_atomic_write(tmp_path: Path):
    store = FileStore(tmp_path)
    path = tmp_path / "docs/spine/decisions/01.md"
    path.parent.mkdir(parents=True)
    store.atomic_write(path, "first\n")
    store.atomic_write(path, "second\n")
    assert path.read_text(encoding="utf-8") == "second\n"


def test_filestore_atomic_write_fsyncs():
    import inspect

    from spine.store import FileStore

    assert "fsync" in inspect.getsource(FileStore.atomic_write)


def test_coordstore_survives_reopen(tmp_path: Path):
    init_target(tmp_path)
    a = CoordStore(tmp_path)
    a.put("schema_version", "1")
    assert a.get("schema_version") == "1"
    b = CoordStore(tmp_path)
    assert b.get("schema_version") == "1"
    assert (tmp_path / ".spine" / "coord.db").exists()


def test_engine_does_not_import_sqlite():
    import inspect
    import spine.engine as engine

    src = inspect.getsource(engine)
    assert "sqlite3" not in src
    assert "CoordStore" not in src


def test_query_owns_next_and_board():
    import inspect

    import spine.artifacts as artifacts
    import spine.query as query

    assert query.next_lines is artifacts.next_lines
    assert query.board is artifacts.board
    assert query.status_payload is artifacts.status_payload
    src = inspect.getsource(artifacts)
    assert "def next_lines" not in src
    assert "def board" not in src
    assert "def status_payload" not in src


def test_coordstore_claims_one_winner(tmp_path: Path):
    init_target(tmp_path)
    a = CoordStore(tmp_path)
    a.take_claim("docs/spine/tickets/01.md", "ada", "2026-09-19T00:00:00+00:00")
    assert a.get_claim("docs/spine/tickets/01.md") == (
        "ada",
        "2026-09-19T00:00:00+00:00",
    )
    b = CoordStore(tmp_path)
    with pytest.raises(ClaimConflict, match="already claimed"):
        b.take_claim("docs/spine/tickets/01.md", "bob", "2026-09-19T00:00:01+00:00")
    assert b.get_claim("docs/spine/tickets/01.md")[0] == "ada"


def test_coordstore_drop_claim_owner_only(tmp_path: Path):
    init_target(tmp_path)
    store = CoordStore(tmp_path)
    store.take_claim("wi", "ada", "t")
    with pytest.raises(ClaimConflict, match="held by"):
        store.drop_claim("wi", owner="bob")
    assert store.get_claim("wi") == ("ada", "t")
    store.drop_claim("wi", owner="ada")
    assert store.get_claim("wi") is None


def test_coordstore_concurrent_one_winner(tmp_path: Path):
    import threading

    init_target(tmp_path)
    CoordStore(tmp_path)
    winners: list[str] = []
    losers: list[str] = []
    n = 8
    barrier = threading.Barrier(n)
    lock = threading.Lock()

    def worker(name: str) -> None:
        barrier.wait()
        store = CoordStore(tmp_path)
        try:
            store.take_claim("spec", name, "t")
            with lock:
                winners.append(name)
        except ClaimConflict:
            with lock:
                losers.append(name)

    threads = [threading.Thread(target=worker, args=(f"w{i}",)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(winners) == 1
    assert len(losers) == n - 1
    assert CoordStore(tmp_path).get_claim("spec")[0] == winners[0]


def test_coordstore_claims_use_immediate_lock():
    import inspect

    src = inspect.getsource(CoordStore)
    assert "CREATE TABLE IF NOT EXISTS claims" in src
    assert "BEGIN IMMEDIATE" in src

