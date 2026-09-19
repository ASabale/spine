---
name: eval
description: Check a software work item against acceptance. Use when status is checking.
---

# eval

Write proof under `.spine/evals/`. Then:

```
spine set-status docs/spine/work-items/NN-slug.md reviewing
```

Craft: `npx skills add mattpocock/skills -s qa -y`.

## Gate
checking (agent-drivable). Software profile requires this before done.
