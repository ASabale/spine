from __future__ import annotations

from pathlib import Path

from spine.claims import claim, identity, is_stale, release  # noqa: F401  (re-export)
from spine.model import (
    EXEC_ROOT,
    SPEC_ROOT,
    dump_front,
)

from spine.store import CoordStore, FileStore


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
                    if _under_spec(root, f):
                        return f.resolve()
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
