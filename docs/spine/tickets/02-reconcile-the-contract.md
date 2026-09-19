# Reconcile the contract

Type: task
Status: open
Blocked by: 
Owner: 
Claimed-at: 

## Question

What exactly does spine promise? Produce one authoritative behavioral contract — a single
spec that spec, README, CLI help, implementation, and tests all agree with — and drop every
claim the code does not enforce (harness adapters, multi-target, "full" state coverage).
Make `contract.yaml` the single source the machine runs from.

Options: (a) one Markdown spec with `contract.yaml` as its executable form; (b) `contract.yaml`
as the SSoT with prose derived from it. Constraints: stay harness-agnostic and Git-friendly.
Resolved = docs/help/code/tests reconcile to one contract, and a test asserts the docs and the
machine agree. Unblocks the whole route.