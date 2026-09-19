from __future__ import annotations

from pathlib import Path

from spine.artifacts import is_stale, read_meta, release, write_meta
from spine.model import EXEC_ROOT, SPEC_DIRS, SPEC_ROOT, load_contract, packaged_contract


def _blocker_number(value: str) -> int | None:
    head = value.strip().split("-", 1)[0].split("/", 1)[-1]
    if head.isdigit():
        return int(head)
    return None


def doctor(root: Path, *, apply: bool = True) -> list[str]:
    msgs: list[str] = []
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
            if status and status not in contract.statuses and status not in {"open", "claimed", "resolved"}:
                msgs.append(f"REPORT unknown status {status} in {path.name}")
            if is_stale(meta, root=root):
                msgs.append(f"STALE claim on {path.name}")
                if apply:
                    release(root, str(path.relative_to(root)))
                    msgs.append(f"FIX released stale claim {path.name}")
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
                msgs.append(f"FIX links on {path.name}")
                meta, body = read_meta(path)

            blocked = (meta.get("Blocked by") or "").strip()
            if blocked:
                num = _blocker_number(blocked)
                tickets = root / SPEC_ROOT / "tickets"
                exists = False
                if num is not None and tickets.is_dir():
                    exists = any(
                        p.name.split("-", 1)[0] == f"{num:02d}" for p in tickets.glob("*.md")
                    )
                if not exists:
                    msgs.append(f"BROKEN blocker {path.name} → {blocked}")
                    if apply:
                        meta["Blocked by"] = ""
                        write_meta(path, meta, body)
                        msgs.append(f"FIX cleared Blocked by on {path.name}")

    out = root / EXEC_ROOT / "doctor" / "last.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(msgs) + ("\n" if msgs else "ok\n"), encoding="utf-8")
    if not msgs:
        msgs.append("ok")
    return msgs
