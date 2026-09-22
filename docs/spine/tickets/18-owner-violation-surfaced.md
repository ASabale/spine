# Owner violation surfaced

Type: task
Status: open
Blocked by: 17-owner-checked-advance.md
Owner:
Claimed-at:

## Question

The owner violation (17) must be visible on every surface: the CLI exits with a
documented code and message; doctor reports the state; show/next reflect that a
claimed item is not advance-able by other actors.

Resolved = wrong-actor `set-status` exits typed; doctor and board reflect it.

- [ ] `spine set-status` with wrong actor → documented exit code + message (scheme extended or mapped, documented)
- [ ] `spine doctor` reports the owner-violation state
- [ ] `spine show` / `next` reflect that a claimed item is not advance-able by other actors
- [ ] No silent failure on a violation
