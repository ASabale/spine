# Zero pyright errors

Type: task
Status: open
Blocked by: 29-pyright-baseline.md
Owner:
Claimed-at:

## Question

The baseline (29) is a list of known errors. Clear it: fix findings, raise
strictness, until the typecheck is clean and real.

Gates: 29

Resolved = `make typecheck` passes with zero errors.

- [ ] Zero pyright errors
- [ ] No unexplained `# type: ignore` (or documented pattern)
- [ ] `make release` fully green
