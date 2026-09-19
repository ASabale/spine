---
name: new
description: Mint a spine ticket or work item. Use when capturing a new ticket or work item.
---

# new

Run `spine new`. Done when the file exists under `docs/spine/tickets/` or `docs/spine/work-items/`.

```
spine new ticket --title "..." --type grilling
spine new work-item --title "..." --profile software
spine new --title "..." --ticket
spine new --title "..." --work-item
```

CLI owns metadata. Craft for interviewing: `docs/spine/wires.yaml` concern `wayfind`.
