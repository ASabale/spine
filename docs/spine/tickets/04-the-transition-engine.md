# The transition engine

Type: task
Status: open
Blocked by: 03-the-contract-machine.md
Owner: 
Claimed-at: 

## Question

Build the single transition guard every command funnels through:
`advance(item, to, actor, reason, run_id)` → validate (legal transition, required proof present
+ current, HITL gate, claim held) → record (append event + update frontmatter atomically) → run
side-effects → return a structured result or a typed error. No command bypasses it.

Decide the structured error types (InvalidTransition, ClaimConflict, EvaluationInvalid,
ReviewInvalid, HumanInterventionRequired, …) and the stable exit-code scheme (0 ok, 1 general,
2 usage, 3 bad transition, 4 claim conflict, 5 validation, 6 HITL, 7 external, 8 inconsistent).
Resolved = every mutation is one guarded, recorded, idempotent call. Invariants locked: #3, #10.