---
name: wayfind
description: Plan with a spine map and tickets. Use when the way to a destination is foggy or multi-session.
---

# wayfind

Planning lives on the map, not on the work item. Load `docs/spine/maps/`, work frontier tickets under `docs/spine/tickets/`. Claim a ticket with the CLI before work.

```
spine status
spine new ticket --title "..." --type research
spine claim tickets/NN-slug.md
```

Do not vendor Wayfinder. Install craft from skills.sh: `npx skills add mattpocock/skills -s wayfinder -s grilling -s domain-modeling -y`.

## Gate
No work-item status for planning. Create a work item at `ready` only when the way is clear.
