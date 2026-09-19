# Short execution machine

Type: grilling
Status: resolved

## Question

Design the work-item **contract** from scratch: statuses, legal transitions, which are HITL vs agent-drivable, bounce paths. Few statuses. Next session must see the next gate.

Do **not** import Generic Workflows’ 16-status idea→done list. Planning (map/tickets) is a separate artifact — do not put `grilling` / `prd` / `planning` on the work item.

Recommended starting set: `ready → doing → checking → reviewing → done`, with `changes-requested → doing`. HITL: `reviewing` (and creating a work item). Agent-drivable: `doing`, `checking`. Exact names can move; the shape should stay this small.

## Answer

Happy path: `ready → doing → checking → reviewing → done`.

Bounce: `reviewing → changes-requested → doing`.

Legal transitions:

- `ready → doing`
- `doing → checking`
- `checking → reviewing`
- `reviewing → done`
- `reviewing → changes-requested`
- `changes-requested → doing`

HITL: creating a work item; `reviewing` (human or named reviewer-agent verdict — software profile names proof). Agent-drivable: `doing`, `checking`.

No `grilling` / `prd` / `planning` on the work item. Next session reads the current status as the next gate. Software-profile eval/review proof stays on [Software profile](11-software-profile.md). Claim fields stay on [Claim policy](13-claim-policy.md).
