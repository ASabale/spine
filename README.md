# spine

Harness-agnostic process spine. Planning is a map + tickets. Execution is a work item. Files in the **target** are the source of truth. Claims are one-winner. Eval/review gates are YAML mappings bound to the work-item body hash.

MIT. CLI command `spine`. PyPI: [spine-cli](https://pypi.org/project/spine-cli/). GitHub: [ASabale/spine](https://github.com/ASabale/spine).

## Install

```
uvx --from spine-cli spine init
```

From this source tree:

```
uv run spine init
uv run pytest
make test
```

## Stranger loop

1. `spine init` — spec dirs, starter map, `.spine/`, gitignore, binder skills, default `wires.yaml`
2. `spine prime` — agent sit-down (doctor + next as JSON). Humans: `spine doctor` then `spine next` / `spine status`
3. `spine run` — print the first executable `spine …` command (`run` is `{cmd, hitl}` mappings)
4. `spine wire --install` — `npx skills add mattpocock/skills` (skills.sh). Needs `npx`.
5. `spine evolve` — refresh binder from the wheel; `npx skills update` if present
6. `spine migrate` — upgrade `contract.yaml` and coord schema (`--dry-run` / apply / `--rollback`)

## Verbs

`init` `status` `next` `run` `prime` `new` `claim` `show` `release` `set-status` `link` `doctor` `wire` `evolve` `migrate`

`spine new --title "…" --ticket --work-item` mints both. Same command with a kind: `spine new ticket --title "…"`.

Craft skills are **not** vendored. Discover them on [skills.sh](https://www.skills.sh/). Default pack: [mattpocock/skills](https://www.skills.sh/mattpocock/skills).

Dev gate: `make test`. Ship gate: `make release`.

See [spec.md](spec.md).
