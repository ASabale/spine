# Packaging and name

Type: research
Status: resolved

## Question

Facts a naming and packaging decision needs: (1) can a stranger run a Python CLI via `uvx` / `uv tool install` in 2026, and what is the current packaging layout (pyproject, scripts, data files for a contract + SKILL.md)? (2) is the name `spine` blocked or confusing on PyPI and GitHub?

Write the report at [research/17-packaging-and-name.md](../research/17-packaging-and-name.md). Do not pick the product name.

## Answer

Report: [research/17-packaging-and-name.md](../research/17-packaging-and-name.md).

A stranger can run a Python CLI in 2026 with `uvx <pkg>` or `uv tool install <pkg>` (uv 0.12.17). Need `pyproject.toml`, a build backend, and `[project.scripts]`. Non-code files (contract, SKILL.md) must be explicitly packed (Hatchling `force-include` / package-data) and read via `importlib.resources`; init still has to copy skills onto harness discovery paths. The PyPI name `spine` is taken (DeepLearnPhysics HEP, v1.2.4 uploaded 2026-09-16) — `uvx spine` would install that package. `spine-engine` is also taken (VTT workflows). `spine-cli`, `process-spine`, `harness-spine` were free this day. GitHub org `spine` is the dormant JS MVC project; Esoteric Spine, Cacti/spine, and synaptixs/spine (2026 agent-orchestrator) are the confusion set. A personal repo slug is still available; exact PyPI `spine` is not.
