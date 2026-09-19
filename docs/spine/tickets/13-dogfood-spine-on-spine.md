# Dogfood spine on spine

Type: task
Status: open
Blocked by: 12-release-ci-security-and-migration.md
Owner: 
Claimed-at: 

## Question

Prove it end-to-end by running the productionized spine on itself. One complete example: a piece
of real spine work driven through the full route — claim → doing → checking (real eval) →
reviewing (real review) → done — with a simulated crash/recovery and a concurrent second worker,
captured as the canonical example in the docs. This is the acceptance proof of the whole effort
(B§23: the first dogfood target is spine's own repo).

Resolved = the e2e example runs green and is the documented proof.