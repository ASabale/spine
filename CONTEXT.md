# Spine

A public, harness-agnostic process spine. Planning and execution survive sessions as files in a target repo. This glossary is for the product; implementation detail does not belong here.

## Language

**Spine**:
The toolkit: a versioned contract, a CLI that owns metadata, binder skills, and a doctor. Installed into a target.
_Avoid_: Generic Workflows, plugin, pipeline-as-the-product

**Target**:
A git repository `spine` inits. Artifact files live here. They are the source of truth.
_Avoid_: host, workspace (ambiguous with the agent’s cwd)

**Map**:
The durable planning artifact in the target: destination, notes, decisions-so-far, fog, out of scope. Tickets are its children.
_Avoid_: board, PRD, roadmap

**Ticket**:
One decision or investigation on a map. Types: research, prototype, grilling, task.
_Avoid_: issue (overloaded with work item), card

**Work item**:
The durable execution artifact: status, owner, claim, links, next gate.
_Avoid_: task (overloaded with Wayfinder task tickets and Generic Workflows’ pipeline file), issue

**Contract**:
The versioned machine: statuses, transitions, gates, type profiles. Skills and the CLI reference it; they never restate it.
_Avoid_: lifecycle.json as a proper noun, config, schema (too generic)

**Binder**:
Concern → skill routing. Skills never restate the contract.
_Avoid_: router, catalog, palette (unless we later name the user-facing surface)

**CLI**:
Harness-agnostic command-line tool on PATH. It inits a target and is the only writer of machine-driving metadata.
_Avoid_: plugin, hook, wf.py

**Doctor**:
A CLI command that reports mechanical drift and may auto-fix it. Not a harness hook.
_Avoid_: health hook, UserPromptSubmit

**Software profile**:
A type profile on the same contract for code work (build / eval / review). Optional relative to the agnostic spine; in v1 spec.
_Avoid_: the pipeline, 16-status machine

**Claim**:
Solo-first lock on a work item (owner + stale release) so a second agent or human does not require a rewrite.
_Avoid_: assignee (tracker-specific), lock

**Spec tier**:
Checked-in artifact files in the target (maps, tickets, work items, decisions). Shared with clones.
_Avoid_: source of truth (the whole target-file set is SSoT, including local execution files on that machine)

**Execution tier**:
Gitignored local files (claims runtime, evals, handoffs, doctor output). Not required for a clone to be correct, required for a running session to resume on that machine.
_Avoid_: state, cache
