# Harness skill discovery (2026-09-18)

Facts only. Sources: official docs plus on-disk evidence on this Mac. No product recommendation.

## Shared shape (Agent Skills)

Cursor, Claude Code, and Codex all describe skills as a directory containing `SKILL.md` with YAML frontmatter. The open standard is [agentskills.io](https://agentskills.io) / [skill.md](http://skill.md/). Common minimum: `name` + `description`. A skill **outside** a harness’s discovery roots is invisible to that harness unless copied, symlinked, or loaded via a plugin (plugin APIs are out of this ticket’s “without a plugin API” scope except as a named extra path).

On this machine (2026-09-18): `~/.claude/skills/` (user skills present), `~/.cursor/skills/` (user skills present), `~/.agents/skills` via `/Users/akshay/Development/.agents/skills` (project-level at Development), `~/.omp/` exists (agent home, not a skills tree at the root), **no** `~/.codex`.

---

## Cursor

**Docs:** [cursor.com/docs/skills](https://cursor.com/docs/skills.md) (fetched 2026-09-18).

### Paths

| Scope | Path |
| --- | --- |
| Project | `.agents/skills/`, `.cursor/skills/` |
| User | `~/.agents/skills/`, `~/.cursor/skills/` |
| Compatibility | also `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, `~/.codex/skills/` |

Cursor walks the skills root **recursively** and picks up any `SKILL.md`. Nested category folders are organizational; identity is the folder that contains `SKILL.md`. A `.cursor/skills/` or `.agents/skills/` **anywhere in the repo** is discovered. Nested project directories are scoped to files under that directory (similar to `paths` frontmatter).

User skills in `~/.cursor/skills/` stay local unless “Sync Skills for Cloud Agents” is on. Cursor does **not** copy `~/.agents/skills/` or unsynced local skills to Cloud Agents / Agents Window remote SSH / self-hosted workers.

### Filename / frontmatter

Folder + `SKILL.md`. Required: `name`, `description`. `name`: lowercase letters, numbers, hyphens; **must match the parent folder name**. Optional: `paths`, `disable-model-invocation`, `icon`, `color`, `metadata`. Legacy `globs` still accepted; new skills should use `paths`.

### Naming

Identity = folder containing `SKILL.md`. Slash invoke: `/skill-name`. Manual `/` search also works.

### Invisible if

Not under the listed roots (and not in a plugin). Cloud/remote agents miss unsynced user skills and `~/.agents/skills/`.

### Stale risk

Cursor 2.4 `/migrate-to-skills`; compatibility load of Claude/Codex dirs; `paths` vs `globs`; Cloud Agents sync policy. Docs already treat Agent Skills as the portable format.

**On-disk:** `~/.cursor/skills/find-skills/SKILL.md` has `name` + `description`. `/Users/akshay/Development/.cursor` exists (skills dir present).

---

## Claude Code

**Docs:** [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) (fetched 2026-09-18). Follows Agent Skills; Claude Code adds extra frontmatter.

### Paths

| Scope | Path |
| --- | --- |
| Personal | `~/.claude/skills/<name>/SKILL.md` |
| Project | `.claude/skills/<name>/SKILL.md` |
| Nested | `<subdir>/.claude/skills/<name>/SKILL.md` (loads when session works in/below that dir, or via `/add-dir`) |
| Additional dir | `.claude/skills/` under `--add-dir` / `/add-dir` |
| Enterprise | `.claude/skills/` in managed settings |
| Legacy commands | `.claude/commands/*.md` still work as `/name` |
| Reserved | do not name a folder `synced` (used for claude.ai download) |

Walks project skills from start dir **up to repo root**. Nested skills below start dir load lazily when files there are touched (v2.1.257+ `/add-dir` can force earlier). Symlinked skill folders supported for enterprise/personal/project.

Personal `~/.claude/skills/` does **not** load in Cowork or cloud sessions.

### Filename / frontmatter

`SKILL.md` with opening `---` as line 1. **Directory name is the command** for personal/project skills; `name` is display-only there. `description` recommended (used for auto-invoke; truncated at 1,536 chars with `when_to_use`). Many Claude-only fields (`allowed-tools`, `context: fork`, `hooks`, …). Spec-only fields for claude.ai upload: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` — extra keys **fail** upload.

### Naming

`/directory-name`. Nested clash: `/apps/web:deploy`. Plugin skills: `/plugin-name:skill-name`. Precedence: enterprise > personal > project for the same `/name`.

### Invisible if

Outside `.claude/skills` (or commands, plugins, synced account, managed). Nested skill not yet loaded. Cowork/cloud without account enable or committed project skills.

### Stale risk

High: docs cite many v2.1.x behavior changes (sync, nested load, `skillOverrides`, doctor as bundled skill). Recheck this page before locking init copies.

**On-disk:** `~/.claude/skills/` has 38 user skill dirs (grilling, wayfinder-adjacent names, etc.).

---

## Codex CLI

**Docs:** [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) (fetched 2026-09-18).

### Paths (no plugin required)

| Scope | Location |
| --- | --- |
| REPO | `$CWD/.agents/skills`, then each parent `.agents/skills` up to `$REPO_ROOT/.agents/skills` |
| USER | `$HOME/.agents/skills` |
| ADMIN | `/etc/codex/skills` |
| SYSTEM | bundled with Codex |

Symlinked skill folders are followed. Duplicate `name` values are **not** merged; both can appear in selectors. Disable without delete: `[[skills.config]]` in `~/.codex/config.toml` with `path` + `enabled = false` (restart after edit).

Optional `agents/openai.yaml` for ChatGPT UI / `allow_implicit_invocation`. Distribution beyond a repo is plugins (out of “file drop” init).

### Filename / frontmatter

Directory + `SKILL.md`. **`name` and `description` required.** Optional `scripts/`, `references/`, `assets/`.

### Naming

Frontmatter `name`. Implicit match uses `description`. Explicit: `$skill` / `/skills` in CLI.

### Invisible if

Not under those `.agents/skills` (or admin/system/plugin) trees. This Mac has **no** `~/.codex` home; Codex is not installed locally, so user-level Codex-only paths were not observed.

### Stale risk

Repo scan is **`.agents/skills`**, not `.codex/skills`. Cursor still *loads* `.codex/skills/` for compatibility; Codex’s own local discovery as documented here does not list `.codex/skills/` as a REPO/USER root. That mismatch will confuse init if it only writes `.codex/skills`. Initial skills list budget: 2% of context or 8k chars.

---

## oh-my-pi (omp)

**Docs:** local checkout `/Users/akshay/Development/oh-my-pi/docs/skills.md` (this Mac’s source of truth; `https://omp.sh/docs/skills` fetch returned a thin marketing page). Implementation pointers in that file: `packages/coding-agent/src/extensibility/skills.ts`, `discovery/builtin.ts`.

### Paths

Provider-based, **one level** under each `skills/` root: `<root>/skills/<skill-name>/SKILL.md`. Nested `skills/group/skill/SKILL.md` is **not** discovered unless `skills.customDirectories` points at the nested parent (scan still non-recursive).

Registered providers (priority, first name wins):

1. `native` (100) — `.omp` user/project skills
2. `omp-plugins` (90)
3. `claude` (80) — Claude skill dirs
4. `claude-plugins`, `agents`, `codex` (70) — `.agent[s]/skills` is described as the **canonical OMP-native location** (`enableAgentsUser` / `enableAgentsProject`)
5. `opencode` (55)
6. `github` (30) — `.github/skills/<name>/SKILL.md` (project only)
7. `omp-managed` (5) — `~/.omp/agent/managed-skills`

Toggles can disable Claude/Codex/Pi user or project sources; the agents provider is independent. `skills.enabled = false` loads nothing.

**On-disk:** `~/.omp/{agent,cache,logs,...}` — no top-level `skills/` here. Project skills used by this session live at `/Users/akshay/Development/.agents/skills/` (wayfinder `SKILL.md` with `name`, `description`, `disable-model-invocation: true`).

### Filename / frontmatter

`name` defaults to directory name. `description` **required** for native `.omp`, omp-plugins, github, and `customDirectories`. Claude/Codex/agents providers can load without description. Also: `globs`, `alwaysApply`, `hide`, `disable-model-invocation` (normalized from kebab-case).

### Naming

Skill `name`; `/skill:<name>`; `skill://<name>` and `skill://<name>/relative`.

### Invisible if

Nested more than one level under `skills/` without a custom directory; `hide` still loaded but omitted from the advertised list; disabled by toggles/`ignoredSkills`; not in any provider root.

### Stale risk

omp discovery is implementation-defined and versioned with the agent. Recheck `docs/skills.md` in the installed omp. Recursive Cursor vs non-recursive omp is a real init fork: a nested taxonomy Cursor finds, omp will miss.

---

## Cross-harness overlap (fact)

Writing **one** tree at **project** `.agents/skills/<name>/SKILL.md` is documented as a discovery root for **Cursor** and **Codex**, and as omp’s agents provider. It is **not** Claude Code’s project root (that is `.claude/skills/`). Cursor additionally loads `.claude/` and `.codex/` for compatibility. omp additionally loads Claude and Codex providers if those toggles are on.

A skill sitting only in `docs/` or a Python package’s site-packages is invisible until init copies (or symlinks) it into a discovery root.

## Inference

- Init that targets “any of the four” likely needs **at least two project copies** of the same binder text (`.agents/skills` and `.claude/skills`), or rely on Cursor/omp compatibility loaders for Claude/Codex dirs — those compatibility paths are harness-specific and can change.
- User-level installs (`~/.agents/skills`, `~/.claude/skills`, `~/.cursor/skills`) do not travel with a cloned target repo.
