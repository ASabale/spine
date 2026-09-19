from pathlib import Path

import pytest

from spine.artifacts import new_work_item, read_meta, set_status
from spine.initcmd import init_target


def test_software_checking_needs_eval(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "checking")
    with pytest.raises(ValueError, match="evals"):
        set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text("eval\n", encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")


def test_software_reviewing_needs_review(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "checking")
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text("eval\n", encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    with pytest.raises(ValueError, match="reviews"):
        set_status(tmp_path, str(wi), "done")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text("ship\n", encoding="utf-8")
    set_status(tmp_path, str(wi), "done")
    meta, _ = read_meta(wi)
    assert meta["Status"] == "done"
