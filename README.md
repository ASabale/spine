# spine

Harness-agnostic process spine for humans and agents. Planning is a **map** plus **tickets**. Execution is a **work item**. Files in the **target** are the source of truth. The CLI is the only writer of status, owner, claim, links, and numbers.

**spine-cli 0.3.0** is fleet-capable: one-winner claims, YAML eval/review gates bound to the work-item body hash, doctor recovery, structured `run`, and `spine migrate`.

MIT. Command `spine`. PyPI: [spine-cli](https://pypi.org/project/spine-cli/). GitHub: [ASabale/spine](https://github.com/ASabale/spine).

## Install

Python **3.11+**.

```
uvx --from spine-cli spine init
```

or `uv tool install spine-cli` then `spine init`. Idempotent: missing artifacts only.

From this source tree:

```
uv run spine init
uv run pytest
make test
```

Dev gate: `make test`. Ship gate: `make release`.

## Sit-down

Agents:

```
spine prime
```

Doctor, then print next as JSON. Execute the first `{cmd, hitl}` in `run`. Empty `run` (`hitl: true`) means a human must act.

Humans: `spine doctor` then `spine next` / `spine status`. The `## Next` block is the next command. `spine run` prints the first executable `spine …` line, or exits 2 when the next step is HITL.

## Planning and execution

Chart a map under `docs/spine/maps/`, cut tickets under `docs/spine/tickets/`, work the frontier (open, unblocked, unclaimed). When the way is clear, mint a work item at `ready`. Planning never lives on the work item.

Work-item happy path: `ready → doing → checking → reviewing → done`. Bounce: `reviewing → changes-requested → doing`. Tickets: `open → claimed → resolved`. Both machines live in `docs/spine/contract.yaml` (the packaged copy in the wheel must stay byte-identical). Skills and the CLI reference that file; they do not restate it.

Software work items need real proofs, not “a file exists”:

- eval (`.spine/evals/<stem>.md`): `passed: true`, `command`, `when`, `revision`
- review (`.spine/reviews/<stem>.md`): `verdict` in `{approve, request-changes, block}`, plus `by`, `when`, `revision`, `evidence`

`checking → reviewing` needs a passing eval. `reviewing → done` needs that eval plus an `approve` review. `revision` is the sha256 of the Markdown **body** after frontmatter, so Status/Owner changes do not invalidate proofs.

## Claims

One-winner lock on a ticket or work item. A second agent or human gets exit 4; they do not rewrite the artifact to take it. Release is owner-only unless the claim is stale (4 hours) or doctor force-releases it. Frontmatter `Owner` / `Claimed-at` is the Git-visible copy.

`spine claim` with no target claims whatever `spine next` would claim.

## Recovery

- `spine doctor` — wake-up loop. Repairs illegal status, event-log drift, stale claims, broken links, and resolved/missing `Blocked by`. Prints before → after (why). Exit 8 when unrepaired. `--report-only` does not mutate.
- `spine migrate` — upgrade `contract.yaml` and coord schema (`--dry-run` / apply / `--rollback`).
- `spine evolve` — refresh binder skills from the wheel; `npx skills update` if present.

## Layout

Checked-in **spec tier** (`docs/spine/`):

- `maps/` — planning maps (index only)
- `tickets/` — map tickets (`NN-slug.md`)
- `work-items/` — execution work items
- `decisions/` — durable decisions
- `contract.yaml` — statuses and transitions
- `wires.yaml` — binder concern → skills.sh craft skills

Gitignored **execution tier** (`.spine/`): evals, reviews, handoffs, doctor, claims, `events.jsonl`, `coord.db`, migrate.

## CLI

`init` `status` `next` `run` `prime` `new` `claim` `show` `release` `set-status` `link` `doctor` `wire` `evolve` `migrate`

```
spine new --title "…" --ticket --work-item
spine new ticket --title "…"
spine new work-item --title "…" --profile software
```

`--json` on most verbs prints the same payload agents consume (`next`, `run`, `hitl`, `version`, …). Resolve stays inside `docs/spine` (symlink-safe). Typed exits: 0 ok, 2 usage / empty `run`, 3 illegal transition, 4 claim conflict, 5 validation, 8 inconsistent.

Craft skills are **not** vendored. Discover them on [skills.sh](https://www.skills.sh/). Default pack: [mattpocock/skills](https://www.skills.sh/mattpocock/skills). `spine wire --install` runs `npx skills add …`.

## Docs

- [spec.md](spec.md) — product contract
- [CONTEXT.md](CONTEXT.md) — glossary
- [CHANGELOG.md](CHANGELOG.md)
- [docs/spine/examples/dogfood.md](docs/spine/examples/dogfood.md) — claim → crash → doctor → eval → review → done
