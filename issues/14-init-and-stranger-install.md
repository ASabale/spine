# Init and stranger-install

Type: grilling
Status: resolved
Blocked by: 01, 02, 03, 05, 07, 08, 16

## Question

End-to-end stranger story: install the CLI, init a git repo, get contract + binder skills + spec/execution dirs + gitignore, run doctor once. No plugin marketplace. No clone of the spine source repo required.

Use [Harness skill discovery](16-harness-skill-discovery.md) for where init must write skill files so at least one of Cursor / Claude Code / Codex / oh-my-pi sees them without a plugin API. If harnesses disagree on paths, init may write multiple copies of the same binder text.

Recommended: `uvx <name> init` in the target (or `uv tool install` then `spine init`). Idempotent: missing artifacts only, refresh offered. README in this spec names the one-liner. GitHub home is documentation, not an install dependency.

## Answer

Stranger runs `uvx --from spine-cli spine init` in a git repo (or `uv tool install spine-cli` then `spine init`). Init writes contract, binder skills onto harness roots (same text, multiple copies as needed: `.agents/skills`, `.claude/skills`, …), spec-tier dirs under `docs/spine/`, `.spine/` plus `.gitignore`, short `docs/spine/README.md`. Idempotent: missing artifacts only; refresh offered. Then `spine doctor` once. No plugin marketplace. No clone of the spine source repo. GitHub home is documentation, not an install dependency.
