---
name: review
description: Verdict a software work item. Use when status is reviewing.
---

# review

Write a YAML mapping at `.spine/reviews/<work-item-stem>.md` on two axes (spec and standards): `verdict` (`approve` / `request-changes` / `block`), `by`, `when`, `revision` (same body hash as the eval), `evidence`.

Pass (`verdict: approve`):

```
spine set-status docs/spine/work-items/NN-slug.md done
```

Bounce (`verdict: request-changes`):

```
spine set-status docs/spine/work-items/NN-slug.md changes-requested
```

Craft: `docs/spine/wires.yaml` concern `review`.
