# Review the productionize diff

Type: task
Status: resolved
Owner: ASabale
Claimed-at: 2026-09-20T00:44:09.307624+00:00
Blocked by: 

## Question

AFK two-axis review (standards + spec) of the productionize work since
`b1f1da8` (or `77b61c4` if that is the cleaner fixed point). Spec is
`docs/spine/maps/productionize.md` plus tickets 09–13.

Report findings. Do not edit. Unblocks [Align spec.md with the 0.2.0 tree](15-align-spec-md-with-the-0-2-0-tree.md).

## Answer

Fixed point used: `6b48b03` (productionize chart) … `0fd491a` (docs=code map).
That is the full productionize implementation, not only 09–13. Diff: 64 files,
+2999/−376, 22 commits. Architecture HTML (not in repo):
`/var/folders/z3/gmpk7cz57qn9h1f_f15p3kq00000gn/T/architecture-review-1789865220.html`.

The AFK reviewer child failed after the survey (local Qwen). Parent completed
both axes from the tree plus the architecture scan.

### Standards

Hard (documented):

- **spec.md / AGENTS.md / productionize fog still describe the pre-productionize
  product** while the diff shipped migrate, SQLite claims, real YAML gates, and
  structured `run`. spec.md still says “solo-first lock”, omits `migrate` from
  the main verb list, and lists “Contract versioning and artifact migration”
  as deferred. That is ticket 15, not a code defect. Same drift in
  `docs/spine/README.md` / `initcmd.README` (execution tier names evals/reviews
  but not `coord.db` or `events.jsonl`) and binder `eval`/`review` skills
  (“file exists” vs YAML mappings).
- **`_has_proof` is leftover** in `artifacts.py` after gates moved to
  `gates.py`. Dead path next to the real gate.

Judgement (Fowler baseline; repo YAML-SSoT / sqlite-free engine override):

- **Divergent change — `artifacts.py`**: mint, resolve, claim/release, link,
  identity, FileStore/CoordStore, and query re-exports still share one file
  after ticket 06 split query/store out. Feature Envy: claim logic reaches into
  CoordStore + frontmatter + `.claim` files.
- **Duplicated scans — `query.py`**: `next_lines`, `status_payload`, and
  `board` each walk tickets/work-items. Inflight order comes from Contract;
  command strings are a parallel `if status` ladder.
- **Shotgun / two Status writers**: `engine.advance` vs `doctor.write_meta`
  for repairs. Claim `open→claimed` also bypasses `advance` (no event).
- **Speculative generality — `ArtifactStore` Protocol**: one adapter
  (`FileStore`). `list_md` unused; query uses `os.scandir`. CoordStore is a
  different interface, not a second ArtifactStore.
- **Mysterious Name — `doctor_ok`**: success is inferred from `ok`/`FIX `/
  `REPORT ` string prefixes, not a structured result.

Not flagged (repo standard wins): YAML as SSoT; engine sqlite-free;
SQLite+frontmatter claim pair; 50-worker harness.

### Spec

Implemented as asked:

- P0–P2: `contract.yaml` SSoT + `Contract.validate`; ticket machine in YAML;
  `engine.advance` for `set-status`; typed exit codes 0–8; eval/review YAML
  mappings; `query` + `FileStore`/`CoordStore`; engine has no sqlite.
- P3: append-only `events.jsonl`; `content_revision` hashes body; doctor
  recovery + exit 8; inflight from contract; `run` is `{cmd, hitl}` mappings.
- P4: `claims` table `BEGIN IMMEDIATE` one-winner; owner-or-stale release;
  `allocate_id`; `docs/spine` path boundary; 50-worker + 100k next/claim tests.
- P5–P6: `make release`, CI, `spine migrate`, symlink/shell guards, dogfood
  e2e with crash restore + second-worker `ClaimConflict`.

Missing or partial vs ticket *questions* (Answers already deferred some):

- Ticket 04 question: every mutation through `advance`, claim held, HITL gate,
  atomic record. **Answer deferred** claim-held/HITL; event log shipped in 07.
  Still true: `claim`/`release`/`link`/`new`/`doctor` repairs bypass
  `advance`. `reason` is unused. `HumanInterventionRequired` is unused.
  `set-status` does not check the claim owner — bob can advance ada’s item.
- Ticket 04 “atomic frontmatter + event”: write_meta then append_event (fsync
  on the log only). Doctor prefers the log, so a crash after frontmatter
  reverts — conservative, not one transaction.
- Ticket 06 “narrow artifacts to thin persistence”: query/store extracted;
  artifacts remains the hub (cycle ART ⇄ query, ART → engine).
- `contract.yaml` keys `hitl`, `agent_drivable`, `gates.*`,
  `profiles.default.allow_doing_to_done`, `claim.owner_env` are unused by
  Contract/engine/identity (identity reads `SPINE_USER` directly).
- Gate locate and `_has_proof` use substring `stem in p.name` (same as 0.2.0
  lookup). `_deliverable_exists` allows an absolute path outside the target.

Not scope creep: SQLite, 50 workers, CI/release were the productionize
destination.

### Architecture (separate axis)

After productionize the 2026-09-19 6.5/10 items are done. Remaining deepenings,
ranked:

1. **Strong — Claim is three writers, two status paths** (`artifacts.claim`,
   CoordStore, `.claim` file; `advance` can set ticket `claimed` with no lock).
2. **Strong — Doctor repairs behind the engine seam** (`write_meta` Status).
3. **Strong — Next/board/payload: three scans, hardcoded steps**.
4. **Worth exploring — Contract seam is porous** (callers hardcode YAML keys).
5. **Worth exploring — artifacts is still the import barrel**.
6. **Speculative — drop ArtifactStore Protocol until a second adapter exists**.

Left alone: gates (already deep), YAML SSoT, CLI argparse, engine sqlite-free.

These are not this map’s docs=code destination. Do not graduate them onto
`map.md` tickets unless a later session names that work.

**Summary:** Standards 6 findings (worst: spec/README/binder drift vs the
shipped machine). Spec 5 partials (worst: claim-held / HITL / every-mutation
still deferred; `set-status` ignores owner). Architecture top: deepen Claim.