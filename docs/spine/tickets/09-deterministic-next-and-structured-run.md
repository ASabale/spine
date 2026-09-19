# Deterministic next and structured run

Type: task
Status: open
Blocked by: 04-the-transition-engine.md
Owner: 
Claimed-at: 

## Question

Make `next` deterministic and prioritized (a stable, documented ordering over active work items
and tickets; same state → same next) and make `run` a structured, machine-readable plan (ordered
commands + HITL gates), not prose lines. The `next` rules should come from the contract, not
hardcoded lists.

Resolved = an agent can consume `run` as JSON and act, and two agents on the same state pick the
same next. Invariant locked: #10 (human + machine modes read the same state).