---
name: doctor
description: Recover spine drift. Use at session start and when artifacts look wrong.
---

# doctor

Run the CLI. Done when `spine doctor` prints `ok` or every reported line is understood.

```
spine doctor
spine evolve
```

Doctor applies stale claims, dangling links, and missing `Blocked by` rollups. It reports unknown statuses, missing spec files, and gitignore drift. Craft refresh: `spine evolve`.
