# Dogfood spine on spine

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

Prove it end-to-end by running the productionized spine on itself. One complete example: a piece
of real spine work driven through the full route — claim → doing → checking (real eval) →
reviewing (real review) → done — with a simulated crash/recovery and a concurrent second worker,
captured as the canonical example in the docs. This is the acceptance proof of the whole effort
(B§23: the first dogfood target is spine's own repo).

Resolved = the e2e example runs green and is the documented proof.

## Answer

This repo is a spine target. The canonical e2e is
`docs/spine/examples/dogfood.md`, automated by `tests/test_dogfood.py`:
claim → doing → checking, crash (frontmatter reset, doctor restores from the
event log), a second worker gets `ClaimConflict`, real eval + review bound to
`content_revision`, then `done`.