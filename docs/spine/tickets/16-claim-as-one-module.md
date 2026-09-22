# Claim as one module

Type: task
Status: open
Blocked by:
Owner:
Claimed-at:

## Question

Claim logic today is spread across the artifacts layer (claim / release / stale)
calling into the coordination store. Make Claim one module: one place owns
taking, releasing, staleness, and owner lookup for a claimed artifact, and all
callers (CLI, doctor, engine) go through that seam. Behavior unchanged; the
module is testable as a unit.

Resolved = one module owns the claim lifecycle; no claim logic left in the
caller layers; concurrency one-winner intact.

- [ ] One module owns claim/release/staleness/owner lookup; no claim logic left in the artifacts layer
- [ ] `spine claim` / `spine release` behavior unchanged, including conflict messages
- [ ] Stale policy (4h, contract-configurable) enforced from the one place
- [ ] Concurrency harness still passes (one winner per claim); `make test` green
