# Doctor as recovery loop

Type: task
Status: open
Blocked by: 04-the-transition-engine.md
Owner: 
Claimed-at: 

## Question

Turn `doctor` from a partial checker into an idempotent, deterministic recovery loop over the
same machine + full scan. It must detect AND repair: unknown/illegal statuses, stale claims,
broken/orphaned links, resolved-but-still-blocking `Blocked by`, and mid-write corruption
(reconcile frontmatter against the event log). Standardize the `Blocked by` reference format
(bare filename vs path — the current parser is shallow) and make it accept either. Every action
prints before/after/why; re-running changes nothing (idempotent). Adopt the rich exit-code scheme.

Resolved = doctor is the recovery path an agent runs on wake and it converges. Invariants locked:
#7, #8.