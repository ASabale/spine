# The contract machine

Type: task
Status: resolved
Blocked by: 02-reconcile-the-contract.md
Owner: 
Claimed-at: 

## Question

Design the single deep `Contract` module that owns the entire lifecycle as data — statuses,
transitions, gates, proof requirements, next-commands, and the inflight set — with one
interface (`validate`, `allowed`/`advance`, `next_for`, `is_stale`) that hides the YAML. Fold
the hardcoded ticket machine (`TICKET_STATUSES`/`TICKET_TRANSITIONS` in `model.py`, plus
`doctor`, `claim`, `release`) into the same contract. Decide the interface and the seam
(contract = data, machine = behavior).

This is the core deepening (Report A: "run the work-item machine from the contract" [Strong]).
Resolved = one module; `artifacts.py`, `doctor`, `next`, `set-status`, and `claim` all consult
it and no second machine survives. Invariants locked: #1 (done ⇒ gates), #3 (legal transitions).

## Answer

One `Contract` in `src/spine/model.py` owns both machines as data from
`contract.yaml` (`statuses`/`transitions` for work items; `tickets.statuses`/
`tickets.transitions` for map tickets). Interface on this ticket: `validate`,
`allowed`, `ticket_allowed`. `set-status`, `doctor`, and load paths consult it;
`TICKET_STATUSES`/`TICKET_TRANSITIONS` are gone.

Deferred to later tickets (not a second hardcoded table): `advance` + typed
errors (04), real eval/review proof (05), `next_for` / inflight as data (09),
`is_stale` stays a thin helper over `claim.stale_hours`.