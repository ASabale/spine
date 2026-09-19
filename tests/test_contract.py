from pathlib import Path

import pytest
import yaml

from spine.model import ContractError, SPEC_ROOT, load_contract, packaged_contract

REPO = Path(__file__).resolve().parent.parent


def test_packaged_contract_validates():
    c = packaged_contract()
    assert c.statuses == [
        "ready",
        "doing",
        "checking",
        "reviewing",
        "done",
        "changes-requested",
    ]
    assert c.allowed("ready", "doing")
    assert not c.allowed("ready", "done")
    assert c.stale_hours == 4
    assert "reviewing" in c.software_required()
    assert c.ticket_statuses == ["open", "claimed", "resolved"]
    assert c.ticket_allowed("open", "claimed")
    assert c.ticket_allowed("claimed", "open")
    assert not c.ticket_allowed("resolved", "open")
    assert c.inflight == ["reviewing", "checking", "doing", "changes-requested"]


def test_no_hardcoded_ticket_machine():
    import spine.model as model

    assert not hasattr(model, "TICKET_STATUSES")
    assert not hasattr(model, "TICKET_TRANSITIONS")


def test_docs_contract_matches_packaged():
    docs = (REPO / SPEC_ROOT / "contract.yaml").read_text(encoding="utf-8")
    packaged = (REPO / "src" / "spine" / "data" / "contract.yaml").read_text(encoding="utf-8")
    assert docs == packaged
    loaded = load_contract(REPO)
    pkg = packaged_contract()
    assert loaded.statuses == pkg.statuses
    assert loaded.transitions == pkg.transitions
    assert loaded.stale_hours == pkg.stale_hours
    assert loaded.version == pkg.version
    assert loaded.ticket_statuses == pkg.ticket_statuses
    assert loaded.ticket_transitions == pkg.ticket_transitions


def test_spec_md_lists_every_work_item_status():
    spec = (REPO / "spec.md").read_text(encoding="utf-8")
    for status in packaged_contract().statuses:
        assert status in spec


def _write_contract(tmp_path: Path, raw: dict) -> None:
    path = tmp_path / "docs" / "spine" / "contract.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")


def _valid_raw() -> dict:
    return yaml.safe_load((REPO / SPEC_ROOT / "contract.yaml").read_text(encoding="utf-8"))


def test_unknown_transition_target_rejected(tmp_path: Path):
    raw = _valid_raw()
    raw["transitions"]["ready"] = ["bogus"]
    _write_contract(tmp_path, raw)
    with pytest.raises(ContractError):
        load_contract(tmp_path)


def test_unknown_transition_source_rejected(tmp_path: Path):
    raw = _valid_raw()
    raw["transitions"]["bogus"] = ["doing"]
    _write_contract(tmp_path, raw)
    with pytest.raises(ContractError):
        load_contract(tmp_path)


def test_empty_statuses_rejected(tmp_path: Path):
    raw = _valid_raw()
    raw["statuses"] = []
    _write_contract(tmp_path, raw)
    with pytest.raises(ContractError):
        load_contract(tmp_path)


def test_status_missing_from_transitions_rejected(tmp_path: Path):
    raw = _valid_raw()
    del raw["transitions"]["done"]
    _write_contract(tmp_path, raw)
    with pytest.raises(ContractError):
        load_contract(tmp_path)


def test_required_before_done_must_be_a_status(tmp_path: Path):
    raw = _valid_raw()
    raw["profiles"]["software"]["required_before_done"] = ["nope"]
    _write_contract(tmp_path, raw)
    with pytest.raises(ContractError):
        load_contract(tmp_path)


def test_stale_hours_must_be_positive_int(tmp_path: Path):
    raw = _valid_raw()
    raw["claim"]["stale_hours"] = 0
    _write_contract(tmp_path, raw)
    with pytest.raises(ContractError):
        load_contract(tmp_path)


def test_unknown_ticket_transition_target_rejected(tmp_path: Path):
    raw = _valid_raw()
    raw["tickets"]["transitions"]["open"] = ["bogus"]
    _write_contract(tmp_path, raw)
    with pytest.raises(ContractError):
        load_contract(tmp_path)


def test_missing_tickets_section_rejected(tmp_path: Path):
    raw = _valid_raw()
    raw.pop("tickets", None)
    _write_contract(tmp_path, raw)
    with pytest.raises(ContractError):
        load_contract(tmp_path)
