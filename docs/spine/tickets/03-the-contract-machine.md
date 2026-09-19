# The contract machine

Type: task
Status: open
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