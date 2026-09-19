from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Protocol

from spine.errors import ClaimConflict
from spine.model import EXEC_ROOT, dump_front, parse_front



class ArtifactStore(Protocol):
    def load(self, path: Path) -> tuple[dict[str, str], str]: ...
    def save(self, path: Path, meta: dict[str, str], body: str) -> None: ...
    def exists(self, path: Path) -> bool: ...
    def list_md(self, folder: Path) -> list[Path]: ...
    def atomic_write(self, path: Path, text: str) -> None: ...


class FileStore:
    def __init__(self, root: Path):
        self.root = root

    def load(self, path: Path) -> tuple[dict[str, str], str]:
        return parse_front(path.read_text(encoding="utf-8"))

    def save(self, path: Path, meta: dict[str, str], body: str) -> None:
        title = meta.get("Title") or path.stem
        self.atomic_write(path, dump_front(meta, body, title=title))

    def exists(self, path: Path) -> bool:
        return path.exists()

    def list_md(self, folder: Path) -> list[Path]:
        if not folder.is_dir():
            return []
        return sorted(p for p in folder.glob("*.md") if p.is_file())

    def atomic_write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        tmp.replace(path)


class CoordStore:
    """SQLite coordination DB at <root>/.spine/coord.db."""

    def __init__(self, root: Path):
        folder = root / EXEC_ROOT
        folder.mkdir(parents=True, exist_ok=True)
        self.path = folder / "coord.db"
        self._conn = sqlite3.connect(self.path, timeout=30.0, isolation_level=None)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=30000")
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS claims ("
            " spec TEXT PRIMARY KEY,"
            " owner TEXT NOT NULL,"
            " claimed_at TEXT NOT NULL)"
        )

    def get(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return None if row is None else row[0]

    def put(self, key: str, value: str) -> None:
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)", (key, value)
            )
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def get_claim(self, spec: str) -> tuple[str, str] | None:
        row = self._conn.execute(
            "SELECT owner, claimed_at FROM claims WHERE spec = ?", (spec,)
        ).fetchone()
        return None if row is None else (row[0], row[1])

    def take_claim(self, spec: str, owner: str, claimed_at: str) -> None:
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            self._conn.execute(
                "INSERT INTO claims (spec, owner, claimed_at) VALUES (?, ?, ?)",
                (spec, owner, claimed_at),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            self._conn.rollback()
            row = self.get_claim(spec)
            if row:
                raise ClaimConflict(f"already claimed by {row[0]} at {row[1]}") from exc
            raise ClaimConflict(f"already claimed: {spec}") from exc
        except Exception:
            self._conn.rollback()
            raise

    def drop_claim(self, spec: str, *, owner: str | None = None, force: bool = False) -> None:
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            row = self._conn.execute(
                "SELECT owner, claimed_at FROM claims WHERE spec = ?", (spec,)
            ).fetchone()
            if row is None:
                self._conn.commit()
                return
            if not force and owner is not None and row[0] != owner:
                self._conn.rollback()
                raise ClaimConflict(f"held by {row[0]}, not {owner}")
            self._conn.execute("DELETE FROM claims WHERE spec = ?", (spec,))
            self._conn.commit()
        except ClaimConflict:
            raise
        except Exception:
            self._conn.rollback()
            raise

