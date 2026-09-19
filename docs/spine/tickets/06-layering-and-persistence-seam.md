# Layering and persistence seam

Type: task
Status: resolved
Blocked by: 03-the-contract-machine.md
Owner: 
Claimed-at: 

## Question

Enforce clean layering and a persistence seam. Target dependency direction:
CLI (parsing/IO) → service (orchestration) → domain (the contract machine) → persistence (port)
→ FS/SQLite (adapters). Narrow `artifacts.py` from a god object to thin persistence; extract the
machine into the domain layer. Define the persistence port (load / save / atomic-write / list /
scan) with an FS adapter (Markdown + frontmatter) and a SQLite adapter (coordination state).
Decouple the machine from the store.

Resolved = the layers hold, the machine is store-agnostic, and `--json` is a serializer (not a
re-shaper). Invariants locked: #9, #10.

## Answer

CLI stays a parser. `src/spine/query.py` owns `next_lines` / `board` /
`status_payload` (re-exported from `artifacts` as the same function objects so
`cli.py` keeps importing those names from `artifacts`). `engine.advance` is the
mutation path. `Contract` is the domain machine.

Persistence port: `ArtifactStore` protocol; `FileStore` (Markdown + frontmatter,
atomic tmp+replace); `CoordStore` (SQLite `.spine/coord.db`, kv table only).
`engine.py` does not import `sqlite3` or `CoordStore`. Claims table is ticket 10.