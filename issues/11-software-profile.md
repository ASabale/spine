# Software profile

Type: grilling
Status: resolved
Blocked by: 06, 09

## Question

On the same contract, what is the v1 **software profile**? Which work-item gates apply to code work (build / eval / review), what proof those gates require, and what a non-software work item skips.

Do not restore Generic Workflows’ PRD/blueprint stages on the work item — those belong on the map if they belong at all.

Recommended: software work items must pass `checking` (eval against acceptance) and `reviewing` (human or reviewer-agent verdict) before `done`. Non-software items may `doing → done` under human judgment with a named deliverable existing. Eval/review artifacts live in the execution tier.

## Answer

Software work items must pass `checking` (eval against acceptance) and `reviewing` (human or reviewer-agent verdict) before `done`. Proof artifacts live in `.spine/{evals,reviews}/`. Non-software items may `doing → done` under human judgment with a named deliverable existing. No PRD/blueprint stages on the work item.
