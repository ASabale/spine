# Software proof artifacts

Type: work-item
Profile: software
Status: done
Owner: 
Claimed-at: 
Links: 
Deliverable: src/spine/artifacts.py

## Intent

Software profile: proof files live in `.spine/evals/` and `.spine/reviews/`. `set-status` to `reviewing` (from `checking`) requires an eval file whose stem matches the work item. `set-status` to `done` from `reviewing` requires a review file. Default profile is unchanged. Tests in `tests/test_proofs.py` only (do not edit `tests/test_spine.py`).