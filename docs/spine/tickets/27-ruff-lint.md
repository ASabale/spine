# ruff lint

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

`make lint` is `python -m compileall`. There is no ruff.

Add ruff as a dev dependency. `make lint` runs `ruff check src tests` and compileall, and that command exits 0. `make release` already depends on `lint`; do not add a second path. Do not run `ruff format` in this ticket (ticket 28).

Fix only the diagnostics ruff reports on the first run. Do not add extra rule sets. If a diagnostic needs a design choice, stop and leave a one-line note in this ticket.

Resolved = `make lint` runs ruff and is clean.

- [x] ruff is a dev dependency
- [x] `make lint` runs `ruff check` and exits 0
- [x] `make release` still calls the `lint` target
- [x] Verify: `make lint`