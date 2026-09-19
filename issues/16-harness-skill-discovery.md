# Harness skill discovery

Type: research
Status: resolved

## Question

How do current agent harnesses load skills **without** a plugin API, in enough detail that init knows where to write binder `SKILL.md` files?

Cover at least: Cursor, Claude Code, Codex CLI, oh-my-pi. For each: discovery paths (project vs user), required frontmatter, naming, whether a skill outside those paths is invisible, and any 2026-era change that would stale this.

Write the report at [research/16-harness-skill-discovery.md](../research/16-harness-skill-discovery.md). Do not recommend product decisions.

## Answer

Report: [research/16-harness-skill-discovery.md](../research/16-harness-skill-discovery.md).

Without a plugin API, all four harnesses only load a folder of `SKILL.md` under known roots. Cursor: `.agents/skills` and `.cursor/skills` (project and `~/`), recursive, plus Claude/Codex dirs for compatibility; frontmatter `name` must match the folder. Claude Code: `.claude/skills` (project) and `~/.claude/skills` (user); command name is the directory; nested dirs load lazily. Codex CLI: `.agents/skills` from CWD up to repo root, plus `~/.agents/skills`; `name`+`description` required; this Mac has no `~/.codex`. omp: one-level `<root>/skills/<name>/SKILL.md`; `.agents/skills` is canonical; Claude/Codex providers optional; nested taxonomy is invisible unless `customDirectories` is set. A wheel or `docs/` copy is invisible until init places files in those roots. Cursor vs omp recursion, and Claude’s distinct `.claude/skills` path, are the init forks. Claude Code’s v2.1.x notes will stale fastest.
