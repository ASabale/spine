# HANDOFF

## Current State

Tree version **0.2.0**. Published as **spine-cli 0.2.0** on PyPI and GitHub (`v0.2.0`). Sit-down: `spine prime`. Exec: `spine run`.

Productionize route (full orchestration): tickets 02–08 resolved. Next: 09 deterministic next and structured run. Product ticket `01-dogfood-this-target` stays open HITL.

P3b delivered: `spine doctor` repairs unknown/illegal status, event-log drift, stale claims, dangling links, and resolved/missing blockers. `Blocked by` accepts path or filename. FIX lines are before → after (why). `doctor`/`prime` exit 8 on unrepaired inconsistency. Claims table is ticket 10.

## Next Steps

Stranger install: `uvx --from spine-cli spine init`. Verify: `uv run pytest -q`.
