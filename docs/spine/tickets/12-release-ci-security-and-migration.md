# Release, CI, security and migration

Type: task
Status: open
Blocked by: 11-scale-and-concurrency-harness.md
Owner: 
Claimed-at: 

## Question

Make it shippable. CI gates: unit + integration + invariant suite + concurrency harness +
type-check + lint + coverage + build + smoke test, all required before merge; one `make test`
path for devs. Packaging (PyPI) + versioned releases + changelog. Security review (no path
traversal, no symlink escape, no shell injection, input validation, safe file ops). Migration
strategy: detect the repo version, plan it, run it transactionally, verify after, with a dry-run
and a rollback.

Resolved = `make release` is a defined, gated path and migration is non-destructive.