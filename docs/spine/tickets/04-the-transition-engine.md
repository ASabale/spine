# The transition engine

Type: task
Status: resolved
Blocked by: 
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

## Answer

Every `set-status` goes through `spine.engine.advance(root, spec, nxt, *, actor, reason, run_id) -> AdvanceResult`. Same-status is a no-op (`changed=False`). Typed errors live in `spine.errors` with stable CLI exit codes: 0 ok, 1 general, 2 usage, 3 `InvalidTransition`, 4 `ClaimConflict`, 5 `EvaluationInvalid`/`ReviewInvalid`/`ContractError`, 6 HITL, 7 external, 8 inconsistent.

Deferred: event-log record + atomic fsync (07), claim-held / lease (10), HITL as a hard gate inside `advance` (09). Proof content (not existence) is 05.