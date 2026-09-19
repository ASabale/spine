from __future__ import annotations

from pathlib import Path

from spine import __version__
from spine.artifacts import identity, read_meta
from spine.model import SPEC_ROOT, load_contract


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
    inflight = load_contract(root).inflight
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