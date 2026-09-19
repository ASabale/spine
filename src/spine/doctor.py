from __future__ import annotations

import json
from pathlib import Path

from spine.artifacts import _is_ticket, is_stale, read_meta, release, write_meta
from spine.model import EXEC_ROOT, SPEC_DIRS, SPEC_ROOT, load_contract, packaged_contract


def _blocker_number(value: str) -> int | None:
    head = value.strip().split("-", 1)[0].split("/", 1)[-1]
    if head.isdigit():
        return int(head)
    return None


def _find_blocker(root: Path, value: str) -> Path | None:
    raw = value.strip()
    if not raw:
        return None
    tickets = root / SPEC_ROOT / "tickets"
    if not tickets.is_dir():
        return None
    cand = root / raw
    if cand.exists() and cand.parent == tickets:
        return cand
    named = tickets / Path(raw).name
    if named.exists():
        return named
    num = _blocker_number(raw)
    if num is None:
        return None
    for p in tickets.glob("*.md"):
        if p.name.split("-", 1)[0] == f"{num:02d}":
            return p
    return None


def _logged_status(root: Path, path: Path) -> str | None:
    log = root / EXEC_ROOT / "events.jsonl"
    if not log.exists():
        return None
    last = None
    name, stem = path.name, path.stem
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        ev = json.loads(line)
        spec = str(ev.get("spec") or "")
        if name in spec or stem in spec:
            last = ev.get("to") or None
    return last


def doctor_ok(msgs: list[str]) -> bool:
    """True when nothing unrepaired remains (FIX lines count as repaired)."""
    if not msgs:
        return True
    if all(m == "ok" or m.startswith("FIX ") for m in msgs):
        return True
    reports = [m for m in msgs if m.startswith("REPORT ")]
    unrepairable = [m for m in reports if "unknown status" not in m]
    if unrepairable:
        return False
    detect = [m for m in msgs if m != "ok" and not m.startswith("FIX ")]
    if not detect:
        return True
    return any(m.startswith("FIX ") for m in msgs)


def doctor(root: Path, *, apply: bool = True) -> list[str]:
    msgs: list[str] = []
    if not (root / SPEC_ROOT / "contract.yaml").exists():
        msgs.append("REPORT not a spine target; run: spine init")
        out = root / EXEC_ROOT / "doctor" / "last.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(msgs) + "\n", encoding="utf-8")
        return msgs
    contract = load_contract(root)
    packaged = packaged_contract()
    if contract.version != packaged.version:
        msgs.append(
            f"REPORT contract version {contract.version} in target vs packaged {packaged.version}"
        )

    for name in SPEC_DIRS:
        p = root / SPEC_ROOT / name
        if not p.is_dir():
            msgs.append(f"REPORT missing spec dir {p.relative_to(root)}")

    for rel in (
        SPEC_ROOT / "README.md",
        SPEC_ROOT / "contract.yaml",
        SPEC_ROOT / "wires.yaml",
        SPEC_ROOT / "maps" / "map.md",
    ):
        if not (root / rel).exists():
            msgs.append(f"REPORT missing spec file {rel}")

    gi = root / ".gitignore"
    if not gi.exists() or ".spine/" not in gi.read_text(encoding="utf-8"):
        msgs.append("REPORT gitignore missing .spine/")

    folders = []
    for name in ("work-items", "tickets"):
        d = root / SPEC_ROOT / name
        if d.is_dir():
            folders.append(d)

    for folder in folders:
        for path in folder.glob("*.md"):
            meta, body = read_meta(path)
            status = meta.get("Status", "")
            ticket = _is_ticket(path, meta)
            allowed = contract.ticket_statuses if ticket else contract.statuses
            if status and status not in allowed:
                msgs.append(f"REPORT unknown status {status} in {path.name}")
                if apply:
                    nxt = "open" if ticket else "ready"
                    meta["Status"] = nxt
                    write_meta(path, meta, body)
                    msgs.append(f"FIX status {path.name} {status} → {nxt} (not in contract)")
                    meta, body = read_meta(path)
            logged = _logged_status(root, path)
            cur = meta.get("Status", "")
            if logged and logged in allowed and logged != cur:
                msgs.append(f"DRIFT {path.name} {cur} vs event {logged}")
                if apply:
                    meta["Status"] = logged
                    write_meta(path, meta, body)
                    msgs.append(f"FIX status {path.name} {cur} → {logged} from event log (frontmatter drifted)")
                    meta, body = read_meta(path)
            if is_stale(meta, root=root):
                msgs.append(f"STALE claim on {path.name}")
                if apply:
                    release(root, str(path.relative_to(root)))
                    msgs.append(f"FIX released stale claim {path.name} (lease expired)")
            links = [x.strip() for x in (meta.get("Links") or "").split(",") if x.strip()]
            kept = []
            changed = False
            for rel in links:
                if (root / rel).exists():
                    kept.append(rel)
                else:
                    msgs.append(f"BROKEN link {path.name} → {rel}")
                    changed = True
            if changed and apply:
                meta["Links"] = ", ".join(kept)
                write_meta(path, meta, body)
                msgs.append(f"FIX links on {path.name} (dropped missing paths)")
                meta, body = read_meta(path)

            blocked = (meta.get("Blocked by") or "").strip()
            if blocked:
                blocker = _find_blocker(root, blocked)
                if blocker is None:
                    msgs.append(f"BROKEN blocker {path.name} → {blocked}")
                    if apply:
                        meta["Blocked by"] = ""
                        write_meta(path, meta, body)
                        msgs.append(f"FIX cleared Blocked by on {path.name} ({blocked} missing)")
                else:
                    bmeta, _ = read_meta(blocker)
                    if (bmeta.get("Status") or "") == "resolved":
                        msgs.append(f"RESOLVED blocker {path.name} → {blocked}")
                        if apply:
                            meta["Blocked by"] = ""
                            write_meta(path, meta, body)
                            msgs.append(f"FIX cleared Blocked by on {path.name} ({blocked} resolved)")

    out = root / EXEC_ROOT / "doctor" / "last.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(msgs) + ("\n" if msgs else "ok\n"), encoding="utf-8")
    if not msgs:
        msgs.append("ok")
    return msgs
