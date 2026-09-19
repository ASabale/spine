# spine — v1 spec

Public, harness-agnostic process spine. Planning and execution survive sessions as files in a **target**. This spec plus [CONTEXT.md](CONTEXT.md) is enough to implement the toolkit. It does not implement it.

License: **MIT**. Product, GitHub slug, docs, and CLI command: **spine**. PyPI distribution: **spine-cli**. Intended GitHub home: https://github.com/ASabale/spine (not created by this spec). Do not publish as Generic Workflows.

## Job

Durable process across sessions: a **map** plus **tickets** for planning; a **work item** for execution (status, owner, claim, links, next gate). Repo files in the target are the source of truth. No harness API is required for correctness. Optional adapters later; never required.

## Stranger install

Python **3.11+**. Console script `spine` via `[project.scripts]`. Wheel ships the **contract** and binder `SKILL.md` as package data (`importlib.resources`). Init copies skills onto harness discovery roots; a wheel copy is invisible until then.

```text
uvx --from spine-cli spine init
```

or `uv tool install spine-cli` then `spine init`. Idempotent: missing artifacts only; refresh offered. Then `spine doctor` once. No plugin marketplace. No clone of the spine source repo. GitHub home is documentation, not an install dependency.

## Two-tier paths

**Spec tier** (checked in):

```text
docs/spine/README.md
docs/spine/maps/
docs/spine/tickets/
docs/spine/work-items/
docs/spine/decisions/
```

**Execution tier** (gitignored; init writes `.gitignore` for `.spine/`):

```text
.spine/evals/
.spine/reviews/
.spine/handoffs/
.spine/doctor/
.spine/claims/
```

Do not use `docs/workflow/` or `.workflow/`. Folder names match the glossary. `docs/spine/README.md` names the tree for a first-time agent.

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

Skills and the CLI **reference** this contract; they never restate it.

## Software profile

Same contract. Software work items must pass `checking` (eval against acceptance) and `reviewing` (human or reviewer-agent verdict) before `done`. Proof artifacts live in `.spine/{evals,reviews}/`. Non-software items may `doing → done` under human judgment with a named deliverable existing. No PRD/blueprint stages on the work item.

## CLI

Humans and agents use the same CLI. It is the only writer of machine-driving metadata (status, owner, claim, links, numbers).

Verbs: `init`, `status`, `new`, `claim`, `release`, `set-status`, `link`, `doctor`.

- `init` — scaffold a target.
- `status` — board (work items + next gate).
- `new` — mint a work item and/or a map ticket (flags, not a second verb).
- `claim` / `release` — solo-first lock.
- `set-status` — only legal transitions.
- `link` — CLI-owned bidirectional links.
- `doctor` — mechanical drift.

No harness-specific subcommands. No plugin install.

## Claim policy

`Owner` + `Claimed-at` owned by the CLI. Stale after **4 hours**. `spine claim` fails if a non-stale claim exists. `spine release` and stale doctor-fix clear it. No auth system. Username is `user.name` or `SPINE_USER`.

## Doctor

CLI command, not a harness hook.

**Auto-fix:** stale claims past the policy window; broken bidirectional links the CLI owns; rollups the CLI owns.

**Report-only:** unknown statuses after a contract bump; missing spec-tier files; gitignore drift.

Never auto-edit content sections. Harness session-start is adapter fog, not required v1.

## Binder

v1 concerns (thin `SKILL.md` each): `new` (capture), `wayfind`, `next` (frontier + work-item board), `doctor`, plus software pointers `build`, `eval`, `review`. Do not vendor grilling, TDD, or Wayfinder bodies. Drop graph, tour, and a `dev-*` palette.

Shape: YAML frontmatter + short body — when to use, CLI invocations by pointer, `## Gate` names that exist in the contract (not copied statuses). One skill text. Init writes copies onto harness roots (at least `.agents/skills` for Cursor/Codex/oh-my-pi; `.claude/skills` for Claude Code). No Devin `hooks.v1.json`.

## Out of scope (v1)

- Harness plugins or hooks as required.
- Code graph (CRG / Graphify).
- Shipping a full craft-skill catalog.
- Importing a 16-status idea→done machine.
- Creating the GitHub repository as part of implementing this spec (home is named; create is a later act).

## Deferred (not decided here)

- Contract versioning and artifact migration.
- Optional per-harness adapters.
- A docs-only type profile besides software.
- How already-wayfinding folders relate to a spine-inited target.
- Whether init scaffolds CONTEXT.md / ADR conventions.
- Work-item templates (PRD, blueprint).
- User-level vs project-level install besides `uvx` + init.

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

**Self-recover:** `spine doctor` is the recovery loop. `spine evolve` is the refresh loop. Init stays idempotent.

**Extra CLI verbs (addendum):** `wire`, `evolve`. Same CLI owns metadata; `npx skills` owns craft-skill files on harness roots.
