# Evidence, event log and revision binding

Type: task
Status: open
Blocked by: 06-layering-and-persistence-seam.md
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