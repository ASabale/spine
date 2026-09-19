# Real gates: eval and review

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

Make checking→reviewing (eval) and reviewing→done (review) real machine-verifiable gates, not
"does a file exist?" Define the structured format + schema for each:
- eval: the test commands actually run, pass/fail, which revision, when.
- review: verdict (approve / request-changes / block), evidence, which revision, by whom, when.

Decide validation (a passing gate requires real passing results; a stale or missing one blocks)
and the content rules. Resolved = the machine checks the proof's content and freshness, not its
existence. Invariant locked: #1 (done ⇒ valid passing eval + approving review on the same
revision).

## Answer

Gates are YAML mappings on disk, not file existence. `spine.gates.require_eval` /
`require_review` parse `.spine/evals/<stem>.md` and `.spine/reviews/<stem>.md`.

Eval: `passed` (bool, must be true), `command`, `when`, `revision` (non-empty strings).
Review: `verdict` in `{approve, request-changes, block}`, plus `by`, `when`,
`revision`, `evidence`. `reviewing → done` requires `verdict: approve`.

Prose, missing file, missing field, YAML error, or `passed: false` raises
`EvaluationInvalid` / `ReviewInvalid` (CLI 5). Schema listed under `contract.yaml`
`gates:`. Same-revision binding (eval.revision == review.revision == content hash)
is ticket 07.