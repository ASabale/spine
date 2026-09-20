---
name: eval
description: Check a software work item against acceptance. Use when status is checking.
---

# eval

Write a YAML mapping at `.spine/evals/<work-item-stem>.md` with `passed: true`, `command`, `when`, and `revision` equal to the work-item body hash. Done when `spine set-status … reviewing` succeeds.

```
spine set-status docs/spine/work-items/NN-slug.md reviewing
```

Craft: `docs/spine/wires.yaml` concern `eval`.
