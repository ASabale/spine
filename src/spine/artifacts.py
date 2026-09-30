from __future__ import annotations

import os
from pathlib import Path

from spine.claims import claim, identity, is_stale, release  # noqa: F401  (re-export)
from spine.errors import AmbiguousArtifact, HumanInterventionRequired
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
    if os.environ.get("SPINE_HUMAN") != "1":
        raise HumanInterventionRequired("creating a work item needs SPINE_HUMAN=1")
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


def _artifact_files(root: Path, folders: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    for name in folders:
        folder = root / SPEC_ROOT / name
        if not folder.is_dir():
            continue
        base = folder.resolve()
        for path in folder.glob("*.md"):
            if path.is_symlink():
                resolved = path.resolve()
                try:
                    resolved.relative_to(base)
                except ValueError:
                    continue
                found.append(resolved)
                continue
            if path.is_file():
                found.append(path)
    return found


def _direct_file(root: Path, token: str, folders: tuple[str, ...]) -> Path | None:
    raw = Path(token)
    cand = raw if raw.is_absolute() else root / token
    if not cand.is_file():
        return None
    resolved = cand.resolve()
    for name in folders:
        base = (root / SPEC_ROOT / name).resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            continue
        return resolved
    return None


def _one_match(root: Path, spec: str, matches: list[Path]) -> Path:
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        rels = sorted(str(path.relative_to(root)) for path in matches)
        raise AmbiguousArtifact(spec, rels)
    raise FileNotFoundError(spec)


def resolve_artifact(
    root: Path,
    spec: str,
    *,
    folders: tuple[str, ...] = ("work-items", "tickets"),
) -> Path:
    """Bind spec to one markdown artifact under the searched folders.

    An existing path wins, then an exact filename, stem, or relative path,
    then a pure number as a zero-padded ``NN-`` prefix. Any other token must
    be a unique substring. A pure number does not fall through to a substring,
    and more than one match raises.
    """
    root = root.resolve()
    token = spec.strip()
    if not token:
        raise FileNotFoundError(spec)
    direct = _direct_file(root, token, folders)
    if direct is not None:
        return direct
    files = _artifact_files(root, folders)
    exact = [
        path
        for path in files
        if path.name == Path(token).name
        or path.stem == token
        or str(path.relative_to(root)) == token
    ]
    if exact:
        return _one_match(root, token, exact)
    if token.isdigit():
        prefix = f"{int(token):02d}-"
        numbered = [path for path in files if path.name.startswith(prefix)]
        return _one_match(root, token, numbered)
    fuzzy = [path for path in files if token in path.name or token in path.stem]
    return _one_match(root, token, fuzzy)


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


# Late re-export: a top-level import cycles claims → artifacts → query → claims.
from spine.query import (  # noqa: F401
    board,
    claimable_from_next,
    next_lines,
    status_payload,
)
