# Binder skill shape

Type: grilling
Status: resolved
Blocked by: 07, 09, 16

## Question

What does a binder `SKILL.md` contain so it works in any harness that can load a skill file, never restates the contract, and calls the CLI for metadata?

Use [Harness skill discovery](16-harness-skill-discovery.md) for how Cursor, Claude Code, Codex CLI, and oh-my-pi actually load skills (paths, frontmatter, namespacing). Init’s job of placing those files is [Init and stranger-install](14-init-and-stranger-install.md).

Recommended: YAML frontmatter + short body: when to use, CLI invocations by pointer, `## Gate` names that exist in the contract (not copied statuses). No Devin `hooks.v1.json`. If a harness needs a copy in `.agents/skills` vs `.cursor/skills`, init writes the copies; the skill text is one.

## Answer

YAML frontmatter + a short body: when to use, CLI invocations by pointer, `## Gate` names that exist in the contract (not copied statuses). One skill text. Init writes copies onto harness roots (`.agents/skills`, `.claude/skills`, and others as needed). No Devin `hooks.v1.json`. Skills never restate the contract; the CLI owns metadata.
