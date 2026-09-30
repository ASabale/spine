# HANDOFF

## Current State

Tree version **0.3.0**. Published as **spine-cli 0.3.0** on PyPI and GitHub (`v0.3.0`). Sit-down: `spine prime`. Exec: `spine run`.

**1.0 tickets are sliced for one local-agent session each (2026-09-23).** Map: `docs/spine/maps/1.0.md`. Tickets **16–42**. Coverage is ticket 42, not ticket 36. Ticket 36 is changelog and version only. Ticket 38 is a human checklist (no tag, no push, no publish).

Ticket 16's code is delivered. `spine.claims` owns claim, release, staleness, and identity. `artifacts` re-exports those four names. `uv run pytest`: 161 passed. The ticket's Status was not edited by hand. Plan: `research/2026-09-30-execution-plan.md`.

Second waits are hard stops in `## Question`, not a `Gates:` line. `Blocked by` stays one filename.

## Next Steps

Next spine code: when `advance` sends a ticket to `open`, drop the coord row through `spine.claims` (engine stays free of `CoordStore`). Then ticket 19. Finance work is the recorded-close slice in `/Users/akshay/Development/finance`, on a fixture, not on `finance.db`. Do not tag or publish.


[You have received this identical output 3 times. Re-reading '/Users/akshay/Development/spine/HANDOFF.md:raw' will not change it — use a narrower selector (path:A-B), or proceed with the edit.]