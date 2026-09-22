# Human-intervention error wired

Type: task
Status: open
Blocked by:
Owner:
Claimed-at:

## Question

`HumanInterventionRequired` is defined but never raised, and human-gated
mutations can silently succeed for the wrong actor. Wire it: a human-gated
transition (contract HITL) attempted by an unauthorized actor raises the typed
error (exit 6); the human proceeds.

Resolved = unauthorized human-gated mutation exits 6; the human proceeds.

- [ ] Unauthorized actor on a human-gated transition → typed error, exit 6
- [ ] Human proceeds on the same transition
- [ ] `spine run` still returns `run=[]` for HITL-only states
- [ ] No silent success on human-gated mutations
- [ ] `make test` green
