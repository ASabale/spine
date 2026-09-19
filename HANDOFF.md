# Handoff: spine implementation

Last updated: 2026-09-19

## Objective

v1 spine-cli from spec.md. Auto-evolvable, skills.sh wires, Matt Pocock default pack, doctor recovery.

## Current State

Working CLI. `uv run pytest` — 19 passed. Wheel packs binder + contract.

Software `checking → reviewing` needs `.spine/evals/` proof named for the item; `reviewing → done` needs `.spine/reviews/`. `spine wire --install` builds `npx skills add <pack> -s …` from `wires.yaml`. Doctor reports missing spec files (README, contract, wires, map) and gitignore drift (no auto-fix). GitHub: https://github.com/ASabale/spine. PyPI: https://pypi.org/project/spine-cli/ (0.1.0). Next: `spine wire --install` in a throwaway git repo.

Builder queue (SpineDoctor/Binder/Evolve/Serial) died with Metal GPU OOM; do not parallel-spawn local Qwen for this tree.

## Next Steps

- Create `ASabale/spine` and publish `spine-cli` only when asked.
- Do not edit generic-workflows.
- One small builder at a time if using the local model.
