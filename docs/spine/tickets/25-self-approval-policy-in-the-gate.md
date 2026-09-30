# Self-approval policy in the gate

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

`require_review` checks that `by` is non-empty. It does not compare `by` to the work item `Owner`. Reviews are YAML under `.spine/reviews/`, not work-item frontmatter.

Add `self_approval: false` under `profiles.software` in both `docs/spine/contract.yaml` and `src/spine/data/contract.yaml`. Do not add the key under `default`.

On `reviewing` → `done`, when the profile is `software` and `self_approval` is false and review `by` equals the work item `Owner`, raise `ReviewInvalid` (exit 5) and do not write. A non-software profile may have `by == Owner`. Do not record `self: true` in this ticket.

Resolved = software self-approval is rejected; non-software self-approval still reaches done.

- [x] Both contract files set `profiles.software.self_approval: false`
- [x] Software `by == Owner` raises `ReviewInvalid` and leaves status at `reviewing`
- [x] Software `by` different from `Owner` still reaches `done` (with `SPINE_HUMAN=1` if ticket 20 has landed)
- [x] Non-software `by == Owner` is allowed
- [x] `uv run pytest` passes