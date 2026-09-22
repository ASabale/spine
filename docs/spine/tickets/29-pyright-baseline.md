# pyright baseline

Type: task
Status: open
Blocked by: 28-ruff-format.md
Owner:
Claimed-at:

## Question

`make typecheck` is an import smoke — it proves modules import, nothing else.
Adopt pyright: run it over the source and record the baseline error set.

Gates: 28

Resolved = `make typecheck` runs pyright; baseline recorded; gate deterministic.

- [ ] `make typecheck` runs pyright over the source
- [ ] Baseline error set recorded; gate passes with the baseline
- [ ] `make release` green
