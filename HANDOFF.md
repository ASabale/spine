# HANDOFF

## Current State

Tree version **0.3.0**. Published as **spine-cli 0.3.0** on PyPI and GitHub (`v0.3.0`). Sit-down: `spine prime`. Exec: `spine run`.

**1.0 tickets are sliced for one local-agent session each (2026-09-23).** Map: `docs/spine/maps/1.0.md`. Tickets **16–42**. Coverage is ticket 42, not ticket 36. Ticket 36 is changelog and version only. Ticket 38 is a human checklist (no tag, no push, no publish).

Ticket 16's code is delivered. `spine.claims` owns claim, release, staleness, and identity. `artifacts` re-exports those four names. Ticket 20 requires `SPINE_HUMAN=1` for a new work item and for `reviewing` → `done`. The CLI and doctor share one resolver: a path, an exact name, a zero-padded `NN-` number, or a unique substring. `1` binds `01-…` and does not bind `11-…` or `116-…`. Two matches raise, and doctor leaves an ambiguous blocker in place. Eval and review YAML under `.spine/evals/` and `.spine/reviews/` are checked in; `coord.db`, claim files, and `events.jsonl` stay gitignored. `uv run pytest`: 176 passed. Status was not edited by hand. Plan: `research/2026-09-30-execution-plan.md`.

Second waits are hard stops in `## Question`, not a `Gates:` line. `Blocked by` stays one filename.

## Next Steps

Next spine code: ticket 25, self-approval in the review gate. Finance next: one month count for partial, thin, and `reliableFrom`, shared by `spend12` and `income12`. Recorded-close is in `close.ts`. Do not tag or publish.


[You have received this identical output 3 times. Re-reading '/Users/akshay/Development/spine/HANDOFF.md:raw' will not change it — use a narrower selector (path:A-B), or proceed with the edit.]