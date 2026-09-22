# Doctor repairs through the engine

Type: task
Status: open
Blocked by: 22-link-mutations-through-the-engine.md
Owner:
Claimed-at:

## Question

Doctor repairs (status drift, unknown status) call `write_meta` directly, and
claim/link repairs call the artifacts layer. Doctor must only DETECT; every
repair goes through the engine's paths (status via advance; claim and links via
the family paths).

Gates: 21, 22

Resolved = doctor makes no direct mutations; every repair produces a logged
event; idempotency preserved.

- [ ] No `write_meta` from doctor outside engine calls
- [ ] Every repair (status drift, unknown status, stale claim, broken link) produces a logged event
- [ ] Doctor idempotency preserved (second apply = no-op)
- [ ] Doctor exit 8 on unrepaired unchanged; `make test` green
