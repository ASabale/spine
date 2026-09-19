from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Protocol

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
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)


class CoordStore:
    """SQLite coordination DB at <root>/.spine/coord.db. Key/value for now; claims table in ticket 10."""

    def __init__(self, root: Path):
        folder = root / EXEC_ROOT
        folder.mkdir(parents=True, exist_ok=True)
        self.path = folder / "coord.db"
        self._conn = sqlite3.connect(self.path)
        self._conn.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self._conn.commit()

    def get(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return None if row is None else row[0]

    def put(self, key: str, value: str) -> None:
        self._conn.execute("INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)", (key, value))
        self._conn.commit()
