from pathlib import Path

import pytest

from spine.artifacts import new_work_item, set_status
from spine.errors import EvaluationInvalid, ReviewInvalid
from spine.events import content_revision
from spine.initcmd import init_target


def _passing_eval(path: Path) -> str:
    return (
        "passed: true\n"
        "command: uv run pytest -q\n"
        'when: "2026-09-19T00:00:00+00:00"\n'
        f"revision: {content_revision(path)}\n"
    )


def _failing_eval(path: Path) -> str:
    return (
        "passed: false\n"
        "command: uv run pytest -q\n"
        'when: "2026-09-19T00:00:00+00:00"\n'
        f"revision: {content_revision(path)}\n"
    )


def _approving_review(path: Path) -> str:
    return (
        "verdict: approve\n"
        "by: ada\n"
        'when: "2026-09-19T00:00:00+00:00"\n'
        f"revision: {content_revision(path)}\n"
        "evidence: two-axis pass\n"
    )


def _changes_review(path: Path) -> str:
    return (
        "verdict: request-changes\n"
        "by: ada\n"
        'when: "2026-09-19T00:00:00+00:00"\n'
        f"revision: {content_revision(path)}\n"
        "evidence: bounce\n"
    )


STALE_EVAL = """\
passed: true
command: uv run pytest -q
when: "2026-09-19T00:00:00+00:00"
revision: testhash
"""

STALE_REVIEW = """\
verdict: approve
by: ada
when: "2026-09-19T00:00:00+00:00"
revision: testhash
evidence: two-axis pass
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
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(_failing_eval(wi), encoding="utf-8")
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
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(_passing_eval(wi), encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")


def test_request_changes_review_blocks_done(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(_passing_eval(wi), encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(_changes_review(wi), encoding="utf-8")
    with pytest.raises(ReviewInvalid):
        set_status(tmp_path, str(wi), "done")


def test_approving_review_allows_done(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(_passing_eval(wi), encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(_approving_review(wi), encoding="utf-8")
    set_status(tmp_path, str(wi), "done")


def test_mismatched_eval_review_revision_blocks_done(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(_passing_eval(wi), encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(
        _approving_review(wi).replace(f"revision: {content_revision(wi)}", "revision: other"),
        encoding="utf-8",
    )
    with pytest.raises(ReviewInvalid):
        set_status(tmp_path, str(wi), "done")


def test_stale_eval_revision_blocks_reviewing(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(STALE_EVAL, encoding="utf-8")
    with pytest.raises(EvaluationInvalid):
        set_status(tmp_path, str(wi), "reviewing")


def test_changed_work_item_invalidates_eval(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(_passing_eval(wi), encoding="utf-8")
    wi.write_text(wi.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
    with pytest.raises(EvaluationInvalid):
        set_status(tmp_path, str(wi), "reviewing")


def test_stale_review_revision_blocks_done(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(_passing_eval(wi), encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(STALE_REVIEW, encoding="utf-8")
    with pytest.raises(ReviewInvalid):
        set_status(tmp_path, str(wi), "done")


def test_changed_work_item_after_review_blocks_done(tmp_path: Path):
    wi = _checking_item(tmp_path)
    (tmp_path / ".spine/evals" / f"{wi.stem}.md").write_text(_passing_eval(wi), encoding="utf-8")
    set_status(tmp_path, str(wi), "reviewing")
    (tmp_path / ".spine/reviews" / f"{wi.stem}.md").write_text(_approving_review(wi), encoding="utf-8")
    wi.write_text(wi.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
    with pytest.raises((EvaluationInvalid, ReviewInvalid)):
        set_status(tmp_path, str(wi), "done")
