---
name: review
description: Review a software work item. Use when status is reviewing.
---

# review

HITL verdict. Proof under `.spine/reviews/`. Pass:

```
spine set-status docs/spine/work-items/NN-slug.md done
```

Bounce:

```
spine set-status docs/spine/work-items/NN-slug.md changes-requested
```

Craft: `npx skills add mattpocock/skills -s code-review -y`.

## Gate
reviewing (HITL). Software profile requires this before done.
