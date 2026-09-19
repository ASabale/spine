# HANDOFF

## Current State

Tree version **0.2.0**. Published as **spine-cli 0.2.0** on PyPI and GitHub (`v0.2.0`). Sit-down: `spine prime`. Exec: `spine run`. Mutating verbs print `## Next`; `--json` prints `status_payload`. Prime JSON includes `cwd`, `ok`, `inited`.

Productionize route (full orchestration): P0–P1 tickets 02–03 resolved; 04 in flight (`advance()` in `src/spine/engine.py`, typed `SpineError` exit codes). Product ticket `01-dogfood-this-target` stays open HITL.

## Next Steps

Stranger install: `uvx --from spine-cli spine init`. Verify: `uv run pytest -q`.
