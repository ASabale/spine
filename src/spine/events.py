from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from spine.model import EXEC_ROOT, parse_front


def append_event(
    root: Path,
    *,
    actor: str = "",
    from_status: str,
    to_status: str,
    revision: str = "",
    run_id: str = "",
    spec: str = "",
) -> Path:
    path = root / EXEC_ROOT / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "actor": actor,
        "time": datetime.now(timezone.utc).isoformat(),
        "from": from_status,
        "to": to_status,
        "revision": revision,
        "run_id": run_id,
        "spec": spec,
    }
    line = json.dumps(rec, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()
        os.fsync(fh.fileno())
    return path


def content_revision(path: Path) -> str:
    _meta, body = parse_front(path.read_text(encoding="utf-8"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()