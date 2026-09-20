# spine — v1 spec

Public, harness-agnostic process spine. Planning and execution survive sessions as files in a **target**. This spec plus [CONTEXT.md](CONTEXT.md) is enough to implement the toolkit. It does not implement it.

License: **MIT**. Product, GitHub slug, docs, and CLI command: **spine**. PyPI distribution: **spine-cli**. GitHub home: https://github.com/ASabale/spine. Do not publish as Generic Workflows.

## Job

Durable process across sessions: a **map** plus **tickets** for planning; a **work item** for execution (status, owner, claim, links, next gate). Repo files in the target are the source of truth. No harness API is required for correctness. Optional adapters later; never required.

The 0.2.0 tree is fleet-capable: one-winner claims, machine-verifiable eval/review gates, doctor recovery, structured `run`, and `spine migrate`. `docs/spine/contract.yaml` is the single source of truth for statuses and transitions.

## Stranger install

Python **3.11+**. Console script `spine` via `[project.scripts]`. Wheel ships the **contract** and binder `SKILL.md` as package data (`importlib.resources`). Init copies skills onto harness discovery roots; a wheel copy is invisible until then.

```text
uvx --from spine-cli spine init
```

or `uv tool install spine-cli` then `spine init`. Idempotent: missing artifacts only; refresh offered. Then `spine doctor` once. No plugin marketplace. No clone of the spine source repo. GitHub home is documentation, not an install dependency.

Dev gate: `make test`. Ship gate: `make release`.

## Two-tier paths

**Spec tier** (checked in):

```text
docs/spine/README.md
docs/spine/maps/
docs/spine/tickets/
docs/spine/work-items/
docs/spine/decisions/
docs/spine/contract.yaml
docs/spine/wires.yaml
```

**Execution tier** (gitignored; init writes `.gitignore` for `.spine/`):

```text
.spine/evals/
.spine/reviews/
.spine/handoffs/
.spine/doctor/
.spine/claims/
.spine/events.jsonl
.spine/coord.db
.spine/migrate/
```

Do not use `docs/workflow/` or `.workflow/`. Folder names match the glossary. `docs/spine/README.md` names the tree for a first-time agent. Packaged `src/spine/data/contract.yaml` must stay byte-identical to `docs/spine/contract.yaml`.

## Planning (Wayfinder as files)

No GitHub Issues required. One map file per map. Sections: Destination, Notes, Decisions so far, Not yet specified (fog), Out of scope. The map is an **index**: gist plus link; it does not restate a ticket’s answer.

Child tickets: `NN-<slug>.md`, title is the name. Fields: `Type:` (research, prototype, grilling, task), `Status:` (open, claimed, resolved), `Blocked by: NN`. Answers under `## Answer`. Research write-ups are separate files, linked, not pasted. Frontier: open, unblocked, unclaimed tickets. Claim on tickets is a field the **CLI** owns.

Planning never lives on the work item. Chart the map, cut tickets, work the frontier. When the way is clear, HITL **creates** a work item at `ready`.

## Work-item machine (contract)

Happy path: `ready → doing → checking → reviewing → done`.

Bounce: `reviewing → changes-requested → doing`.

Legal transitions:

- `ready → doing`
- `doing → checking`
- `checking → reviewing`
- `reviewing → done`
- `reviewing → changes-requested`
- `changes-requested → doing`

HITL: creating a work item; `reviewing`. Agent-drivable: `doing`, `checking`. No `grilling` / `prd` / `planning` status on a work item. Next session reads the current status as the next gate.

Tickets: `open → claimed → resolved` (also `open → resolved`). Both machines live in `contract.yaml`. Skills and the CLI **reference** this contract; they never restate it.

Every `set-status` goes through `engine.advance`. Same-status is a no-op. Typed CLI exits: 0 ok, 1 general, 2 usage, 3 illegal transition, 4 claim conflict, 5 validation, 6 HITL, 7 external, 8 inconsistent.

## Software profile

Same contract. Software work items must pass `checking` (eval against acceptance) and `reviewing` (human or reviewer-agent verdict) before `done`. Proof artifacts live in `.spine/{evals,reviews}/` as YAML mappings, not file existence:

- eval: `passed: true` (bool), `command`, `when`, `revision`
- review: `verdict` in `{approve, request-changes, block}`, plus `by`, `when`, `revision`, `evidence`

`checking → reviewing` requires a passing eval whose `revision` equals the work-item **body** hash. `reviewing → done` requires eval, an `approve` review, and the same hash. Status/Owner changes do not invalidate proofs. Non-software items may `doing → done` under human judgment with a named deliverable existing. No PRD/blueprint stages on the work item.

## CLI

Humans and agents use the same CLI. It is the only writer of machine-driving metadata (status, owner, claim, links, numbers).

Verbs: `init`, `status`, `next`, `run`, `prime`, `new`, `claim`, `show`, `release`, `set-status`, `link`, `doctor`, `wire`, `evolve`, `migrate`.

