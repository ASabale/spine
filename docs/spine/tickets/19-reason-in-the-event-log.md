# reason lands in the event log

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

`advance` accepts `reason` and `append_event` drops it. The line today is `actor`, `time`, `from`, `to`, `revision`, `run_id`, `spec`.

Add `reason: str = ""` and `op: str = "status"` to `append_event`. `advance` passes its `reason` through and leaves `op` as `status`. Do not add `engine.record` in this ticket.

A jsonl line with no `reason` and no `op` still parses: missing `op` means `status`, missing `reason` means `""`.

`spine show` prints `reason: <text>` from the latest event for that artifact. An empty reason prints `reason:`.

Resolved = a status change stores the reason, old lines still parse, and show prints the last reason.

- [x] Status change with reason `because` stores `"reason":"because"` and `"op":"status"`
- [x] A line without those keys still loads
- [x] `spine show` prints the last reason
- [x] `uv run pytest` passes