# HANDOFF

## Current State

Tree version **0.2.0**. Published as **spine-cli 0.2.0** on PyPI and GitHub (`v0.2.0`). Sit-down: `spine prime`. Exec: `spine run`.

Productionize route (full orchestration): tickets 02–06 resolved. Next: 07 evidence, event log, and revision binding. Product ticket `01-dogfood-this-target` stays open HITL.

P2 delivered: `src/spine/store.py` (`FileStore`, `CoordStore` kv) and `src/spine/query.py` (next/board/status_payload). `artifacts.py` re-exports those query names as the same function objects. Claims table is ticket 10.

## Next Steps

Stranger install: `uvx --from spine-cli spine init`. Verify: `uv run pytest -q`.
