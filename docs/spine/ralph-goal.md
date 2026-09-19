# Ralph goal

Task list is `scripts/ralph/prd.json` (snarktank format: `passes`, `priority`, verifiable `acceptanceCriteria`).
Memory between iterations is git + `scripts/ralph/progress.txt`.
Loop: `scripts/ralph.sh` → `scripts/ralph/ralph.sh`.

Do not invent contract migration, adapters, extra type profiles, or CONTEXT/ADR scaffolding.
Do not spawn a second GPU builder. Do not install the full ECC plugin. Do not print secrets. Do not push.

Human STOP: put `STOP` on its own line here **or** set every story `passes: true`.
