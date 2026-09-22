# Claim/release through the engine

Type: task
Status: open
Blocked by: 16-claim-as-one-module.md
Owner:
Claimed-at:

## Question

Claim and release mutate frontmatter directly, bypassing the engine. Route them
through the engine's mutation path: every claim/release is a recorded mutation
(reason carried, event appended) — the engine becomes the sole mutation point
for claim state.

Gates: 16, 19

Resolved = no claim-state mutation happens outside the engine; every
claim/release is a logged event.

- [ ] `spine claim` / `spine release` mutate via the engine path
- [ ] Every claim/release appends an event log line (with reason)
- [ ] No direct frontmatter writes from the CLI for claim state
- [ ] Concurrency harness still one-winner; `make test` green
