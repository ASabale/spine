"""Claim lifecycle: one module owns taking, releasing, staleness, and owner
lookup for claimed artifacts.

Every caller goes through this seam: the CLI verbs (`spine claim` /
`spine release`), doctor repairs, and the transition engine. A claim lives
in three representations kept in lockstep: frontmatter `Owner`/`Claimed-at`,
the one-winner row in `.spine/coord.db`, and a `.spine/claims/<stem>.claim`
runtime copy. The stale policy comes from the contract
(`claim.stale_hours`); a claim past it is re-takeable, and doctor releases
it.

The `spine.artifacts` imports are function-level on purpose: a top-level
import would close a claims -> artifacts -> query -> claims cycle through
the query re-export at the bottom of `spine.artifacts`. At call time the
import cache is complete, so the lazy import is safe (same convention as
`set_status`'s lazy `spine.engine` import).
"""

from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from spine.errors import ClaimConflict
from spine.model import EXEC_ROOT, load_contract
from spine.store import CoordStore


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


def _now() -> datetime:
    return datetime.now(UTC)


def owner_of(root: Path, path: Path, meta: dict[str, str]) -> tuple[str, str]:
    """Effective `(owner, claimed_at)` for one artifact: the one-winner row
    in coord.db wins; frontmatter is the fallback when no row exists."""
    row = CoordStore(root).get_claim(str(path.relative_to(root)))
    if row is not None:
        return row
    return (meta.get("Owner") or "", meta.get("Claimed-at") or "")


def _stale(iso: str, hours: int | None = None, root: Path | None = None) -> bool:
    """True when an ISO claimed-at is older than the stale policy."""
    hours = hours or load_contract(root).stale_hours
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return True
    if then.tzinfo is None:
        then = then.replace(tzinfo=UTC)
    return (_now() - then).total_seconds() > hours * 3600


def is_stale(meta: dict[str, str], root: Path | None = None) -> bool:
    """Staleness for a frontmatter dict; no Claimed-at means fresh."""
    at = meta.get("Claimed-at") or ""
    if not at:
        return False
    return _stale(at, root=root)


def _runtime(root: Path, path: Path) -> Path:
    return root / EXEC_ROOT / "claims" / f"{path.stem}.claim"


def claim(root: Path, spec: str) -> Path:
    """Take the claim on `spec`: one-winner insert in coord.db, frontmatter
    Owner/Claimed-at, and a `.spine/claims/` copy written in lockstep. A
    non-stale claim is refused; a stale lease is taken over."""
    from spine.artifacts import read_meta, resolve_artifact, write_meta

    path = resolve_artifact(root, spec)
    meta, body = read_meta(path)
    key = str(path.relative_to(root))
    store = CoordStore(root)
    row = store.get_claim(key)
    owner = row[0] if row else (meta.get("Owner") or "")
    claimed_at = row[1] if row else (meta.get("Claimed-at") or "")
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
    rt = _runtime(root, path)
    rt.parent.mkdir(parents=True, exist_ok=True)
    rt.write_text(f"{meta['Owner']}\n{meta['Claimed-at']}\n", encoding="utf-8")
    return path


def clear_lock(root: Path, path: Path) -> None:
    """Drop the coord row and the runtime claim file. Does not touch frontmatter."""
    CoordStore(root).drop_claim(str(path.relative_to(root)), force=True)
    rt = _runtime(root, path)
    if rt.exists():
        rt.unlink()


def release(root: Path, spec: str, *, force: bool = False) -> Path:
    """Release `spec`'s claim: the owner, a forced caller, or a stale lease.
    Clears the three representations in lockstep and flips claimed back to
    open."""
    from spine.artifacts import read_meta, resolve_artifact, write_meta

    path = resolve_artifact(root, spec)
    meta, body = read_meta(path)
    key = str(path.relative_to(root))
    store = CoordStore(root)
    me = identity()
    held_by, claimed_at = owner_of(root, path, meta)
    stale = bool(claimed_at) and _stale(claimed_at, root=root)
    if held_by and held_by != me and not stale and not force:
        raise ClaimConflict(f"held by {held_by}, not {me}")
    store.drop_claim(key, owner=me, force=force or stale or not held_by)
    meta["Owner"] = ""
    meta["Claimed-at"] = ""
    if meta.get("Status") == "claimed":
        meta["Status"] = "open"
    write_meta(path, meta, body)
    rt = _runtime(root, path)
    if rt.exists():
        rt.unlink()
    return path