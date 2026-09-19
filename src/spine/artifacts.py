from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from spine import __version__

from spine.model import (
    EXEC_ROOT,
    SPEC_ROOT,
    dump_front,
    load_contract,
    parse_front,
)


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


def _next_number(folder: Path) -> int:
    n = 0
    if not folder.exists():
        return 1
    for p in folder.glob("*.md"):
        head = p.name.split("-", 1)[0]
        if head.isdigit():
            n = max(n, int(head))
    return n + 1


def new_ticket(root: Path, title: str, typ: str = "grilling") -> Path:
    folder = root / SPEC_ROOT / "tickets"
    folder.mkdir(parents=True, exist_ok=True)
    num = _next_number(folder)
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
    num = _next_number(folder)
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


def resolve_artifact(root: Path, spec: str) -> Path:
    p = Path(spec)
    if p.is_absolute() and p.exists():
        return p
    cand = root / spec
    if cand.exists():
        return cand
    for folder in ("work-items", "tickets"):
        d = root / SPEC_ROOT / folder
        if d.exists():
            for f in d.glob("*.md"):
                if spec in f.name or spec in f.stem:
                    return f
    raise FileNotFoundError(spec)


def read_meta(path: Path) -> tuple[dict[str, str], str]:
    return parse_front(path.read_text(encoding="utf-8"))


def write_meta(path: Path, meta: dict[str, str], body: str) -> None:
    title = meta.get("Title") or path.stem
    path.write_text(dump_front(meta, body, title=title), encoding="utf-8")


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
    contract = load_contract(root)
    path = resolve_artifact(root, spec)
    meta, body = read_meta(path)
    cur = meta.get("Status", "")
    if _is_ticket(path, meta):
        if nxt not in contract.ticket_statuses:
            raise ValueError(f"unknown ticket status {nxt}")
        if not contract.ticket_allowed(cur, nxt):
            raise ValueError(f"illegal ticket transition {cur} → {nxt}")
        meta["Status"] = nxt
        if nxt == "open":
            meta["Owner"] = ""
            meta["Claimed-at"] = ""
        write_meta(path, meta, body)
        return path
    if nxt not in contract.statuses:
        raise ValueError(f"unknown status {nxt}")
    profile = (meta.get("Profile") or "software").lower()
    software = profile == "software"
    if cur == "doing" and nxt == "done" and not software:
        if not _deliverable_exists(root, meta):
            raise ValueError("non-software doing → done needs an existing Deliverable path")
    elif not contract.allowed(cur, nxt):
        raise ValueError(f"illegal transition {cur} → {nxt}")
    if software and cur == "checking" and nxt == "reviewing":
        if not _has_proof(root, "evals", path.stem):
            raise ValueError("software checking → reviewing needs proof under .spine/evals/")
    if nxt == "done" and software:
        required = contract.software_required()
        if cur not in {"reviewing"} and "reviewing" in required:
            raise ValueError("software profile requires reviewing before done")
        if not _has_proof(root, "reviews", path.stem):
            raise ValueError("software reviewing → done needs proof under .spine/reviews/")
    meta["Status"] = nxt
    write_meta(path, meta, body)
    return path


def claim(root: Path, spec: str) -> Path:
    path = resolve_artifact(root, spec)
    meta, body = read_meta(path)
    owner = meta.get("Owner") or ""
    claimed_at = meta.get("Claimed-at") or ""
    if owner and claimed_at and not _stale(claimed_at, root=root):
        raise ValueError(f"already claimed by {owner} at {claimed_at}")
    meta["Owner"] = identity()
    meta["Claimed-at"] = _now().isoformat()
    if meta.get("Status") == "open":
        meta["Status"] = "claimed"
    write_meta(path, meta, body)
    runtime = root / EXEC_ROOT / "claims" / f"{path.stem}.claim"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text(f"{meta['Owner']}\n{meta['Claimed-at']}\n", encoding="utf-8")
    return path


def release(root: Path, spec: str) -> Path:
    path = resolve_artifact(root, spec)
    meta, body = read_meta(path)
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


def _ticket_blocked(meta: dict[str, str]) -> bool:
    return bool((meta.get("Blocked by") or "").strip())


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _map_destination(root: Path) -> str:
    path = root / SPEC_ROOT / "maps" / "map.md"
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    capturing = False
    chunk: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if capturing:
                break
            capturing = line.strip() == "## Destination"
            continue
        if capturing:
            chunk.append(line)
    return "\n".join(chunk).strip()


def _next_for_work_item(root: Path, row: tuple[str, Path, dict[str, str]]) -> list[str]:
    status, path, meta = row
    rel = _rel(path, root)
    software = (meta.get("Profile") or "software").lower() == "software"
    if status == "ready":
        return [
            f"spine claim {rel}",
            f"spine set-status {rel} doing",
        ]
    if status == "doing":
        if software:
            return [f"spine set-status {rel} checking"]
        dest = (meta.get("Deliverable") or "").strip() or "<Deliverable path>"
        return [
            f"Confirm deliverable exists: {dest}",
            f"spine set-status {rel} done",
        ]
    if status == "checking":
        return [
            f"Write .spine/evals/{path.stem}.md",
            f"spine set-status {rel} reviewing",
        ]
    if status == "reviewing":
        return [
            f"Write .spine/reviews/{path.stem}.md",
            f"spine set-status {rel} done",
            f"# or spine set-status {rel} changes-requested",
        ]
    if status == "changes-requested":
        return [f"spine set-status {rel} doing"]
    return ["spine status"]


