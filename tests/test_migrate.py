from pathlib import Path

from spine.initcmd import init_target
from spine.migrate import SCHEMA, migrate, plan
from spine.model import load_contract
from spine.store import CoordStore


def test_migrate_dry_run_does_not_write(tmp_path: Path):
    init_target(tmp_path)
    before = (tmp_path / "docs/spine/contract.yaml").read_text(encoding="utf-8")
    msgs = migrate(tmp_path, dry_run=True)
    assert any("dry-run" in m for m in msgs)
    assert (tmp_path / "docs/spine/contract.yaml").read_text(encoding="utf-8") == before
    assert not (tmp_path / ".spine/coord.db").exists()


def test_migrate_apply_upgrades_invalid_contract(tmp_path: Path):
    init_target(tmp_path)
    path = tmp_path / "docs/spine/contract.yaml"
    path.write_text("version: 1\nstatuses: []\n", encoding="utf-8")
    msgs = migrate(tmp_path, dry_run=True)
    assert any("invalid contract" in m or "replace invalid" in m for m in msgs)
    assert path.read_text(encoding="utf-8") == "version: 1\nstatuses: []\n"
    msgs = migrate(tmp_path)
    assert any("ok migrated" in m for m in msgs)
    c = load_contract(tmp_path)
    assert c.ticket_statuses
    assert CoordStore(tmp_path).get("schema_version") == str(SCHEMA)


def test_migrate_rollback_restores_backup(tmp_path: Path):
    init_target(tmp_path)
    path = tmp_path / "docs/spine/contract.yaml"
    original = path.read_text(encoding="utf-8")
    path.write_text("version: 1\nstatuses: []\n", encoding="utf-8")
    migrate(tmp_path)
    assert load_contract(tmp_path).ticket_statuses
    msgs = migrate(tmp_path, rollback=True)
    assert any("rolled back" in m for m in msgs)
    assert path.read_text(encoding="utf-8") == "version: 1\nstatuses: []\n"


def test_migrate_noop_when_current(tmp_path: Path):
    init_target(tmp_path)
    migrate(tmp_path)
    msgs = migrate(tmp_path)
    assert any("already current" in m for m in msgs)
    pl = plan(tmp_path)
    assert pl.needed is False
