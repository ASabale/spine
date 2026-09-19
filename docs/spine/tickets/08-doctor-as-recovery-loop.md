# Doctor as recovery loop

Type: task
Status: resolved
Blocked by: 
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

## Answer

`spine doctor` is the wake-up recovery loop. It scans every ticket and work item
and repairs what it can:

- unknown / illegal status → `ready` (work item) or `open` (ticket)
- frontmatter Status vs last `.spine/events.jsonl` entry → restore the logged status
- stale claims → release
- missing Links → drop
- missing `Blocked by` (number, filename, or path) → clear
- `Blocked by` pointing at a resolved ticket → clear

Each FIX line is `before → after (why)`. `--report-only` does not mutate.
A second apply is a no-op. CLI `doctor` / `prime` exit 0 when `doctor_ok`, else 8
(`InconsistentState`). Unrepairable REPORT (missing spec files, gitignore, version
skew) keeps exit 8.
