# Wayfinder map: spine spec

Labels: `wayfinder:map`

## Destination

A written spec (`spec.md`) for **spine** — a public toolkit: an evolvable, harness-agnostic process spine. Planning durability is a map + tickets; execution durability is a work item (status, owner, claim, links, next gate). Repo files in the **target** are the source of truth. A CLI on PATH inits a target and owns metadata + doctoring; **binder** skills route by concern and never restate the **contract**. v1 spec includes a **software profile**. Spec locks final name, license, stranger-install, and intended GitHub home. This map stops at the spec.

## Notes

- Domain: process spine (not a Devin/Cursor/Claude plugin). Glossary: [CONTEXT.md](CONTEXT.md). Tracker: [docs/issue-tracker.md](docs/issue-tracker.md). Workspace: `/Users/akshay/Development/spine`.
- Skills every session: `wayfinder`, `grilling`, `domain-modeling`. Research → `researcher`. Resume: [AGENTS.md](AGENTS.md), [HANDOFF.md](HANDOFF.md).
- **Plan, don’t do.** No product code. No GitHub create/push. One non-research ticket per session.
- Frozen prior art: `/Users/akshay/Development/generic-workflows`. Do not edit it. Do not put that name on GitHub.
- Standing preferences from charting (2026-09-18): planning profile **is Wayfinder as files**; execution machine **designed short from scratch** (do not import the 16-status pipeline); CLI is **Python distributed with uv**; toolkit **ships binder skills** (not the craft catalog); artifacts use **two tiers** (spec vs execution).
- Leading words: spine, target, map, ticket, work item, contract, binder, CLI, doctor, software profile, claim, spec tier, execution tier.

## Decisions so far

- [Harness skill discovery](issues/16-harness-skill-discovery.md) — binder files only load from harness skill roots; `.agents/skills` covers Cursor+Codex+omp, Claude needs `.claude/skills`; wheels are invisible until init copies
- [Packaging and name](issues/17-packaging-and-name.md) — `uvx` works; `[project.scripts]` + explicit data files; PyPI `spine` is taken (HEP, active 2026-09-16)
- [License](issues/02-license.md) — MIT
- [Name the public toolkit](issues/01-name-the-toolkit.md) — product/GitHub/CLI `spine`; PyPI `spine-cli`
- [GitHub owner](issues/03-github-owner.md) — ASabale/spine (not created on this map)
- [Wayfinder as files](issues/04-wayfinder-as-files.md) — this workspace’s tracker: one map, child tickets, CLI owns claim
- [Two-tier paths](issues/05-two-tier-paths.md) — spec `docs/spine/{maps,tickets,work-items,decisions}/` + README; execution `.spine/` gitignored
- [Short execution machine](issues/06-short-execution-machine.md) — ready → doing → checking → reviewing → done; bounce changes-requested → doing
- [CLI verb surface](issues/07-cli-verb-surface.md) — init status new claim release set-status link doctor
- [Python uv packaging](issues/08-python-uv-packaging.md) — 3.11+; PyPI `spine-cli`; script `spine`; contract + SKILL.md in the wheel
- [Binder concern table](issues/09-binder-concern-table.md) — new, wayfind, next, doctor, build, eval, review
- [Binder skill shape](issues/10-binder-skill-shape.md) — YAML + short body; one text; init copies; no restated contract
- [Software profile](issues/11-software-profile.md) — software: checking + reviewing; non-software may doing → done
- [Doctor duties](issues/12-doctor-duties.md) — auto-fix stale claims, CLI links, rollups; report unknown statuses, missing spec files, gitignore
- [Claim policy](issues/13-claim-policy.md) — Owner + Claimed-at; stale 4h; user.name or SPINE_USER
- [Init and stranger-install](issues/14-init-and-stranger-install.md) — `uvx --from spine-cli spine init`; idempotent; no clone
- [Write the spec](issues/15-write-the-spec.md) — [spec.md](spec.md)

## Not yet specified

- Contract versioning beyond the shipped `spine migrate` (0.2.0 tree).
- Optional per-harness adapters (hooks, plugins) — never required for correctness.
- A docs-only type profile besides the software profile.
- How already-wayfinding folders (agent-companion, finances, …) relate to a spine-inited target.
- Whether init scaffolds CONTEXT.md / ADR conventions.
- Work-item templates (PRD, blueprint) — software-profile or not.
- User-level vs project-level install besides `uvx` + init.

## Out of scope

- Editing generic-workflows.
- Publishing under the name Generic Workflows.
- Harness plugins or hooks as required.
- Code graph (CRG / Graphify).
- Shipping a full craft-skill catalog (grilling, tdd, … vendored 44-deep).
- Implementing spine.
- Creating or pushing the GitHub repository (spec names the home; create is after).
- Importing Generic Workflows’ 16-status idea→done machine.
