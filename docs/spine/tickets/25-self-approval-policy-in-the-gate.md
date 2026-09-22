# Self-approval policy in the gate

Type: task
Status: open
Blocked by:
Owner:
Claimed-at:

## Question

The review gate requires non-empty `by`, but the item's owner can approve their
own work item — a self-approval hole. Enforce per profile: the software profile
rejects `by == Owner`; non-software profiles allow it (flagged).

Resolved = self-approved review on a software item fails the gate; non-software
passes, flagged.

- [ ] Self-approved review on a software work item fails the gate (typed error)
- [ ] Self-approved review on a non-software item passes
- [ ] Profile policy lives in the contract (explicit, not implicit)
- [ ] `make test` green
