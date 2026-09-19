# spine artifacts

Checked-in **spec tier** (this tree):

- `maps/` — planning maps (index only)
- `tickets/` — map tickets (`NN-slug.md`)
- `work-items/` — execution work items
- `decisions/` — durable decisions
- `wires.yaml` — binder concern → skills.sh craft skills

Gitignored **execution tier** lives in `.spine/` (`evals`, `reviews`, `handoffs`, `doctor`, `claims`).

Install craft skills with the open skills CLI (skills.sh), not by copying bodies into this repo:

```
npx skills add mattpocock/skills -y
```

Or `spine wire --install` to install the default wires.
