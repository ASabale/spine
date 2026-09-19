# Deterministic next and structured run

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

Make `next` deterministic and prioritized (a stable, documented ordering over active work items
and tickets; same state → same next) and make `run` a structured, machine-readable plan (ordered
commands + HITL gates), not prose lines. The `next` rules should come from the contract, not
hardcoded lists.

Resolved = an agent can consume `run` as JSON and act, and two agents on the same state pick the
same next. Invariant locked: #10 (human + machine modes read the same state).

## Answer

`next` order is `contract.next.inflight` (reviewing, checking, doing,
changes-requested), then claimed tickets, then open tickets, then ready work
items. Same files → same next (sorted glob + that list).

`status_payload()["run"]` is a list of `{cmd, hitl}` mappings, not filtered
prose. HITL-only states (empty map, mint with `...`) have `run == []` and
`hitl is True`. `spine run` prints the first `cmd` or exits 2. Humans read
`next` lines; agents read `run` from the same payload (invariant #10).
