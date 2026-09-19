# Implementation notes (this repo is also the first target)

Implement spine from [spec.md](spec.md) plus this file. Product code lives here now.

## Every session

1. Read [spec.md](spec.md), [CONTEXT.md](CONTEXT.md).
2. Verify: `uv run pytest`.
3. CLI owns metadata; agents own content. Binder skills never restate the contract.
4. Craft skills come from skills.sh (`npx skills add mattpocock/skills`), not vendored.

## Standing constraints

- Harness/agent/platform agnostic. No required plugin API.
- Auto-evolve: `spine evolve`. Self-recover: `spine doctor`.
- Do not edit `/Users/akshay/Development/generic-workflows`.
