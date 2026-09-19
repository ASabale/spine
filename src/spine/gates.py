from __future__ import annotations

from pathlib import Path

import yaml

from spine.errors import EvaluationInvalid, ReviewInvalid
from spine.model import EXEC_ROOT

# Reviewing → done requires this verdict; the others are legal verdicts that
# simply do not satisfy the gate.
REVIEW_VERDICTS = ("approve", "request-changes", "block")
_DONE_VERDICT = "approve"

_EVAL_FIELDS = ("command", "when", "revision")
_REVIEW_FIELDS = ("by", "when", "revision", "evidence")


def _locate(root: Path, kind: str, stem: str) -> Path | None:
    """Find the gate file for a work item under ``.spine/<kind>/``.

    Applies the same lookup rule as ``artifacts._has_proof``: a file whose
    name contains the stem, or whose stem equals the work-item stem. Returns
    the first match so the caller can parse it.
    """
    folder = root / EXEC_ROOT / kind
    if not folder.is_dir():
        return None
    for p in sorted(folder.iterdir()):
        if p.is_file() and (stem in p.name or p.stem == stem):
            return p
    return None


def _load(root: Path, kind: str, stem: str, invalid: type) -> tuple[Path, dict]:
    """Locate and parse a gate file, raising ``invalid`` on any defect.

    A missing file, a YAML parse error, or a non-mapping (prose) body is
    invalid. Returns the path and the parsed mapping on success.
    """
    path = _locate(root, kind, stem)
    if path is None:
        raise invalid(f"no gate under {EXEC_ROOT / kind}/ for {stem}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise invalid(f"gate {path.name} under {EXEC_ROOT / kind}/ is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise invalid(f"gate {path.name} under {EXEC_ROOT / kind}/ is not a YAML mapping")
    return path, data


def _require_fields(data: dict, path: Path, kind: str, fields: tuple[str, ...], invalid: type) -> None:
    for field in fields:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise invalid(f"gate {path.name} under {EXEC_ROOT / kind}/ missing field {field}")


def require_eval(root: Path, stem: str) -> dict:
    """Require a passing eval gate for ``stem``. Raises ``EvaluationInvalid``.

    The eval file (``.spine/evals/<stem>.md``) must be a YAML mapping with
    ``passed`` true and non-empty ``command``, ``when`` and ``revision``.
    """
    path, data = _load(root, "evals", stem, EvaluationInvalid)
    if data.get("passed") is not True:
        raise EvaluationInvalid(f"eval gate {path.name} is not passing (passed={data.get('passed')!r})")
    _require_fields(data, path, "evals", _EVAL_FIELDS, EvaluationInvalid)
    return data


def require_review(root: Path, stem: str, *, verdict: str = _DONE_VERDICT) -> dict:
    """Require a review gate for ``stem``. Raises ``ReviewInvalid``.

    The review file (``.spine/reviews/<stem>.md``) must be a YAML mapping with
    a legal ``verdict`` and non-empty ``by``, ``when``, ``revision`` and
    ``evidence``. ``verdict`` is the verdict the transition demands; the file's
    verdict must equal it.
    """
    path, data = _load(root, "reviews", stem, ReviewInvalid)
    v = data.get("verdict")
    if not isinstance(v, str) or v not in REVIEW_VERDICTS:
        raise ReviewInvalid(f"review gate {path.name} has invalid verdict {v!r}")
    _require_fields(data, path, "reviews", _REVIEW_FIELDS, ReviewInvalid)
    if v != verdict:
        raise ReviewInvalid(f"review gate {path.name} verdict {v!r} does not satisfy required {verdict!r}")
    return data