---
name: build
description: Implement a claimed spine work item. Use when status is doing.
---

# build

Claim, then implement the deliverable. Done when the deliverable exists and the next gate is `checking`.

```
spine claim docs/spine/work-items/NN-slug.md
spine set-status docs/spine/work-items/NN-slug.md doing
```

CLI owns metadata. Craft: `docs/spine/wires.yaml` concern `build`.
