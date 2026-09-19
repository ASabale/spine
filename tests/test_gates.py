from pathlib import Path

import pytest

from spine.artifacts import new_work_item, set_status
from spine.errors import EvaluationInvalid, ReviewInvalid
from spine.initcmd import init_target

PASSING_EVAL = """\
passed: true
command: uv run pytest -q
when: "2026-09-19T00:00:00+00:00"
revision: testhash
"""

FAILING_EVAL = """\
passed: false
command: uv run pytest -q
when: "2026-09-19T00:00:00+00:00"
revision: testhash
"""

APPROVING_REVIEW = """\
verdict: approve
by: ada
when: "2026-09-19T00:00:00+00:00"
revision: testhash
evidence: two-axis pass
"""

CHANGES_REVIEW = """\
verdict: request-changes
by: ada
when: "2026-09-19T00:00:00+00:00"
revision: testhash
evidence: bounce
"""


def _checking_item(tmp_path: Path) -> Path:
    init_target(tmp_path)
    wi = new_work_item(tmp_path, "Ship CLI", "software")
    set_status(tmp_path, str(wi), "doing")
    set_status(tmp_path, str(wi), "checking")
    return wi


def test_prose_eval_is_not_a_gate(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text("looks fine\n", encoding="utf-8")
    with pytest.raises(EvaluationInvalid):
        set_status(tmp_path, str(wi), "reviewing")


def test_failing_eval_blocks_reviewing(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(FAILING_EVAL, encoding="utf-8")
    with pytest.raises(EvaluationInvalid):
        set_status(tmp_path, str(wi), "reviewing")


def test_eval_missing_revision_rejected(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(
        "passed: true\ncommand: pytest\nwhen: \"2026-09-19T00:00:00+00:00\"\n",
        encoding="utf-8",
    )
    with pytest.raises(EvaluationInvalid):
        set_status(tmp_path, str(wi), "reviewing")


def test_passing_eval_allows_reviewing(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(PASSING_EVAL, encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")


def test_request_changes_review_blocks_done(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(PASSING_EVAL, encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(CHANGES_REVIEW, encoding="utf-8")
    with pytest.raises(ReviewInvalid):
        set_status(tmp_path, str(wi), "done")


def test_approving_review_allows_done(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(PASSING_EVAL, encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(APPROVING_REVIEW, encoding="utf-8")
    set_status(tmp_path, str(wi), "done")


def test_mismatched_eval_review_revision_blocks_done(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(PASSING_EVAL, encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(
        APPROVING_REVIEW.replace("revision: testhash", "revision: other"),
        encoding="utf-8",
    )
    with pytest.raises(ReviewInvalid):
        set_status(tmp_path, str(wi), "done")
