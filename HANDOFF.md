# HANDOFF

## Current State

Tree version **0.2.0**. Published as **spine-cli 0.2.0** on PyPI and GitHub (`v0.2.0`). Sit-down: `spine prime`. Exec: `spine run`.

Productionize route (full orchestration): tickets 02–10 resolved. Next: 11 scale and concurrency harness. Product ticket `01-dogfood-this-target` stays open HITL.

P4a delivered: SQLite claims table, one-winner INSERT, owner-only release (stale/doctor force). engine.py stays sqlite-free.

## Next Steps

Stranger install: `uvx --from spine-cli spine init`. Verify: `uv run pytest -q`.
