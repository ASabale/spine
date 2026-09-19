---
name: next
description: Pick the next spine action. Use when choosing between the frontier and the board.
---

# next

Run `spine doctor` then `spine status`. Take the first frontier ticket, or the work item whose status is the next gate. Done when the chosen path is claimed or already owned.

```
spine doctor
spine status
```

HITL gates live in `docs/spine/contract.yaml`. Craft: `docs/spine/wires.yaml` concern `next`.
