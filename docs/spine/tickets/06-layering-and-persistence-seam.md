# Layering and persistence seam

Type: task
Status: open
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