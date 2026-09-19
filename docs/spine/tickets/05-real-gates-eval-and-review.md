# Real gates: eval and review

Type: task
Status: open
Blocked by: 03-the-contract-machine.md
Owner: 
Claimed-at: 

## Question

Make checking→reviewing (eval) and reviewing→done (review) real machine-verifiable gates, not
"does a file exist?" Define the structured format + schema for each:
- eval: the test commands actually run, pass/fail, which revision, when.
- review: verdict (approve / request-changes / block), evidence, which revision, by whom, when.

Decide validation (a passing gate requires real passing results; a stale or missing one blocks)
and the content rules. Resolved = the machine checks the proof's content and freshness, not its
existence. Invariant locked: #1 (done ⇒ valid passing eval + approving review on the same
revision).