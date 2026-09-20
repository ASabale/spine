# Align spec.md with the 0.2.0 tree

Type: task
Status: resolved
Blocked by: 
Owner: ASabale
Claimed-at: 2026-09-20T00:56:57.122578+00:00

## Question

`spec.md` still lists contract migration as deferred, omits `migrate` from the
main verb list, and describes claim as person-zero. Make `spec.md` (and README
if it still drifts) describe the fleet-capable 0.2.0 tree: one-winner claims,
real YAML eval/review gates, doctor recovery, structured `run`, `spine migrate`.

Do not bump the version or publish. Do not re-scope the engine. Feed in findings
from [Review the productionize diff](14-review-the-productionize-diff.md).

## Answer

`spec.md` now describes the 0.2.0 tree: one-winner claims, YAML eval/review
bound to the body hash, doctor as recovery loop (exit 8), structured `{cmd,
hitl}` `run`, `spine migrate`. Execution tier names `events.jsonl` and
`coord.db`. README, `docs/spine/README.md` (and `initcmd.README`), binder
eval/review skills, AGENTS.md, CHANGELOG, and `productionize.md` fog match.
Architecture deepenings from ticket 14 stay off this map.