def claimable_from_next(root: Path) -> str:
    for line in next_lines(root):
        if line.startswith("spine claim "):
            return line.split()[-1]
    raise ValueError("nothing to claim; run spine next")


def next_lines(root: Path) -> list[str]:
    if not (root / SPEC_ROOT / "contract.yaml").exists():
        return [
            "This directory is not a spine target.",
            "spine init",
        ]
    wi_dir = root / SPEC_ROOT / "work-items"
    items: list[tuple[str, Path, dict[str, str]]] = []
    if wi_dir.is_dir():
        for p in sorted(wi_dir.glob("*.md")):
            meta, _ = read_meta(p)
            items.append((meta.get("Status", ""), p, meta))
    inflight = ["reviewing", "checking", "doing", "changes-requested"]
    active = [row for row in items if row[0] in inflight]
    active.sort(key=lambda row: inflight.index(row[0]))
    if active:
        return _next_for_work_item(root, active[0])
    tk_dir = root / SPEC_ROOT / "tickets"
    if tk_dir.is_dir():
        for p in sorted(tk_dir.glob("*.md")):
            meta, _ = read_meta(p)
            status = meta.get("Status", "")
            if status == "claimed":
                rel = _rel(p, root)
                return [
                    f"Answer {rel}",
                    f"spine set-status {rel} resolved",
                ]
            if status == "open" and not _ticket_blocked(meta) and not (meta.get("Owner") or "").strip():
                rel = _rel(p, root)
                return [f"spine claim {rel}"]
    ready = [row for row in items if row[0] == "ready"]
    if ready:
        return _next_for_work_item(root, ready[0])
    if not _map_destination(root):
        return [
            "Edit docs/spine/maps/map.md (Destination)",
            'spine new ticket --title "..." --type grilling',
        ]
    return [
        "Way is clear: mint a work item (HITL).",
        'spine new work-item --title "..." --profile software',
    ]


def status_payload(root: Path) -> dict[str, object]:
    """Machine-readable board. `run` is the spine commands an agent may execute."""
    lines = next_lines(root)
    work_items: list[dict[str, str]] = []
    tickets: list[dict[str, str]] = []
    frontier: list[str] = []
    wi = root / SPEC_ROOT / "work-items"
    tk = root / SPEC_ROOT / "tickets"
    if (root / SPEC_ROOT / "contract.yaml").exists():
        contract = load_contract(root)
        if wi.is_dir():
            for p in sorted(wi.glob("*.md")):
                meta, _ = read_meta(p)
                software = (meta.get("Profile") or "software").lower() == "software"
                gates = contract.next_gates(meta.get("Status", ""), software=software)
                work_items.append(
                    {
                        "file": p.name,
                        "status": meta.get("Status", ""),
                        "owner": meta.get("Owner", "") or "",
                        "next": ",".join(gates) if gates else "",
                    }
                )
        if tk.is_dir():
            for p in sorted(tk.glob("*.md")):
                meta, _ = read_meta(p)
                status = meta.get("Status", "")
                tickets.append(
                    {
                        "file": p.name,
                        "status": status,
                        "blocked_by": meta.get("Blocked by", "") or "",
                    }
                )
                if status == "open" and not _ticket_blocked(meta) and not (meta.get("Owner") or "").strip():
                    frontier.append(p.name)
    return {
        "cwd": str(root),
        "user": identity(),
        "version": __version__,
        "next": lines,
        "run": [
            line
            for line in lines
            if line.startswith("spine ") and "..." not in line
        ],
        "hitl": any(
            not line.startswith("spine ") and not line.startswith("#") for line in lines
        ),
        "work_items": work_items,
        "tickets": tickets,
        "frontier": frontier,
    }


def board(root: Path) -> str:
    contract = load_contract(root)
    lines = ["# spine status", f"cwd: {root}", ""]
    lines.append("## Next")
    lines.extend(f"- {line}" if not line.startswith("#") else line for line in next_lines(root))
    lines.append("")
    wi = root / SPEC_ROOT / "work-items"
    tk = root / SPEC_ROOT / "tickets"
    if wi.exists():
        lines.append("## Work items")
        for p in sorted(wi.glob("*.md")):
            meta, _ = read_meta(p)
            software = (meta.get("Profile") or "software").lower() == "software"
            gates = contract.next_gates(meta.get("Status", ""), software=software)
            gate = ",".join(gates) if gates else "-"
            lines.append(
                f"- {p.name}: {meta.get('Status','?')} next={gate} owner={meta.get('Owner','') or '-'}"
            )
        lines.append("")
    frontier: list[str] = []
    if tk.exists():
        lines.append("## Tickets")
        for p in sorted(tk.glob("*.md")):
            meta, _ = read_meta(p)
            status = meta.get("Status", "?")
            blocked = meta.get("Blocked by", "") or "-"
            lines.append(f"- {p.name}: {status} blocked={blocked}")
            if status == "open" and not _ticket_blocked(meta) and not (meta.get("Owner") or "").strip():
                frontier.append(p.name)
        lines.append("")
        lines.append("## Frontier")
        if frontier:
            for name in frontier:
                lines.append(f"- {name}")
        else:
            lines.append("- (empty)")
    return "\n".join(lines) + "\n"
