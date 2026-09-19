# CLI verb surface

Type: grilling
Status: resolved

## Question

What commands does the CLI expose in v1? Humans and agents invoke the same CLI. It is the only writer of machine-driving metadata (status, owner, claim, links, numbers).

Recommended verbs: `init`, `status` (board), `new` (work item and/or map ticket), `claim`, `release`, `set-status`, `link`, `doctor`. No harness-specific subcommands. No plugin install. Packaging is [Python uv packaging](08-python-uv-packaging.md); statuses come from [Short execution machine](06-short-execution-machine.md).

## Answer

v1 verbs: `init`, `status`, `new`, `claim`, `release`, `set-status`, `link`, `doctor`.

- `init` — scaffold a target.
- `status` — board (work items + next gate).
- `new` — mint a work item and/or a map ticket (flags, not a second verb).
- `claim` / `release` — solo-first lock the CLI owns.
- `set-status` — only legal transitions from the contract.
- `link` — CLI-owned bidirectional links (numbers).
- `doctor` — mechanical drift.

Same surface for humans and agents. No harness-specific subcommands. No plugin install. Packaging stays on [Python uv packaging](08-python-uv-packaging.md).
