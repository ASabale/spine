from pathlib import Path

import pytest

from spine.artifacts import claim, new_ticket, read_meta, release
from spine.errors import ClaimConflict
from spine.initcmd import init_target
from spine.store import CoordStore


def test_claim_records_sqlite_row(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Claim me")
    claim(tmp_path, str(tk))
    rel = str(tk.relative_to(tmp_path))
    owner, claimed_at = CoordStore(tmp_path).get_claim(rel)
    assert owner == "ada"
    assert claimed_at
    meta, _ = read_meta(tk)
    assert meta["Owner"] == "ada"
    assert meta["Status"] == "claimed"


def test_second_claimant_loses(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Claim me")
    claim(tmp_path, str(tk))
    monkeypatch.setenv("SPINE_USER", "bob")
    with pytest.raises(ClaimConflict, match="already claimed"):
        claim(tmp_path, str(tk))
    assert read_meta(tk)[0]["Owner"] == "ada"


def test_release_rejects_non_owner(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SPINE_USER", "ada")
    init_target(tmp_path)
    tk = new_ticket(tmp_path, "Claim me")
    claim(tmp_path, str(tk))
    monkeypatch.setenv("SPINE_USER", "bob")
    with pytest.raises(ClaimConflict, match="held by"):
        release(tmp_path, str(tk))
    assert read_meta(tk)[0]["Owner"] == "ada"
    assert CoordStore(tmp_path).get_claim(str(tk.relative_to(tmp_path)))[0] == "ada"
    monkeypatch.setenv("SPINE_USER", "ada")
    release(tmp_path, str(tk))
    meta, _ = read_meta(tk)
    assert not meta.get("Owner")
    assert meta["Status"] == "open"
    assert CoordStore(tmp_path).get_claim(str(tk.relative_to(tmp_path))) is None
