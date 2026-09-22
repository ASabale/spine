# ruff lint

Type: task
Status: open
Blocked by:
Owner:
Claimed-at:

## Question

`make lint` is `compileall` — a syntax check, not a linter. Adopt ruff as the
linter: configured, findings fixed, wired into `make lint` and `make release`.

Resolved = `make lint` runs ruff; the codebase is clean; the gate is real.

- [ ] `make lint` runs ruff (lint rules configured)
- [ ] Findings fixed (or explicitly justified per finding)
- [ ] `make release` uses the new lint; CI green
