# Map

## Destination

Spine is a production-grade, Git-friendly orchestration engine. Multiple humans and agent
fleets coordinate a large body of work through one file-backed spine: real,
machine-verifiable gates (eval + review), atomic one-winner claims, crash recovery,
revision-bound evidence, a deterministic `next`, and full CI/release — with no hosted
service. State lives in Git; runtime coordination is a local SQLite DB under `.spine/`.

## Notes

Two inputs, one destination.

- Report A (architecture review, 2026-09-19): the code is 6.5/10 (B−). The state machine is
  hardcoded and duplicated across four sites, `artifacts.py` is a god object, gates are
  existence-only, and `doctor`/`next` are shallow. Core fix: centralize the machine, make
  gates real, enforce the layers.
- Report B (production-grade engineering brief): a 36-section brief — the 10 invariants,
  gates, concurrency, crash recovery, deterministic next, CI/release/security/migration.
- Scope decision (2026-09-19, Akshay): **full orchestration**. Adopt the brief end-to-end;
  the target is fleet-capable (overrides the earlier person-zero framing).
- Acceptance = the 10 invariants (B§34) as an automated invariant suite, gated per phase.
- This effort carries execution: resolving a phase ticket dispatches that build to the
  builder (local Qwen, `--verify "uv run pytest"`), then a reviewer pass.

Route (7 phases, P0 cheapest-first): P0 reconcile contract → P1 deep core + real gates →
P2 layering + persistence seam → P3 reliability + evidence → P4 concurrency + scale →
P5 product (CI/release/security/migration) → P6 dogfood spine on spine.

## Decisions so far

- Scope = full orchestration (2026-09-19): adopt the production brief end-to-end (SQLite
  coordination, append-only event log, 50-worker concurrency, 100k benchmarks, full
  CI/release/security/migration); spine's target becomes fleet-capable.
- Architecture rating (2026-09-19): 6.5/10 (B−); the load-bearing fixes are centralizing the
  state machine and making eval/review real machine-verifiable gates.
- P0 contract SSoT (2026-09-19): option (b). Work-item statuses/transitions live
  in `contract.yaml` (`ready`, `doing`, `checking`, `reviewing`, `done`,
  `changes-requested`). `Contract.validate()` rejects drift/malformed YAML.
  Packaged data file must stay byte-identical to the docs copy. Ticket machine
  still hardcoded until ticket 03.
- P1 contract machine (2026-09-19): tickets live under `contract.yaml` `tickets:`;
  `Contract.ticket_allowed` is the only ticket transition table.
- P1 transition engine (2026-09-19): `engine.advance` is the only status mutation;
  typed SpineError exit codes 0–8. Event log / claim-held / HITL-in-advance deferred.
- P1 real gates (2026-09-19): eval/review are YAML mappings (`passed`/`verdict` +
  command/when/revision/evidence). Existence-only `_has_proof` is no longer the
  checking→reviewing / reviewing→done gate. Revision binding is 07.
- P2 layering (2026-09-19): `query.py` owns next/board/status_payload;
  `FileStore` + `CoordStore` (kv only) are the persistence seam. `engine.py`
  stays store-agnostic. Claims table is ticket 10.
- P3 event log + revision binding (2026-09-19): `.spine/events.jsonl` is
  append-only JSONL from `advance`; `content_revision` hashes the work-item
  body; eval/review must match each other and that digest.
- P3 doctor recovery (2026-09-19): `doctor` repairs unknown/illegal status,
  event-log drift, stale claims, dangling links, and resolved/missing
  `Blocked by` (path or filename). FIX lines include why. CLI exit 8 when
  unrepaired.
- P3 next + run (2026-09-19): inflight order is `contract.next.inflight`.
  `run` is a list of `{cmd, hitl}` mappings; HITL-only states have `run=[]`.
  `spine run` prints the first command. Same state → same next.
- P4 claims (2026-09-19): SQLite `claims` table, `BEGIN IMMEDIATE` one-winner,
  owner-or-stale release. Frontmatter remains the Git copy. `engine.py` has no
  sqlite. 50-worker harness is ticket 11.
- P4 scale (2026-09-19): atomic IDs, spec-root path boundary, 50-worker
  harness, 100k next < 500ms and claim < 100ms.
- P5 release (2026-09-19): `make release` is the gated path. `spine migrate`
  dry-run/apply/rollback. CI runs the gate. Path/symlink boundary + no shell=True.
- P6 dogfood (2026-09-19): full route with crash recovery and a second
  worker. Example: docs/spine/examples/dogfood.md. Test: tests/test_dogfood.py.
- Review (2026-09-20): two-axis pass since `6b48b03`. Spec of the code holds;
  docs lagged. Remaining deepenings (Claim as one module, doctor through
  engine, one board scan) are **not** this effort — see ticket 14.

## Not yet specified

Route complete (P0–P6 resolved). Fog that sharpened: claims table, YAML
eval/review, stale-hours lease, `spine migrate`, ticket table in
`contract.yaml`. Nothing left on this map.

## Out of scope

Hosted orchestration service; multi-repo / cross-machine coordination; auth/SSO; changes to
the already-shipped 0.1.0/0.2.0 history.