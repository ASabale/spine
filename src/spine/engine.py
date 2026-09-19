from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from spine.artifacts import (
    _deliverable_exists,
    _is_ticket,
    read_meta,
    resolve_artifact,
    write_meta,
)
from spine.errors import InvalidTransition
from spine.gates import require_eval, require_review
from spine.model import load_contract


@dataclass(frozen=True)
class AdvanceResult:
    path: Path
    previous: str
    status: str
    changed: bool


def advance(
    root: Path,
    spec: str,
    nxt: str,
    *,
    actor: str = "",
    reason: str = "",
    run_id: str = "",
) -> AdvanceResult:
    # actor/reason/run_id are accepted and ignored (event log is a later ticket).
    contract = load_contract(root)
    path = resolve_artifact(root, spec)
    meta, body = read_meta(path)
    cur = meta.get("Status", "")
    if cur == nxt:
        return AdvanceResult(path=path, previous=cur, status=nxt, changed=False)
    if _is_ticket(path, meta):
        if nxt not in contract.ticket_statuses:
            raise InvalidTransition(f"unknown ticket status {nxt}")
        if not contract.ticket_allowed(cur, nxt):
            raise InvalidTransition(f"illegal ticket transition {cur} → {nxt}")
        meta["Status"] = nxt
        if nxt == "open":
            meta["Owner"] = ""
            meta["Claimed-at"] = ""
        write_meta(path, meta, body)
        return AdvanceResult(path=path, previous=cur, status=nxt, changed=True)
    if nxt not in contract.statuses:
        raise InvalidTransition(f"unknown status {nxt}")
    profile = (meta.get("Profile") or "software").lower()
    software = profile == "software"
    if cur == "doing" and nxt == "done" and not software:
        if not _deliverable_exists(root, meta):
            raise InvalidTransition("non-software doing → done needs an existing Deliverable path")
    elif not contract.allowed(cur, nxt):
        raise InvalidTransition(f"illegal transition {cur} → {nxt}")
    if software and cur == "checking" and nxt == "reviewing":
        require_eval(root, path.stem)
    if nxt == "done" and software:
        required = contract.software_required()
        if cur not in {"reviewing"} and "reviewing" in required:
            raise InvalidTransition("software profile requires reviewing before done")
        require_review(root, path.stem)
    meta["Status"] = nxt
    write_meta(path, meta, body)
    return AdvanceResult(path=path, previous=cur, status=nxt, changed=True)