- `init` — scaffold a target, then print the board.
- `status` — board plus `## Next` (the next command). `--json` for agents (`next`, `run`, tickets, frontier).
- `next` — print only the next command lines. `--json` exposes `run`, `hitl`, `user`, `version`. Sit-down: `spine prime`. Bare `spine` prints the board. Inflight order comes from `contract.next.inflight`.
- `new` — mint a work item and/or a map ticket (flags, not a second verb). Prints `## Next` after mint. `--json` prints the payload instead.
- `claim` / `release` — one-winner lock. `spine claim` with no target claims the artifact named by `spine next`. A second claimant gets exit 4. Release is owner-only unless the lease is stale or doctor passes force. Both print `## Next` after success. `--json` prints the payload instead of `## Next`.
- `show` — print one ticket or work item by stem or path. `--json` emits `{file, meta, body}`.
- `run` — print the first executable `spine …` command from next. `status --json` `run` is a list of `{cmd, hitl}` mappings, not filtered prose. HITL-only states have `run == []`. Exit 2 when `run` is empty (HITL).
- `set-status` — legal work-item transitions; tickets: `open|claimed|resolved`. Prints `## Next`; `--json` prints the payload.
- `link` — CLI-owned bidirectional links. Prints `## Next` after success. `--json` prints the payload.
- `doctor` — recovery loop, then `## Next`. Non-target: report `spine init`. `--json` / `prime` include `messages`, `ok` (true when only `ok`/`FIX` lines remain), `cwd`, `next`, `run`, `hitl`, `version`. Exit 8 when unrepaired. `--report-only` does not mutate.
- `migrate` — upgrade target `contract.yaml` and coord schema. `--dry-run` plans; apply backs up then writes; `--rollback` restores. Exit 8 on REPORT.

No harness-specific subcommands. No plugin install. Resolve stays inside `docs/spine` (symlink-safe). Subprocess calls are argv lists, never `shell=True`.

## Claim policy

One-winner lock on a ticket or work item. `Owner` + `Claimed-at` (Git-visible copy) owned by the CLI. Runtime lock is local coordination state under `.spine/`. Stale after **4 hours**. `spine claim` fails if a non-stale claim exists. `spine release` is owner-only unless stale; doctor force-releases stale claims. No auth system. Username is `user.name` or `SPINE_USER`. A second agent or human loses; they do not rewrite the artifact to take it.

## Doctor

CLI command, not a harness hook. Wake-up recovery loop: scan every ticket and work item; repair what it can; print before → after (why).

**Auto-fix:** unknown/illegal status → `ready` (work item) or `open` (ticket); frontmatter Status vs last `.spine/events.jsonl` `to` → restore the logged status; stale claims past the policy window; broken bidirectional links the CLI owns; rollups (`Blocked by` missing or already resolved).

**Report-only (unrepairable):** missing spec-tier files; gitignore drift; contract version skew vs packaged.

Never auto-edit content sections. Harness session-start is adapter fog, not required v1.

## Binder

v1 concerns (thin `SKILL.md` each): `new` (capture), `wayfind`, `next` (frontier + work-item board), `doctor`, plus software pointers `build`, `eval`, `review`. Do not vendor grilling, TDD, or Wayfinder bodies. Drop graph, tour, and a `dev-*` palette.

Shape: YAML frontmatter + short body — when to use, CLI invocations by pointer, `## Gate` names that exist in the contract (not copied statuses). One skill text. Init writes copies onto harness roots (at least `.agents/skills` for Cursor/Codex/oh-my-pi; `.claude/skills` for Claude Code). No Devin `hooks.v1.json`.

Eval/review binder skills write YAML mappings (`passed` / `verdict` + revision), not “file exists.”

## Out of scope (v1)

- Harness plugins or hooks as required.
- Code graph (CRG / Graphify).
- Shipping a full craft-skill catalog.
- Importing a 16-status idea→done machine.
- Hosted orchestration; multi-repo / cross-machine coordination.

## Deferred (not decided here)

- Optional per-harness adapters.
- A docs-only type profile besides software.
- How already-wayfinding folders relate to a spine-inited target.
- Whether init scaffolds CONTEXT.md / ADR conventions.
- Work-item templates (PRD, blueprint).
- User-level vs project-level install besides `uvx` + init.
- Publish/tag beyond the already-shipped 0.2.0.
- Funneling claim/release/doctor repairs through `advance`; HITL as a hard gate inside `advance` (ticket 04 deferred).

## Auto-evolve, recover, and skill wires (v1 addendum)

Operator instruction 2026-09-18: the toolkit is auto-evolvable, self-recoverable, harness/agent/platform-agnostic. Craft skills are **not** vendored. Discover them on **skills.sh**. Install and update via the open skills CLI (`npx skills …`). Default recommended pack: **mattpocock/skills**. Users may wire any pack.

**Wires file** (spec tier): `docs/spine/wires.yaml` maps binder concerns to skills.sh slugs (`owner/repo` + skill name). Init writes a default mapping to Matt Pocock skills; `spine wire` edits it; `spine evolve` refreshes binder copies from the wheel and runs `npx skills update` when the CLI is available.

Default wires (concern → skills.sh skills, not vendored bodies):

- `wayfind` → `mattpocock/skills` `wayfinder`, `grilling`, `domain-modeling`
- `new` → `mattpocock/skills` `grill-me` (and map capture via `wayfinder`)
- `next` → `mattpocock/skills` `ask-matt`, `implement`
- `doctor` → binder `doctor` plus `spine doctor`
- `build` → `mattpocock/skills` `implement`, `tdd`, `codebase-design`
- `eval` → `mattpocock/skills` `qa`
- `review` → `mattpocock/skills` `code-review`

**Self-recover:** `spine doctor` is the recovery loop. `spine evolve` is the refresh loop. `spine migrate` upgrades contract + coord schema. Init stays idempotent.

**Extra CLI verbs (addendum):** `wire`, `evolve`, `migrate`. Same CLI owns metadata; `npx skills` owns craft-skill files on harness roots.
