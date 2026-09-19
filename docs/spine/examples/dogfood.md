# Dogfood: spine on spine

Canonical proof that the productionized spine can drive a software work item
to `done` on a real target, including a crash and a second worker.

The automated copy is `tests/test_dogfood.py`. This repo is itself a spine
target (`docs/spine/contract.yaml`); `spine status` and `spine prime` work
here. The route below uses a throwaway target so it does not rewrite live
tickets.

## Route

```
spine init
spine new work-item --title "Ship the route" --profile software
spine claim docs/spine/work-items/01-ship-the-route.md
# second worker: spine claim … → ClaimConflict (exit 4)
spine set-status docs/spine/work-items/01-ship-the-route.md doing
spine set-status docs/spine/work-items/01-ship-the-route.md checking
```

Simulate a crash by setting frontmatter `Status` back to `ready` while
`.spine/events.jsonl` still says `checking`. Then:

```
spine doctor
# FIX status … ready → checking from event log
```

Write a real eval (YAML, `passed: true`, `revision` = work-item body hash),
then:

```
spine set-status … reviewing
```

Write a real review (`verdict: approve`, same `revision`), then:

```
spine set-status … done
```

Eval and review must share the content hash of the work-item **body**.
Changing Status/Owner does not invalidate them.

## Proof

`uv run pytest tests/test_dogfood.py -q` is green. `make release` includes it.
