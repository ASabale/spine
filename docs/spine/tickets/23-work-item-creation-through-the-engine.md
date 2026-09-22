# Work item creation through the engine

Type: task
Status: open
Blocked by: 21-claim-release-through-the-engine.md
Owner:
Claimed-at:

## Question

`spine new` writes the work-item file directly. Route creation through the
engine: creating a work item is a recorded mutation, and
`creating-work-item` (contract HITL) is enforced — humans create work items; an
agent-driven creation is a typed human-intervention.

Gates: 20, 21

Resolved = work item creation is a logged engine mutation, human-gated per
contract.

- [ ] `spine new` creates via the engine path
- [ ] Creation appends an event log line (with reason)
- [ ] Agent-driven creation → typed human-intervention (exit 6); human proceeds
- [ ] `make test` green
