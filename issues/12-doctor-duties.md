# Doctor duties

Type: grilling
Status: resolved
Blocked by: 05, 06, 07

## Question

What does `spine doctor` auto-fix vs only report? It is a CLI command, not a harness hook. A fresh session should be able to run it and know mid-flight work and mechanical drift.

Recommended auto-fix: stale claims past the policy window, broken bidirectional links the CLI owns, rollups the CLI owns. Report-only: unknown statuses after a contract bump, missing spec-tier files, gitignore drift. Never auto-edit content sections. How a harness *chooses* to run doctor on session start is adapter fog (out of required v1).

## Answer

Auto-fix: stale claims past the policy window, broken bidirectional links the CLI owns, rollups the CLI owns. Report-only: unknown statuses after a contract bump, missing spec-tier files, gitignore drift. Never auto-edit content sections. Harness session-start is adapter fog, not required v1. Doctor is a CLI command, not a hook.
