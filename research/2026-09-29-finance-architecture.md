# Finance architecture review — 2026-09-29

HTML report: `/var/folders/z3/gmpk7cz57qn9h1f_f15p3kq00000gn/T/architecture-review-20260929-184608.html`

US ledger only. The India module stays on its own seam and is not a candidate. `backups/`, `documents/`, `finance.db`, and `legacy/` exist and were not read. No code was edited.

## Ranked

1. **Strong** — Record a close as complete. One `balances` row sets `estimated` false, so a partial month becomes recorded net worth and the plan anchor. A card balance would add to locked because `PORTABLE_KINDS` omits `card`. The missing-balance flag skips card kind; `setBalance` does not.
2. **Strong** — Count a month in one place. Partial, thin, and `reliableFrom` are re-decided in analytics, `summarizeCategories`, the plan, insights, status text, and the spending charts. `spend12` drops thin months; `income12` sums the wider slice. The savings chart bars gross against a clipped net rate. The three-month average includes the open month. A thin unfinished month stops the `reliableFrom` walk on the first step and leaves it at `HISTORY_START`.
3. **Strong** — Allocate spend to the covered month. `partsOf` is private to `analyze`. Monthly Housing, housing history, and student years use `covers`. Category detail and `queryTransactions` use `posted_on` and the whole amount.
4. **Strong** — Price a repeat from its cadence. Recurring means three distinct months. `perMonth` divides by months with a charge. `cadenceDays` is stored and unused by that rate. Housing and Education are excluded from the recurring predicate and not from daily, weekday, or the large-purchase list.
5. **Strong** — Read the ledger once, test through a fixture. `analyze` always loads every series and the full transaction list from the live database. `snapshot()` and `analysis()` cache apart, so the first scenario rebuilds the ledger. `queryTransactions` builds the snapshot to tag recurring, then filters after `LIMIT`. Tests call `analyze()` on `finance.db` at import and skip the hand baseline once the file moves. `schema.sql` omits `covers`, `rules`, `audit`, `settings`, the `india_*` tables, and the indexes in `APP_SCHEMA`.
6. **Worth exploring** — Step the checkpoint on one path. `buildPlan` adds a constant; `scenario` compounds; `vsBase` subtracts them. The base path stays rate zero, with payroll savings in and market return and loan principal paydown out, as `context.md` already sets.

## Seams

Module paths only.

### Analytics

- `app/server/src/core/analytics.ts`
- `app/server/src/core/plan.ts`
- `app/server/src/core/insights.ts`
- `app/server/src/core/snapshot.ts`
- `app/server/src/core/report.ts`
- `app/server/src/core/search.ts`
- `app/server/src/core/taxonomy.ts`
- `app/server/src/core/mutations.ts`
- `app/shared/categories.ts`
- `app/shared/types.ts`
- `app/web/src/pages/spending.tsx`
- `app/web/src/pages/habits.tsx`
- `app/web/src/pages/accounts.tsx`
- `app/web/src/pages/plan.tsx`
- `app/web/src/charts/bars.tsx`
- `app/web/src/charts/timeline.tsx`
- `app/web/src/charts/scatter.tsx`
- `app/web/src/charts/scenario.tsx`
- `app/server/src/core/analytics.test.ts`

### Performance

- `app/server/src/core/analytics.ts`
- `app/server/src/core/snapshot.ts`
- `app/server/src/core/search.ts`
- `app/server/src/api.ts`
- `app/server/src/cli.ts`
- `app/server/src/core/db.ts`
- `schema.sql`
- `app/server/src/core/analytics.test.ts`
