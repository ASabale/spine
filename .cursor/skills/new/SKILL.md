---
name: new
description: Capture a map ticket or work item via the spine CLI. Use when something new must be recorded in the target.
---

# new

Mint artifacts with the CLI. Do not hand-edit status, owner, claim, links, or numbers.

```
spine new ticket --title "..." --type grilling
spine new work-item --title "..." --profile software
```

Craft skills for interviewing live on skills.sh. Default wire: `mattpocock/skills` `grill-me` / `wayfinder` (`npx skills add mattpocock/skills -s grill-me -s wayfinder -y`). See `docs/spine/wires.yaml`.

## Gate
creating-work-item is HITL. Tickets start `open`. Work items start `ready`.
