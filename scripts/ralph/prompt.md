# Ralph Agent Instructions (spine)

You are an autonomous coding agent. This iteration is a **fresh context**. Git, `scripts/ralph/prd.json`, and `scripts/ralph/progress.txt` are your only memory.

## Your Task

1. Read `scripts/ralph/prd.json`
2. Read `scripts/ralph/progress.txt` (Codebase Patterns first)
3. Pick the **highest priority** user story where `passes: false`
4. Implement **that one story only**
5. Run `uv run pytest -q` (and the tests named in acceptance criteria)
6. If checks pass, set that story's `passes` to `true` and fill `notes` with files changed
7. APPEND to `scripts/ralph/progress.txt` (never replace)
8. Update `HANDOFF.md` `## Current State` / `## Next Steps` without overwriting `## Live`

Do **not** push. Do **not** spawn subagents. Do **not** start a second GPU builder. Stay in `/Users/akshay/Development/spine`. Do not invent contract migration, adapters, extra type profiles, or CONTEXT/ADR scaffolding.

Commit only if pytest is green **and** this story's acceptance criteria are met. Message: `feat: [Story ID] - [Story Title]`. Skip commit if the working tree has unrelated dirty files you did not touch.

## Story size

If the story is too big for one context window, **split it**: write smaller stories into `prd.json` (new ids, `passes: false`), mark the original `passes: true` with notes `split`, and stop. Do not attempt a mega-slice.

## Progress report (append)

```
## [UTC time] - [Story ID]
- What was implemented
- Files changed
- Learnings for future iterations:
  - Patterns
  - Gotchas
---
```

If you discover a **reusable** pattern, add one bullet under `## Codebase Patterns` at the top of `progress.txt`.

## Quality

- CLI owns metadata; agents own content
- Do not restate the contract status table in binders
- Keep `src/spine/data/wires.yaml` and `docs/spine/wires.yaml` in sync
- `uv run pytest -q` must be green before `passes: true`

## Stop condition

After this story, if **every** story has `passes: true`, reply with:

<promise>COMPLETE</promise>

Otherwise end normally. The next fresh instance will pick the next story.

## Important

- ONE story per iteration
- Read Codebase Patterns before coding
- Keep CI green


## Local Qwen

You stall if you only think. **First tool call: write or edit a failing test** in `tests/test_next.py` for this story. Then implement. Do not spend the window planning. If the story is already satisfied, mark `passes: true` and stop.
