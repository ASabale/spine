# Self-approval recorded and surfaced

Type: task
Status: open
Blocked by: 25-self-approval-policy-in-the-gate.md
Owner:
Claimed-at:

## Question

Allowed self-approval (25) must be recorded, not invisible: the review
frontmatter carries a flag, the event log carries it, and show/rollups display
it.

Gates: 25

Resolved = every review carries the self-approval marker; surfaces display it.

- [ ] Review frontmatter carries the self-approval marker (e.g. `self: true`)
- [ ] The marker rides the event log line
- [ ] `spine show` / rollups surface the marker
- [ ] doctor / evolve tolerate the field; `make test` green
