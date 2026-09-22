# reason lands in the event log

Type: task
Status: open
Blocked by:
Owner:
Claimed-at:

## Question

`advance` accepts `reason` and discards it. Reason must land in the event log:
every recorded mutation carries its reason (absent = empty, back-compatible).

Resolved = event log lines carry reason when provided; surfaces show it.

- [ ] Event log lines carry reason when provided (old lines stay readable)
- [ ] Existing consumers (doctor, evolve, query) tolerate the field
- [ ] `spine show` / rollups surface the last reason
- [ ] `make test` green
