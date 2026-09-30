from pathlib import Path

import pytest

from spine.artifacts import new_ticket, new_work_item, resolve_artifact
from spine.errors import AmbiguousArtifact
from spine.initcmd import init_target


def _rename(path: Path, name: str) -> Path:
    dest = path.with_name(name)
    return path.rename(dest)


def test_number_matches_padded_prefix_not_a_longer_id(tmp_path: Path):
    init_target(tmp_path)
    alpha = new_ticket(tmp_path, "Alpha")
    one = _rename(new_ticket(tmp_path, "One"), "11-one.md")
    wide = _rename(new_ticket(tmp_path, "Wide"), "116-wide.md")
    assert alpha.name == "01-alpha.md"
    assert resolve_artifact(tmp_path, "1") == alpha.resolve()
    assert resolve_artifact(tmp_path, "01") == alpha.resolve()
    assert resolve_artifact(tmp_path, "11") == one.resolve()
    assert resolve_artifact(tmp_path, "116") == wide.resolve()
    with pytest.raises(FileNotFoundError):
        resolve_artifact(tmp_path, "16")


def test_number_does_not_fall_through_to_substring(tmp_path: Path):
    init_target(tmp_path)
    _rename(new_ticket(tmp_path, "One"), "11-one.md")
    with pytest.raises(FileNotFoundError):
        resolve_artifact(tmp_path, "1")


def test_same_number_in_work_items_and_tickets_is_ambiguous(tmp_path: Path):
    init_target(tmp_path)
    ticket = new_ticket(tmp_path, "Alpha")
    item = new_work_item(tmp_path, "Beta")
    with pytest.raises(AmbiguousArtifact) as exc:
        resolve_artifact(tmp_path, "1")
    assert any(ticket.name in match for match in exc.value.matches)
    assert any(item.name in match for match in exc.value.matches)


def test_tickets_folder_ignores_work_items(tmp_path: Path):
    init_target(tmp_path)
    item = new_work_item(tmp_path, "Alpha")
    one = _rename(new_ticket(tmp_path, "One"), "11-one.md")
    with pytest.raises(FileNotFoundError):
        resolve_artifact(tmp_path, "1", folders=("tickets",))
    assert resolve_artifact(tmp_path, "1") == item.resolve()
    assert resolve_artifact(tmp_path, "11", folders=("tickets",)) == one.resolve()


def test_substring_must_be_unique(tmp_path: Path):
    init_target(tmp_path)
    first = new_ticket(tmp_path, "Item A")
    second = new_ticket(tmp_path, "Item B")
    with pytest.raises(AmbiguousArtifact) as exc:
        resolve_artifact(tmp_path, "item")
    assert len(exc.value.matches) == 2
    assert resolve_artifact(tmp_path, "item-a") == first.resolve()
    assert resolve_artifact(tmp_path, second.stem) == second.resolve()
