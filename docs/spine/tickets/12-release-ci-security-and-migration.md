# Release, CI, security and migration

Type: task
Status: resolved
Blocked by: 
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

## Answer

`make test` is the dev path. `make release` runs lint (`compileall`), typecheck
(import smoke), pytest, invariant+harness, coverage ≥70%, `uv build`, and CLI
smoke. GitHub Actions runs `make release` on push/PR. `spine migrate`
`--dry-run` / apply / `--rollback` backs up `contract.yaml` and `coord.db`,
upgrades, verifies, and restores on failure. Resolve stays inside `docs/spine`
(symlink-safe). Subprocess calls are argv lists, never `shell=True`. Changelog
tracks Unreleased vs 0.2.0.