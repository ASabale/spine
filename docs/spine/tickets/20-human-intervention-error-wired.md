# Human-intervention error wired

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

`HumanInterventionRequired` (exit 6) is never raised. There is no agent type and no roles model. The only human signal is the environment variable `SPINE_HUMAN=1`. Agents must not set it. Do not add a new contract concept.

Check the variable in exactly two places: `new_work_item`, and `advance` on `reviewing` → `done`. If it is missing or not `1`, raise `HumanInterventionRequired` and do not write. If it is `1`, proceed, and that event includes `"human": true`.

Ticket transitions do not check the variable. `spine run` stays an empty `run` list for states that are already HITL-only. Do not change that.

The suite mints work items in many tests. Add `tests/conftest.py` with an autouse fixture that sets `SPINE_HUMAN=1`. Add one test that unsets it and expects exit 6 from the CLI and `HumanInterventionRequired` from `new_work_item` and from `reviewing` → `done`.

Resolved = those two writes require `SPINE_HUMAN=1`, and the done event records `human: true`.

- [x] `new_work_item` without `SPINE_HUMAN=1` raises `HumanInterventionRequired` and writes no file
- [x] `spine new work-item` without it exits 6
- [x] `reviewing` → `done` without it raises `HumanInterventionRequired` and does not change status
- [x] With `SPINE_HUMAN=1`, that done event contains `"human": true`
- [x] Ticket `set-status` does not require the variable
- [x] `uv run pytest` passes