# Spec alignment with 1.0 behavior

Type: task
Status: open
Blocked by: 24-doctor-repairs-through-the-engine.md
Owner:
Claimed-at:

## Question

The spec still describes the 0.3-era behavior (no owner check, discarded
reason, unused HITL error). Align the spec's engine/gates/doctor sections with
the 1.0 behavior.

Gates: 17, 18, 20, 24, 26

Resolved = every trust behavior in the code is described in the spec; no stale
claims remain.

- [ ] Spec documents: owner-checked advance, mutation funnel, reason in log, typed exit 6, self-approval policy
- [ ] No stale 0.3-era claims remain in the spec
- [ ] Spec claims verified against the CLI (dogfood pass)
