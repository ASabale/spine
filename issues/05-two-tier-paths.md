# Two-tier paths

Type: grilling
Status: resolved

## Question

Exact directory and filename conventions in a target for **spec tier** (checked in) vs **execution tier** (gitignored).

Spec tier must have a home for maps, tickets, work items, and decisions. Execution tier for claims runtime, evals, reviews, handoffs, doctor output. Init writes `.gitignore` for the execution tier.

Recommended: spec `docs/spine/{maps,tickets,work-items,decisions}/`; execution `.spine/{evals,reviews,handoffs,doctor}/`. Do not reuse Generic Workflows’ `docs/workflow/` + `.workflow/` names (wrong product name, easy to mix with a leftover install).

## Answer

Spec tier (checked in): `docs/spine/{maps,tickets,work-items,decisions}/`.

Execution tier (gitignored): `.spine/{evals,reviews,handoffs,doctor,claims}/`. Init writes `.gitignore` for `.spine/`.

A short `docs/spine/README.md` names that tree so a first-time agent can read folder names without the spec. Do not reuse `docs/workflow/` or `.workflow/`.
