# Evidence, event log and revision binding

Type: task
Status: resolved
Blocked by: 
Owner: 
Claimed-at: 

## Question

Add an append-only, Git-friendly event log (one line per transition: actor, time, from, to,
revision, run_id) plus atomic, idempotent writes (temp file + rename + fsync). Introduce
revision binding: evidence (eval/review) is tied to a content hash/revision, and changed content
invalidates stale proofs. Keep it Git-friendly (the log is append-only text; the SQLite DB is
`.spine/` runtime state).

Resolved = a crash mid-mutation is recoverable and auditable, and stale evidence can't authorize
changed work. Invariants locked: #6, #7.

## Answer

`.spine/events.jsonl` is append-only: one JSON object per real `advance` (actor, time,
from, to, revision, run_id, spec). Idempotent no-ops do not write a line. The writer
flushes and `fsync`s. `FileStore.atomic_write` is tmp+replace+fsync.

`content_revision(path)` is sha256 of the Markdown body after frontmatter, so Status
metadata changes do not invalidate proofs. `checking → reviewing` requires
`eval.revision == digest`. `reviewing → done` requires eval revision, review revision,
and digest to be identical. Changing the work-item body invalidates stale gates
(`EvaluationInvalid` / `ReviewInvalid`, CLI 5).