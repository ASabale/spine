# Execution plan — 2026-09-30

Decisions are locked. Evidence is the three reports from 2026-09-29. Do not re-research them.

## Spine

One repo, one machine. No server, no MCP, no multi-machine sync in this pass. Do not tag or publish.

1. **Claim is one module.** Done. `spine.claims` owns take, release, staleness, and identity. `artifacts` re-exports those four names and does not touch the claim table. `uv run pytest`: 161 passed. Ticket 16 checkboxes are marked. Status was not edited by hand.
2. **Returning a ticket to open drops the lock.** `advance` to `open` clears Owner and Claimed-at and leaves the coord row. `release` already drops it. Next code change: one test, then the open transition drops the row through `spine.claims`, not a second writer. `engine.py` still must not mention `CoordStore`.
3. **Wave 0 continues at ticket 19** (reason in the event log), then 20, 25, 27, 32, 34, 39, in map order, one ticket at a time. Ticket 21 stays blocked by 19. Ticket 24 (doctor through the engine) stays blocked.
4. **Proofs a second checkout can verify.** After 19. Smallest slice: eval and review YAML are readable from a clone; `coord.db` and the claim files stay gitignored. Not a sync product.
5. **Resolver.** CLI substring match and doctor number match can bind the same token to different tickets. One resolver, used by both, with a test for the collision. Do this after the open-lock fix, before new product surface.

A slice is commitable when its verify command passes. Spine verify: `uv run pytest` from this repo.

## Finance

Repo: `/Users/akshay/Development/finance`. Separate commits from spine. Do not open `finance.db` as a source of truth, and do not read `backups/`, `documents/`, or `legacy/`. India stays on its own seam.

1. A month is recorded net worth only when the close covers every account. One balance row must not set `estimated` false or become the plan anchor. A card balance is debt, not locked cash.
2. Partial, thin, and `reliableFrom` are decided in one place. `spend12` and `income12` use that same window.
3. Spend that has covers is allocated to the covered month in category detail and search, not only in the monthly rollup.
4. A repeat's monthly price uses its cadence, not only months that happened to have a charge. Housing and Education follow the same exclude rule in every list.
5. Tests of those rules run on a fixture. The live ledger is not imported at test load.
6. The plan steps a checkpoint on one path.

Verify each slice with the finance test runner against the fixture, then the existing suite.
