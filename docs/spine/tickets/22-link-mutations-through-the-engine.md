# Link mutations through the engine

Type: task
Status: open
Blocked by: 21-claim-release-through-the-engine.md
Owner:
Claimed-at:

## Question

`link` (and doctor's broken-link repair) rewrite Links frontmatter directly.
Route every link mutation (create, remove) through the engine, recorded.

Gates: 21

Resolved = no Links mutation happens outside the engine; link mutations are
logged.

- [ ] `spine link` and doctor's broken-link repair mutate via the engine
- [ ] Link create/remove appends event log lines
- [ ] No direct Links writes outside the engine
- [ ] `make test` green
