# spine artifacts

Sit-down in this directory:

```
spine prime
```

Humans can run `spine doctor` then `spine next` / `spine status`. The `## Next` block is the next command. CLI owns status, owner, claim, links, numbers. Agents own content.

Checked-in **spec tier** (this tree):

- `maps/` — planning maps (index only)
- `tickets/` — map tickets (`NN-slug.md`)
- `work-items/` — execution work items
- `decisions/` — durable decisions
- `wires.yaml` — binder concern → skills.sh craft skills
- `contract.yaml` — statuses and transitions (do not restate in skills)

Gitignored **execution tier** lives in `.spine/` (`evals`, `reviews`, `handoffs`, `doctor`, `claims`, `events.jsonl`, `coord.db`, `migrate`).

Craft: `spine wire --install` (skills.sh). Bodies are not vendored here.
