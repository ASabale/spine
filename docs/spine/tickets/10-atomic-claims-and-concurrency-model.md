# Atomic claims and concurrency model

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

Make claims safe under concurrency. Decide the substrate: a SQLite coordination DB under
`.spine/` (atomic one-winner claim, ownership-aware release, lease/renewal or a simple
stale-timeout) vs pure-FS primitives (atomic create / lock / CAS). Define the claim lifecycle
(claim → work → release/complete, with ownership) and release semantics (only the owner, or an
expired lease, can release). Design for 50 agents contending.

Resolved = no two workers ever hold the same claim, and release is ownership-aware. Invariants
locked: #2 (no simultaneous claims), #4 (no mutation escapes the target root).

## Answer

Substrate is SQLite `.spine/coord.db`, table `claims(spec PRIMARY KEY, owner, claimed_at)`.
`take_claim` uses `BEGIN IMMEDIATE` so one INSERT wins; losers get `ClaimConflict` (CLI 4).
Release is owner-only, or an expired lease (`claim.stale_hours`), or doctor `force=True`.
Frontmatter Owner/Claimed-at stays the Git-visible copy. `engine.py` stays sqlite-free.
Lease is the existing stale-timeout, not a separate renew command.
