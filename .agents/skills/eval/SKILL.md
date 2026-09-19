---
name: eval
description: Check a software work item against acceptance. Use when status is checking.
---

# eval

Write proof at `.spine/evals/<work-item-stem>.md`. Done when every acceptance line has a pass/fail and the file exists.

```
spine set-status docs/spine/work-items/NN-slug.md reviewing
```

Craft: `docs/spine/wires.yaml` concern `eval`.
