---
name: next
description: Pick the next spine action from the map frontier and work-item board.
---

# next

Run `spine doctor` then `spine status`. Take the first open unblocked unclaimed ticket, or the work item whose status is the next gate.

```
spine doctor
spine status
```

Craft router (optional): `npx skills add mattpocock/skills -s ask-matt -s implement -y`.

## Gate
Respect HITL: do not `set-status` to `reviewing` verdicts or mint work items without a human if the contract marks them HITL.
