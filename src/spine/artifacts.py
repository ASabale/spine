from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from spine.errors import ClaimConflict

from spine.model import (
    EXEC_ROOT,
    SPEC_ROOT,
    dump_front,
    load_contract,
)

from spine.store import CoordStore, FileStore


def _now() -> datetime:
    return datetime.now(timezone.utc)


def identity() -> str:
    env = os.environ.get("SPINE_USER") or os.environ.get("GIT_AUTHOR_NAME")
    if env:
        return env
    try:
        proc = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True,
            text=True,
            check=False,
        )
        name = (proc.stdout or "").strip()
        if proc.returncode == 0 and name:
            return name
    except OSError:
        pass
    return os.environ.get("USER") or "unknown"


def _slug(title: str) -> str:
    s = "".join(ch.lower() if ch.isalnum() else "-" for ch in title).strip("-")
    while "--" in s:
        s = s.replace("--", "-")
    return s or "item"


def _file_max(folder: Path) -> int:
    n = 0
    if not folder.exists():
        return 0
    for p in folder.glob("*.md"):
        head = p.name.split("-", 1)[0]
        if head.isdigit():
            n = max(n, int(head))
    return n


def _next_number(root: Path, folder: Path, kind: str) -> int:
    return CoordStore(root).allocate_id(kind, floor=_file_max(folder))


def new_ticket(root: Path, title: str, typ: str = "grilling") -> Path:
    folder = root / SPEC_ROOT / "tickets"
    folder.mkdir(parents=True, exist_ok=True)
    num = _next_number(root, folder, "tickets")
    path = folder / f"{num:02d}-{_slug(title)}.md"
    body = f"## Question\n\n{title}\n"
    text = dump_front(
        {"Type": typ, "Status": "open", "Blocked by": "", "Owner": "", "Claimed-at": ""},
        body,
        title=title,
    )
    path.write_text(text, encoding="utf-8")
    return path


def new_work_item(root: Path, title: str, profile: str = "software") -> Path:
    folder = root / SPEC_ROOT / "work-items"
    folder.mkdir(parents=True, exist_ok=True)
    num = _next_number(root, folder, "work-items")
    path = folder / f"{num:02d}-{_slug(title)}.md"
    body = f"## Intent\n\n{title}\n"
    text = dump_front(
        {
            "Type": "work-item",
            "Profile": profile,
            "Status": "ready",
            "Owner": "",
            "Claimed-at": "",
            "Links": "",
            "Deliverable": "",
        },
        body,
        title=title,
    )
    path.write_text(text, encoding="utf-8")
    return path


def _under_spec(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to((root / SPEC_ROOT).resolve())
        return True
    except ValueError:
        return False


def resolve_artifact(root: Path, spec: str) -> Path:
    root = root.resolve()
    p = Path(spec)
    cand = p if p.is_absolute() else root / spec
    if cand.exists() and _under_spec(root, cand):
        return cand.resolve()
    for folder in ("work-items", "tickets"):
        d = root / SPEC_ROOT / folder
        if d.exists():
            for f in d.glob("*.md"):
                if spec in f.name or spec in f.stem:
                    return f
    raise FileNotFoundError(spec)


def read_meta(path: Path) -> tuple[dict[str, str], str]:
    return FileStore(path.parent).load(path)


def write_meta(path: Path, meta: dict[str, str], body: str) -> None:
    FileStore(path.parent).save(path, meta, body)


def _deliverable_exists(root: Path, meta: dict[str, str]) -> bool:
    dest = (meta.get("Deliverable") or "").strip()
    if not dest:
        return False
    p = Path(dest)
    return (root / dest).exists() or p.exists()


def _has_proof(root: Path, kind: str, stem: str) -> bool:
    folder = root / EXEC_ROOT / kind
    if not folder.is_dir():
        return False
    return any(p.is_file() and (stem in p.name or p.stem == stem) for p in folder.iterdir())


def _is_ticket(path: Path, meta: dict[str, str]) -> bool:
    if path.parent.name == "tickets":
        return True
    return (meta.get("Type") or "") in {"research", "prototype", "grilling", "task"}


def set_status(root: Path, spec: str, nxt: str) -> Path:
    from spine.engine import advance

    return advance(root, spec, nxt).path


def claim(root: Path, spec: str) -> Path:
    path = resolve_artifact(root, spec)
    meta, body = read_meta(path)
    key = str(path.relative_to(root))
    store = CoordStore(root)
    row = store.get_claim(key)
    owner = (row[0] if row else meta.get("Owner") or "")
    claimed_at = (row[1] if row else meta.get("Claimed-at") or "")
    if owner and claimed_at and not _stale(claimed_at, root=root):
        raise ClaimConflict(f"already claimed by {owner} at {claimed_at}")
    if row:
        store.drop_claim(key, force=True)
    me = identity()
    now = _now().isoformat()
    store.take_claim(key, me, now)
    meta["Owner"] = me
    meta["Claimed-at"] = now
    if meta.get("Status") == "open":
        meta["Status"] = "claimed"
    write_meta(path, meta, body)
    runtime = root / EXEC_ROOT / "claims" / f"{path.stem}.claim"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text(f"{meta['Owner']}\n{meta['Claimed-at']}\n", encoding="utf-8")
    return path


def release(root: Path, spec: str, *, force: bool = False) -> Path:
    path = resolve_artifact(root, spec)
    meta, body = read_meta(path)
    key = str(path.relative_to(root))
    store = CoordStore(root)
    row = store.get_claim(key)
    me = identity()
    held_by = (row[0] if row else meta.get("Owner") or "")
    claimed_at = (row[1] if row else meta.get("Claimed-at") or "")
    stale = bool(claimed_at) and _stale(claimed_at, root=root)
    if held_by and held_by != me and not stale and not force:
        raise ClaimConflict(f"held by {held_by}, not {me}")
    store.drop_claim(key, owner=me, force=force or stale or not held_by)
    meta["Owner"] = ""
    meta["Claimed-at"] = ""
    if meta.get("Status") == "claimed":
        meta["Status"] = "open"
    write_meta(path, meta, body)
    runtime = root / EXEC_ROOT / "claims" / f"{path.stem}.claim"
    if runtime.exists():
        runtime.unlink()
    return path


def _stale(iso: str, hours: int | None = None, root: Path | None = None) -> bool:
    hours = hours or load_contract(root).stale_hours
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return True
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return (_now() - then).total_seconds() > hours * 3600


def is_stale(meta: dict[str, str], root: Path | None = None) -> bool:
    at = meta.get("Claimed-at") or ""
    if not at:
        return False
    return _stale(at, root=root)


def link(root: Path, a: str, b: str) -> None:
    pa, pb = resolve_artifact(root, a), resolve_artifact(root, b)
    for path, other in ((pa, pb), (pb, pa)):
        meta, body = read_meta(path)
        links = [x.strip() for x in (meta.get("Links") or "").split(",") if x.strip()]
        rel = str(other.relative_to(root))
        if rel not in links:
            links.append(rel)
        meta["Links"] = ", ".join(links)
        write_meta(path, meta, body)


from spine.query import board, claimable_from_next, next_lines, status_payload
