from pathlib import Path

import pytest

from spine.artifacts import new_work_item, read_meta, set_status
from spine.errors import EvaluationInvalid, ReviewInvalid
from spine.initcmd import init_target


def test_software_checking_needs_eval(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "checking")
    with pytest.raises(EvaluationInvalid, match="evals"):
        set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text("""passed: true\ncommand: uv run pytest -q\nwhen: \"2026-09-19T00:00:00+00:00\"\nrevision: testhash\n""", encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")


def test_software_reviewing_needs_review(tmp_path: Path):
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "checking")
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text("""passed: true\ncommand: uv run pytest -q\nwhen: \"2026-09-19T00:00:00+00:00\"\nrevision: testhash\n""", encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    with pytest.raises(ReviewInvalid, match="reviews"):
        set_status(tmp_path, str(wi), "done")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text("""verdict: approve\nby: ada\nwhen: \"2026-09-19T00:00:00+00:00\"\nrevision: testhash\nevidence: two-axis pass\n""", encoding="utf-8")
    set_status(tmp_path, str(wi), "done")
    meta, _ = read_meta(wi)
    assert meta["Status"] == "done"
