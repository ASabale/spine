---
name: review
description: Verdict a software work item. Use when status is reviewing.
---

# review

Write proof at `.spine/reviews/<work-item-stem>.md` on two axes: spec and standards. Done when the verdict is `done` or `changes-requested` and the file exists.

Pass:

```
spine set-status docs/spine/work-items/NN-slug.md done
```

Bounce:

```
spine set-status docs/spine/work-items/NN-slug.md changes-requested
```

Craft: `docs/spine/wires.yaml` concern `review`.
