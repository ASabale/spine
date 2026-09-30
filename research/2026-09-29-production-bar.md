# Production bar: spine in September 2026

**Question.** Where does spine stand, in September 2026, against the tools a team would
actually trust to run a large software project with humans and coding agents — and what
is missing for that trust?

**Method.** Primary sources only: spine's own `spec.md`, `README.md`, `CHANGELOG.md`,
`docs/spine/maps/1.0.md`, source tree, and its public PyPI/GitHub state (queried 2026-09-29);
official docs/READMEs of GitHub Spec Kit, Beads, GitHub Copilot cloud agent, Claude Code,
OpenAI Codex, and skills.sh (all fetched 2026-09-29). No blog roundups. Every claim below
is tagged **[verified]** (source observed 2026-09-29) or **[inference]**.

## 1. Spine's verified state

### Public state (frozen 9 days)

- **[verified]** PyPI `spine-cli` has exactly three releases: 0.1.0 and 0.2.0 uploaded
  2026-09-19, 0.3.0 uploaded 2026-09-20. Requires Python ≥ 3.10, MIT, homepage
  `https://github.com/ASabale/spine`. (https://pypi.org/pypi/spine-cli/json)
- **[verified]** GitHub `ASabale/spine`: created 2026-09-19, last push 2026-09-20,
  0 stars, 0 forks, 0 open issues, 0 watchers, no topics, no discussions.
  (https://api.github.com/repos/ASabale/spine)
- **[verified]** The remote `main` is at `e168bcbb` "0.3.0: migrate, claims, identity"
  (2026-09-20). Its only CI check, `release`, concluded `success` 2026-09-20.
  (https://api.github.com/repos/ASabale/spine/commits, …/check-runs)
- **[verified]** PyPI `pypistats.org` has no download data for `spine-cli` (404) as of
  2026-09-29 — either too new for GA stats or no measurable downloads; treat as "no
  public adoption signal yet," not as zero.
- **[verified]** The PyPI name `spine` itself is occupied by an active unrelated project
  (HEP-related, latest 1.3.0 uploaded 2026-09-25, 54 releases), which is why spine ships
  as `spine-cli` (`uvx spine` fetches the wrong package).
  (https://pypi.org/pypi/spine/json; cf. `research/17-packaging-and-name.md`)
- **[verified]** The 0.3.0 wheel (29 files) ships `spine/data/contract.yaml`,
  `spine/data/wires.yaml`, and 7 binder `SKILL.md` bodies, so `spine prime` works
  dependency-free. (local `dist/spine_cli-0.3.0-py3-none-any.whl`)

### Unpublished state (local tree, not on GitHub)

- **[verified]** Local repo is 1 commit ahead of `origin/main` — `6d6c409` "docs: cut the
  1.0 plan (map + tickets 16-38)" — plus ~27 uncommitted modified ticket files. The 1.0
  plan and all in-flight 1.0 work (tickets 16–42) are not public.
- **[verified]** `docs/spine/maps/1.0.md` targets exactly this report's question: a
  "production tool a team would trust" (≥90% coverage floor→85, 3-OS × 3-Python CI matrix,
  ruff+pyright, PyPI trusted publishing, user guide, 50-worker harness). Frontier at time
  of writing: 16, 19, 20, 25, 27, 32, 34, 39, 42 — i.e., none of the productionization
  tickets are done.

### What 0.3.0 actually ships (repo paths)

- **[verified]** `spec.md` v0.3.0: three tiers (spec in git / execution gitignored /
  harness skills in git); versioned `contract.yaml` SSoT (status machine, HITL gates,
  profiles, claim policy, next selection); machine-verifiable eval+review gates as YAML
  with the sha256 of the work-item body; single-winner SQLite claims with 4 h stale
  (SPINE_USER identity); append-only `events.jsonl`; `spine doctor` repair (frontmatter
  vs event log); typed exit codes (0 ok, 1 usage, 2 invalid-transition, 3 contract,
  4 claim-conflict, 5 gate, 6 store); boundaries: single repo, no git-history rewrite,
  local files, no hosted orchestration, no multi-machine.
- **[verified]** `src/spine/gates.py` + `src/spine/engine.py`: `checking→reviewing`
  requires a passing eval whose `revision` equals the body hash; `reviewing→done`
  additionally requires `verdict: approve`, `by`, `evidence`, and that eval, review, and
  current body share one hash. Edits after done invalidate the gates.
- **[verified]** `src/spine/initcmd.py` + `src/spine/model.py`: the execution tier
  (`.spine/evals`, `.spine/reviews`, `.spine/claims`, `.spine/coord.db`,
  `.spine/events.jsonl`) is gitignored by `spine init`. `dump_front`/`engine.advance`
  persist only `Status`/`Owner`/`Claimed-at` into frontmatter — **the proofs, commands,
  verdicts, evidence, and revision hashes are not written to git**.
- **[verified]** Harness: `src/spine/binder.py` writes 7 concern skills; default wires
  (`src/spine/data/wires.yaml`) pull craft from `mattpocock/skills` (default pack) plus
  `vercel-labs/skills`, `anthropics/skills`, `obra/superpowers`, `affaan-m/ecc`.
- **[verified]** `Makefile` "production" gate today: lint = `python -m compileall`,
  typecheck = import smoke, `pytest`, invariants, coverage ≥ 70%, build, smoke —
  single `ubuntu-latest` job (`.github/workflows/ci.yml`). The ruff/pyright/3×3/85%
  gates are promises in the unpublished 1.0 map (tickets 27–31).
- **[verified]** Dogfood proof: `docs/spine/examples/dogfood.md` + `tests/test_dogfood.py`
  (crash → doctor → eval → review → done); `tests/` ≈ 24 files / ~2,250 lines.

## 2. Comparable tools, from their official sources (all fetched 2026-09-29)

### GitHub Spec Kit — `github/spec-kit`
- **[verified]** 139,153 stars, created 2025-08-21, pushed 2026-09-29 (today); latest
  release v1.0.13 (2026-09-29); 68 releases since 0.10.0; MIT, Python 3.11+
  (`specify` CLI). (https://github.com/github/spec-kit; api.github.com)
- **[verified]** Official README: works with "GitHub Copilot, Claude Code, Cursor,
  Gemini CLI, Codex, Command Code, Qwen, opencode, and more"; 200+ agent skills shipped
  as `/speckit-*` commands; three processes (core SDD, bug-fixing extension,
  idea-assessment extension); customization via extensions, presets, workflows, bundles.
- **[verified]** Docs (https://github.github.io/spec-kit/reference/agentic-sdd):
  `converge` is a "machine-verifiable gate" that decides whether a codebase converges on
  a spec; `analyze` is a read-only cross-artifact check; `checklist` is a quality gate
  for English requirements; templates can bind to pre-implement / post-impl /
  post-verify lifecycle hooks.
- **[inference]** Spec Kit has no claim/lock model (one "you + agent" per feature branch),
  no crash-recovery event log, and no typed exit-code contract; its `verify`/`converge`
  gates are LLM judgments, not hash-bound machine checks. It also does not ship a
  cross-machine sync story for runtime state — the artifacts (spec/plan/tasks) are
  in-repo files.

### Beads — `gastownhall/beads` (originally `steveyegge/beads`)
- **[verified]** 27,517 stars, 1,287 open issues, created 2025-05-19, pushed today;
  Go; docs say current release is 1.3.0. (api.github.com;
  https://beads.gascity.com/)
- **[verified]** Official README/docs: Dolt-backed (versioned SQL DB) issue tracker for
  AI agents; **cross-machine sync via Dolt push/pull over the git remote — "no server to
  run"**; atomic claims; schema-version guard that refuses to run a binary older than
  the database (anti-corruption); `--json` agent-optimized output; session compaction;
  agent messaging; works without git. (README;
  https://beads.gascity.com/core-concepts/sync-concepts)
- **[verified]** Distribution: `brew install beads`, `@beads/bd` on npm, `beads-mcp` 1.3.0
  on PyPI (MCP server), install script verifies SHA256/GPG checksums; `bd setup` installs
  hooks for Claude Code, Codex, Gemini, Copilot, Cursor, etc.
  (README; https://pypi.org/pypi/beads-mcp/json)
- **[verified]** Docs: workflows layer — formulas (TOML/JSON declarative templates),
  molecules (instantiated work graphs), gates (async coordination primitives: human,
  timer, GitHub), routing. (https://beads.gascity.com/)
- **[inference]** Beads' "done" is a tracker status a human/agent closes — not a
  hash-bound proof of behavior. Spine's gates are strictly stronger on *proof*; Beads is
  strictly stronger on *team, sync, and machine interop*.

### GitHub Copilot cloud agent (formerly "coding agent")
- **[verified]** Docs (https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent):
  "Generally available on all paid plans"; each task runs in an ephemeral GitHub Actions
  environment (auto-scrubbed); "up to 59 minutes per session"; "one task → one repo →
  one branch → one PR"; can't access secrets; assign via `@copilot` or `/copilot` on
  issues/PRs, and via **automations** that assign background tasks.
- **[verified]** Same docs: agent permissions, custom instructions, MCP servers, skills,
  and hooks can be scoped per-repo; **usage metrics and spend management**; **enterprise
  policy management** ("control cloud agent behavior across your organization").
- **[inference]** The most trusted agent-task runner for teams today is *hosted in
  GitHub's cloud*. Spine's "local-first, single repo, 1 human + agent fleet" is a
  deliberate opposite bet (1.0 decision D14/D18) — defensible, but it means spine
  competes for a different job: the durable, in-repo, machine-verified state layer, not
  the delegated-execution layer.

### Claude Code (Anthropic)
- **[verified]** Official docs (https://code.claude.com/docs/en/overview): surfaces in
  terminal, IDE, desktop, **web**, **mobile**; **headless** mode for CI/scripts; **Agent
  SDK**; subagents; **background agents**; **routines** ("recurring, automated work in
  Claude Code on Web"); hooks; skills; MCP; **GitHub Actions integration**; **Code
  Review** (agent-powered review on PRs); channels (Slack).
- **[verified]** Agent teams (https://code.claude.com/docs/en/agent-teams): experimental,
  disabled by default; lead + independent teammate sessions; a **shared task list with
  file locking for claims** ("Task claiming uses file locking to prevent race
  conditions"); task dependencies; mailbox messaging; display modes (in-process, tmux,
  iTerm2); **quality gates via hooks — `TaskCreated`, `TaskCompleted`, `TeammateIdle`,
  each can block with feedback**; documented limitations around session resumption and
  shutdown.
- **[inference]** Harness-native orchestration *with quality-gate hooks* is shipping from
  the harness itself. Anything living between harness and repo (spine's slot) must win on
  durability, cross-harness portability, and machine-verifiable gates — and must
  interoperate (hooks/MCP), which spine does not yet do (no adapter, explicitly deferred:
  `spec.md` "harness session-start is adapter fog, not required for v1").

### OpenAI Codex
- **[verified]** README (https://github.com/openai/codex): open source; CLI (terminal) +
  IDE extension (VS Code, Cursor, Windsurf, Eclipse) + Codex App (macOS/Windows) +
  **Codex Web (cloud)**; "Codex cloud lets you delegate tasks in the background"; works
  with **AGENTS.md**; sandboxing; MCP; skills.
- **[inference]** Same pattern as Copilot: local CLI + cloud delegation + an in-repo
  instruction convention (`AGENTS.md`). For spine, `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`
  files are the de-facto standard surface harness agents read first — spine's skills
  land in `.agents/skills` and are not wired into that file layer beyond the pack's own
  `teach` skill.

### skills.sh / `npx skills` (Vercel Labs) + mattpocock/skills
- **[verified]** skills.sh (https://www.skills.sh/): "The Agent Skills Directory"; "The
  Open Agent Skills Ecosystem" built by Vercel Labs; `npx skills add <owner/repo>`;
  leaderboard with ~1.5M all-time installs; cross-harness (Claude Code, Codex, Cursor,
  Amp, Codex, …). Backend repo `vercel-labs/skills`: 32,848 stars, created 2026-01-14,
  pushed 2026-09-28. (api.github.com)
- **[verified]** `mattpocock/skills` (spine's default pack;
  https://github.com/mattpocock/skills): a craft-skill pack (grilling, TDD, code-review,
  wayfinder, to-tickets, diagnosing-bugs, …) installed via Claude Code plugin or
  skills.sh. Its README positions itself **against** process-owning toolkits — "GSD,
  BMAD, Spec-Kit … take control away … these skills work with **your** process" — i.e.,
  explicitly *not* one of the Spec-Kit-style process owners.
- **[inference]** Tension worth naming: spine (a process owner) wires its defaults to a
  pack that publicly rejects process owners. Spine's binder answers it ("spine owns the
  process; skills are craft only") — but the default pack's own README is the first thing
  a user reads, and it says the opposite.

## 3. Trust dimensions, side by side

| Dimension (what a team needs) | spine 0.3.0 | Spec Kit v1.0.13 | Beads 1.3.0 | Copilot cloud agent | Claude Code |
|---|---|---|---|---|---|
| In-repo process SSoT (git is source of truth) | ✅ versioned `contract.yaml` + frontmatter | ✅ spec/plan/tasks files | ⚠️ DB gitignored; Dolt remote | ⚠️ GitHub data plane | ⚠️ session files |
| Durable crash recovery | ✅ `doctor` (event log) | ❌ not in official docs | ✅ resume/compact/claim sync | ✅ cloud session | ⚠️ resume (teams: known limitation) |
| Claims / locks, race-safe | ✅ SQLite single-winner + stale (single machine) | ❌ none | ✅ atomic claims + sync | ✅ (GitHub-side) | ✅ file-locked task list (experimental) |
| Cross-machine / team sync | ❌ single machine (1.0 decision D14) | ❌ | ✅ Dolt over git remote | ✅ hosted | ⚠️ web/cloud |
| Machine-verifiable gates bound to revision | ✅ eval/review hash-bound | ⚠️ `converge`/`analyze` = LLM judgment | ❌ status, not proof | ⚠️ PR review by agent | ⚠️ hook blocks, not revision-bound |
| Typed exit codes for scripting | ✅ 0–6 table | ❌ not documented | ✅ (JSON errors) | n/a | n/a |
| MCP / machine interop | ❌ none | ❌ not in README | ✅ `beads-mcp` + npm | ✅ | ✅ |
| Harness hooks integration | ❌ (deferred) | ✅ skills-as-commands | ✅ `bd setup <agent>` hooks | ✅ hooks | ✅ hooks |
| CI / engineering bar (public) | ⚠️ 1 OS, 1 Py, compileall-as-lint, import-as-typecheck, cov 70% | ✅ GitHub-run, 68 releases, extension ecosystem | ✅ Go, schema guard, checksummed installer, 1.3.0 line | ✅ first-party | ✅ first-party |
| Adoption / track record | ❌ 0★/0 forks, 10 days old, 3 releases | ✅ 139k★, 13 mo, 68 releases | ✅ 27.5k★, 16 mo | ✅ first-party, GA | ✅ first-party |
| Distribution trust | ⚠️ plain PyPI uploads; name `spine` occupied | ✅ first-party GitHub | ✅ checksum/GPG-verified installs | ✅ first-party | ✅ first-party |
| Docs / onboarding | ⚠️ README + spec only; guide = 1.0 ticket | ✅ docs site + method pages | ✅ docs site | ✅ docs | ✅ docs |
| Multi-human policy / roles | ❌ single human (1.0 decision D15) | ⚠️ "you + agent" | ⚠️ tracker users, no policy | ✅ enterprise policy mgmt | ⚠️ permission modes |
| UI | ❌ (1.0 decision D16: no UI) | ⚠️ files/CLI | ⚠️ CLI (community UI) | ✅ web | ✅ desktop/web/mobile |

## 4. Ranked gaps — what would stop a human or agent relying on spine for a large project

1. **Proofs are not verifiable by a second party.** Eval/review/claims/events live in
   gitignored, single-machine files; `advance` writes only `Status`/`Owner`/`Claimed-at`
   into git (`src/spine/engine.py`, `src/spine/initcmd.py`). A teammate's clone, a CI
   job, or an auditor sees `Status: done` but **cannot see or check the proof**, the
   command, the verdict, or the revision hash. The gates' entire value (trust) does not
   survive `git clone`. Even Spec Kit keeps its artifacts in-repo; Beads syncs via Dolt.
   Spine's 1.0 decision D14 (single machine) is honest, but it caps "large project" at
   one checkout — and with no MCP/server/`spine export`, there is no remote verification
   channel at all.
2. **Zero external adoption and a frozen public state.** 0 stars, 0 forks, 0 issues, no
   topics/discussions; last PyPI release 9 days ago (0.3.0); the 1.0 plan and all
   productionization tickets are unpushed (`origin/main` = `e168bcbb`). Teams buy trust
   from track record, release cadence, and a public roadmap; spine currently has
   only the author's own dogfood (spine on spine) as evidence.
3. **No harness interop while harnesses ship orchestration natively.** No hooks
   integration, no MCP, no adapters (deferred by spec). Claude Code agent teams ship
   file-locked shared task lists *and* `TaskCompleted` quality-gate hooks; Beads ships
   `bd setup <agent>` hooks and an MCP server; Copilot ships automations + policy
   management. A team gets 80% of spine's coordination from its harness alone; spine
   must prove the extra layer is worth the friction of shelling out — and currently
   cannot even enforce gates from inside the harness.
4. **Public engineering gates are thinner than the category's floor.** CI = one OS, one
   Python, `compileall` as lint, import-smoke as typecheck, 70% coverage floor
   (`Makefile`, `.github/workflows/ci.yml`). The credible gates (ruff, pyright,
   3-OS × 3-Python, 85%, trusted publishing) exist only as private 1.0 tickets (27–31,
   37). Beads and Spec Kit both run stricter, first-party-visible CI today.
5. **No distribution/supply-chain story.** Plain PyPI uploads (no trusted publishing,
   signing, or checksums — ticket 37 unshipped), while Beads verifies SHA256/GPG on
   install; and `spine` on PyPI is occupied by an active unrelated package (1.3.0,
   2026-09-25), so discoverability and accidental-install risk are live.
6. **No audit/history surface for an organization.** `events.jsonl` is local and
   append-only; timeline/audit/history is explicitly "fog" (spec.md boundaries). A large
   project needs exportable, inspectable history (who, what, when, with what evidence) —
   spine has no `spine audit`/export at all.
7. **No user-facing docs beyond README + spec.** No hosted docs site, no user guide, no
   "first loop" walkthrough outside the binder skills (1.0 tickets 32/33/41). Spec Kit
   and Beads both run docs sites with methodology pages; that is the surface a team
   evaluates trust on.
8. **Positioning friction with its own default pack.** The default wire
   (`mattpocock/skills`) publicly positions against process-owning toolkits "GSD, BMAD,
   Spec-Kit" — which spine *is*. Spine's binder framing ("craft vs control") resolves it
   in code, but the default pack's README is the first thing users read.
9. **Single-human boundary is narrow for "large project."** No roles, no review routing,
   no policy (1.0 decision D15; HITL = creating + reviewing only). Fine for one trusted
   human; a team of N reviewers needs routing/policy (Beads has human/timer/GitHub gate
   primitives; Copilot has org policy management).

## 5. The single biggest gap

**Spine's machine-verifiable proofs (evals, reviews, claims, events) live in
gitignored, single-machine files, so no second party — teammate, CI, auditor, or future
session on another machine — can ever verify that a work item is truly `done`; the exact
trust property the gates exist to provide does not survive a `git clone`, while every
comparable tool either keeps its artifacts in-repo (Spec Kit), syncs state across
machines (Beads, Copilot cloud), or both.**

---

### Source register (all accessed 2026-09-29)

| Source | Used for |
|---|---|
| `spec.md`, `README.md`, `CHANGELOG.md`, `CONTEXT.md`, `HANDOFF.md`, `docs/spine/maps/1.0.md`, `Makefile`, `.github/workflows/ci.yml`, `src/spine/{model,gates,engine,artifacts,initcmd}.py`, `src/spine/data/{contract,wires}.yaml`, `dist/spine_cli-0.3.0*.whl`, `docs/spine/examples/dogfood.md` (local repo) | spine's verified state |
| https://pypi.org/pypi/spine-cli/json · https://pypi.org/pypi/spine/json · https://pypistats.org/api/packages/spine-cli/recent · https://pypi.org/pypi/beads-mcp/json | public packaging state |
| https://api.github.com/repos/ASabale/spine (+ /commits, /check-runs) · https://api.github.com/repos/github/spec-kit (+ /releases) · https://api.github.com/repos/steveyegge/beads · https://api.github.com/repos/vercel-labs/skills | GitHub metadata |
| https://raw.githubusercontent.com/github/spec-kit/main/README.md · https://github.github.io/spec-kit/reference/agentic-sdd | Spec Kit |
| https://raw.githubusercontent.com/gastownhall/beads/main/README.md · https://beads.gascity.com/ (+ /core-concepts/sync-concepts) | Beads |
| https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent | Copilot cloud agent |
| https://code.claude.com/docs/en/overview · https://code.claude.com/docs/en/agent-teams | Claude Code |
| https://raw.githubusercontent.com/openai/codex/main/README.md | Codex |
| https://www.skills.sh/ · https://raw.githubusercontent.com/mattpocock/skills/main/README.md | skills ecosystem |
