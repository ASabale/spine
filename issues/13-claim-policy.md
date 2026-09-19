# Claim policy

Type: grilling
Status: resolved
Blocked by: 06

## Question

Solo-first, claim-ready: exact claim fields, who may claim, stale-release window, what happens when a second agent starts work on a claimed work item.

Recommended: `Owner` + `Claimed-at` owned by the CLI; stale after **4 hours** (Generic Workflows’ number; good enough); `spine claim` fails if a non-stale claim exists; `spine release` and stale doctor-fix clear it. No auth system. Username is a string the operator sets (`user.name` or `SPINE_USER`).

## Answer

`Owner` + `Claimed-at` owned by the CLI. Stale after **4 hours**. `spine claim` fails if a non-stale claim exists. `spine release` and stale doctor-fix clear it. No auth system. Username is `user.name` or `SPINE_USER`.
