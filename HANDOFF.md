# HANDOFF

## Current State

Tree version **0.2.0**. Published as **spine-cli 0.2.0** on PyPI and GitHub (`v0.2.0`). Sit-down: `spine prime`. Exec: `spine run`.

Productionize route (full orchestration): tickets 02–07 resolved. Next: 08 doctor as recovery loop. Product ticket `01-dogfood-this-target` stays open HITL.

P3a delivered: `.spine/events.jsonl` from `engine.advance`; `content_revision` is sha256 of the work-item body; eval/review must match that digest. Claims table is ticket 10.

## Next Steps

Stranger install: `uvx --from spine-cli spine init`. Verify: `uv run pytest -q`.
