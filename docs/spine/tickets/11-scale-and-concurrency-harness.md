# Scale and concurrency harness

Type: task
Status: open
Blocked by: 10-atomic-claims-and-concurrency-model.md
Owner: 
Claimed-at: 

## Question

Prove it scales. Build a concurrency harness (50 simulated workers claim / advance / release;
assert no lost claims, no lost transitions, no corruption) and a 100k-item benchmark (target:
`next` < 500ms, claim < 100ms). Add a stable-ID + path-boundary scheme so artifacts don't
re-number under load.

Resolved = the harness + benchmark pass and gate the release. Invariants locked: #2, #5.