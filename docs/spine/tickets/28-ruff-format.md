# ruff format

Type: task
Status: open
Blocked by: 27-ruff-lint.md
Owner:
Claimed-at:

## Question

No formatter exists. Apply ruff format across the codebase and make the format
check part of the gate.

Gates: 27

Resolved = tree formatted; the gate checks format.

- [ ] Codebase formatted (clean tree passes the format check)
- [ ] `make lint` includes the format check
- [ ] `make test` green after format
