from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from spine.errors import InconsistentState
from spine.model import EXEC_ROOT, SPEC_ROOT, load_contract, packaged_contract
from spine.resources import read_data
from spine.store import CoordStore

SCHEMA = 1
BACKUP = EXEC_ROOT / "migrate" / "last"


@dataclass(frozen=True)
class MigrationPlan:
    contract_from: int
    contract_to: int
    schema_from: int
    schema_to: int
    steps: list[str]

    @property
    def needed(self) -> bool:
        return bool(self.steps)


def _schema_version(root: Path) -> int:
    db = root / EXEC_ROOT / "coord.db"
    if not db.exists():
        return 0
    conn = sqlite3.connect(db)
    try:
        row = conn.execute(
            "SELECT value FROM kv WHERE key = ?", ("schema_version",)
        ).fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return 0
    finally:
        conn.close()


def _contract_version(root: Path) -> int | None:
    path = root / SPEC_ROOT / "contract.yaml"
    if not path.exists():
        return None
    try:
        return load_contract(root).version
    except Exception:
        return None


def plan(root: Path) -> MigrationPlan:
    packaged = packaged_contract()
    steps: list[str] = []
    raw = _contract_version(root)
    if raw is None:
        if (root / SPEC_ROOT / "contract.yaml").exists():
            steps.append("replace invalid contract.yaml with packaged")
            contract_from = 0
        else:
            steps.append("write packaged contract.yaml")
            contract_from = 0
    else:
        contract_from = raw
        if contract_from < packaged.version:
            steps.append(f"upgrade contract {contract_from} → {packaged.version}")
    schema_from = _schema_version(root)
    if schema_from < SCHEMA:
        steps.append(f"upgrade coord schema {schema_from} → {SCHEMA}")
    return MigrationPlan(
        contract_from=contract_from,
        contract_to=packaged.version,
        schema_from=schema_from,
        schema_to=SCHEMA,
        steps=steps,
    )


def _backup(root: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    contract = root / SPEC_ROOT / "contract.yaml"
    if contract.exists():
        copy2(contract, dest / "contract.yaml")
    db = root / EXEC_ROOT / "coord.db"
    if db.exists():
        copy2(db, dest / "coord.db")


def _restore(root: Path, src: Path) -> None:
    contract_src = src / "contract.yaml"
    if contract_src.exists():
        dest = root / SPEC_ROOT / "contract.yaml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy2(contract_src, dest)
    db_src = src / "coord.db"
    if db_src.exists():
        dest = root / EXEC_ROOT / "coord.db"
        dest.parent.mkdir(parents=True, exist_ok=True)
        copy2(db_src, dest)


def _apply(root: Path, pl: MigrationPlan) -> None:
    packaged = packaged_contract()
    contract = root / SPEC_ROOT / "contract.yaml"
    if any("contract.yaml" in s or "upgrade contract" in s for s in pl.steps):
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_text(read_data("contract.yaml"), encoding="utf-8")
    store = CoordStore(root)
    store.put("schema_version", str(pl.schema_to))
    _ = packaged


def _verify(root: Path) -> None:
    load_contract(root)
    CoordStore(root)
    if not (root / SPEC_ROOT / "contract.yaml").exists():
        raise InconsistentState("contract.yaml missing after migrate")


def migrate(root: Path, *, dry_run: bool = False, rollback: bool = False) -> list[str]:
    msgs: list[str] = []
    backup = root / BACKUP
    if rollback:
        if not backup.exists():
            msgs.append("REPORT no migrate backup to rollback")
            return msgs
        _restore(root, backup)
        msgs.append("FIX rolled back from .spine/migrate/last")
        return msgs
    pl = plan(root)
    msgs.append(
        f"plan contract {pl.contract_from}→{pl.contract_to} schema {pl.schema_from}→{pl.schema_to}"
    )
    msgs.extend(f"step {s}" for s in pl.steps)
    if not pl.needed:
        msgs.append("ok already current")
        return msgs
    if dry_run:
        msgs.append("dry-run; no writes")
        return msgs
    _backup(root, backup)
    try:
        _apply(root, pl)
        _verify(root)
        msgs.append("ok migrated")
    except Exception as exc:
        _restore(root, backup)
        msgs.append(f"REPORT migrate failed; rolled back: {exc}")
        raise
    return msgs
