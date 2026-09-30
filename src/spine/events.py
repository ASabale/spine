from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from spine.model import EXEC_ROOT, parse_front


def load_event(line: str) -> dict:
    """One jsonl event. Lines written before reason/op still parse."""
    ev = json.loads(line)
    ev.setdefault("reason", "")
    ev.setdefault("op", "status")
    return ev


def latest_reason(root: Path, path: Path) -> str:
    log = root / EXEC_ROOT / "events.jsonl"
    if not log.exists():
        return ""
    rel = str(path.relative_to(root))
    keys = {rel, path.name, path.stem}
    last = ""
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        ev = load_event(line)
        spec = str(ev.get("spec") or "")
        if spec in keys:
            last = str(ev.get("reason") or "")
    return last


def append_event(
    root: Path,
    *,
    actor: str = "",
    from_status: str,
    to_status: str,
    revision: str = "",
    run_id: str = "",
    spec: str = "",
    reason: str = "",
    op: str = "status",
    human: bool = False,
) -> Path:
    path = root / EXEC_ROOT / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "actor": actor,
        "time": datetime.now(UTC).isoformat(),
        "from": from_status,
        "to": to_status,
        "revision": revision,
        "run_id": run_id,
        "spec": spec,
        "reason": reason,
        "op": op,
    }
    if human:
        rec["human"] = True
    line = json.dumps(rec, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()
        os.fsync(fh.fileno())
    return path


def content_revision(path: Path) -> str:
    _meta, body = parse_front(path.read_text(encoding="utf-8"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()