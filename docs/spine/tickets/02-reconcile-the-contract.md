# Reconcile the contract

Type: task
Status: resolved
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

## Answer

Option (b): `docs/spine/contract.yaml` is the SSoT; `spec.md` and binder skills
point at it and do not restate transitions.

The 0.2.0 work-item machine already lived in that YAML (`ready → doing →
checking → reviewing → done`, bounce `changes-requested`). P0 did not invent a
second machine. It added `Contract.validate()` / `ContractError` so a malformed
spec cannot load, and tests that (1) packaged `src/spine/data/contract.yaml` is
byte-identical to the docs copy, (2) `spec.md` names every work-item status,
(3) `initcmd.README` matches `docs/spine/README.md`.

Still hardcoded, and the next ticket: the ticket machine
(`open` / `claimed` / `resolved` in `model.py`). Gates remain existence-only
until ticket 05.