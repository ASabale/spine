# HANDOFF

## Current State

Tree version **0.3.0**. Published as **spine-cli 0.3.0** on PyPI and GitHub (`v0.3.0`). Sit-down: `spine prime`. Exec: `spine run`.

**1.0 plan is cut (2026-09-21):** `docs/spine/maps/1.0.md` — destination (a spine the fleet can trust: verifiable authority + an audit trail that proves it), 9 grilling decisions, 6-wave route, fog, out-of-scope. Tickets **16–38** (23, fine-grained): trust chain 16–26, engineering 27–31, docs 32–35, release 36–38. Frontier = wave 0: 16, 19, 20, 25, 27, 32, 34.

Format convention: single-value `Blocked by` (doctor resolves one reference; a comma list is a hazard) + full gate list as a `Gates:` line in the body (21, 23, 24, 35, 36, 38). Coverage 70→85 lives in 36 (release prep), not as a standalone ticket.

Verified green: `uv run pytest -q` (160 passed), `spine doctor` (all parse, no broken refs), `spine status` (frontier correct).

## Next Steps

Awaiting user scan of the numbered breakdown (tickets 16–38). On GO: dispatch the builder per AGENTS.md, wave 0 first (`builder` on local Qwen, `--verify "uv run pytest"`); reviewer pass offered after each wave.
