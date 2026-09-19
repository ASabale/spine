# Packaging and name (2026-09-18)

Facts only. Does not pick the product name.

Checked: uv docs, PyPI JSON API, GitHub search API, PEP 621 / PyPUG, Hatchling build config. uv on PyPI: **0.12.17** this day.

---

## 1. Stranger install of a Python CLI via uv (2026)

Yes. Official model: [Using tools](https://docs.astral.sh/uv/guides/tools/), [Tools concept](https://docs.astral.sh/uv/concepts/tools/).

| Intent | Command |
| --- | --- |
| One-shot, no persistent install | `uvx <pkg>` ≡ `uv tool run <pkg>` |
| Persistent on PATH | `uv tool install <pkg>` then the console script |
| Version pin | `uvx [email protected]` or `--from 'pkg==x'` |
| Git instead of PyPI | `uvx --from git+https://github.com/org/repo <cmd>` |
| Python floor at run | `uvx --python 3.11 <cmd>` |
| Extra data/deps | `--with` |

`uvx` installs into a **temporary isolated** env (cached, disposable). `uv tool install` uses a persistent tool env; executables are console/script entry points **from that package**, not from its dependencies. `uvx` is **not** `uv run` in a project (that one sees project deps).

If the **command name ≠ package name**, use `--from`: `uvx --from httpie http`.

If a package has **no** `[project.scripts]` (or equivalent) entry for the invoked name, `uvx <name>` will not find a CLI. uv installs “all executables provided by the tool” on `uv tool install`.

### pyproject layout that produces a CLI

Standards: [Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [uv project config / scripts](https://docs.astral.sh/uv/concepts/projects/config/).

```toml
[build-system]
requires = ["hatchling >= 1.26"]  # or setuptools, uv_build, …
build-backend = "hatchling.build"

[project]
name = "<pypi-name>"          # required; unique on PyPI
version = "0.1.0"
requires-python = ">=3.11"    # example floor; not a uv requirement
dependencies = []

[project.scripts]
spine = "pkg.cli:main"        # console script name → callable
```

`[project.scripts]` requires a **build backend** (`[build-system]`). After publish, a stranger does `uvx <pypi-name>` if the script name equals the package name; otherwise `uvx --from <pypi-name> <script>`.

PyPI **name** vs **script** vs **import package** can all differ. Occupancy is on the **distribution name** (`name =`).

### Shipping a contract file + SKILL.md (non-Python)

Wheels do not automatically include arbitrary repo files. Build-backend specific:

**Hatchling** ([build config](https://hatch.pypa.io/1.17/config/build/)): default file selection is package-oriented; VCS-ignored files are omitted unless `artifacts`. Options that apply: `include` / `exclude`, `artifacts`, `force-include` (map a path into the wheel), `packages`. Example pattern (illustrative, not a product choice):

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/spine"]
# force-include maps source → path inside the wheel
[tool.hatch.build.targets.wheel.force-include]
"share/contract" = "spine/data/contract"
"share/skills" = "spine/data/skills"
```

Runtime then uses `importlib.resources` (or `Traversable`) against the installed package, **not** the git checkout.

**setuptools:** `package-data` / `tool.setuptools.package-data` to include `*.md` / contract files **inside** an import package. Files sitting only at repo root are not installed unless listed.

**uv_build** is a supported backend (`uv_build >= 0.12.10, <0.13.0` in PyPUG tables) — file-selection details are in uv’s own backend docs, not re-fetched here.

**Implication for init:** even if SKILL.md is in the wheel, **no harness loads skills from site-packages**. Init must copy/symlink those files into a discovery root (see research 16). The package only has to *contain* the bytes.

### Python version floor

uv will fetch an interpreter matching `--python` / the environment; `requires-python` on the project constrains install. There is no universal 2026 floor from uv itself. A declared `requires-python = ">=3.11"` is a packaging fact the CLI can choose; not observed as a uv limitation.

---

## 2. Is `spine` blocked or confusing on PyPI and GitHub?

### PyPI (JSON API, 2026-09-18)

| Name | Status | Latest | Summary / notes |
| --- | --- | --- | --- |
| `spine` | **taken** | 1.2.4 uploaded **2026-09-16** | “SPINE: Scalable Particle Imaging with Neural Embeddings…” — HEP / DeepLearnPhysics. [pypi.org/project/spine](https://pypi.org/project/spine/) |
| `spine-engine` | **taken** | 0.26.8 uploaded 2026-09-10 | “A package to run Spine workflows.” VTT-adjacent workflow engine, **not** this product. [pypi.org/project/spine-engine](https://pypi.org/project/spine-engine/) |
| `spine-cli` | 404 | — | not registered |
| `spine-tools` | 404 | — | not registered as a PyPI *project* (org/name collision still exists on GitHub) |
| `process-spine` | 404 | — | not registered |
| `harness-spine` | 404 | — | not registered |

`uvx spine` today would install **DeepLearnPhysics’ HEP package**, not an empty name. That is a **hard occupancy** for the exact distribution name `spine`.

PyPI name comparison is case-insensitive and treats `-` `_` `.` runs as equal (PEP 503 / PyPUG `name` rules). `Spine`, `python-spine` vs `spine` are different if not equivalent under normalization; `spine` and `Spine` are the same project.

### GitHub (search `spine in:name`, 2026-09-18)

The identifier `spine` is widely used. High-signal collisions:

| Repo / org | What it is | Activity |
| --- | --- | --- |
| [github.com/spine](https://github.com/spine) org; [spine/spine](https://github.com/spine/spine) | JS MVC library (“Spine JS Project”), org created 2013 | last **push 2020-04-04**; repo still updated metadata 2026-09-16 |
| [EsotericSoftware/spine-runtimes](https://github.com/EsotericSoftware/spine-runtimes) | 2D skeletal animation (the dominant “Spine” in games) | **push 2026-09-17** |
| [Cacti/spine](https://github.com/Cacti/spine) | C poller for Cacti | **push 2026-09-18** |
| [DeepLearnPhysics/spine](https://github.com/DeepLearnPhysics/spine) | same HEP project as PyPI `spine` | **push 2026-09-18** |
| [pixijs-userland/spine](https://github.com/pixijs-userland/spine) | Pixi.js Spine plugin | last push 2025-03-24 |
| [synaptixs/spine](https://github.com/synaptixs/spine) | “governed, provenance-grounded autonomous software delivery (installs as agent-orchestrator)” | created 2026-06-26, **push 2026-09-18** — closest *product-category* collision to a process spine |
| [NARUBROWN/spine](https://github.com/NARUBROWN/spine) | “execution-centric backend framework” | push 2026-08-03 |
| User `ASabale/spine` | not in the top search hits | creating `ASabale/spine` is possible; the **org** `spine` is taken |

GitHub repo name `spine` under a personal account is not globally unique and is not blocked by the dormant `spine` org. Search SEO and `uvx spine` / PyPI remain the sharper occupancy problems.

### Confusable (not occupancy)

- Esoteric Software **Spine** (animation) dominates web search for the word.
- VTT **Spine Toolbox** / `spine-engine` is already a “workflows” Python stack.
- `synaptixs/spine` is an agent-orchestrator in the same year.

---

## Facts a naming ticket can use

- A stranger **can** run a published Python CLI with `uvx` / `uv tool install` in 2026; layout is `pyproject.toml` + `[project.scripts]` + a build backend; data files must be **explicitly** included in the wheel and then **copied by init** into harness skill roots.
- The **exact PyPI name `spine` is taken** by an active HEP package (upload 2026-09-16). `uvx spine` is therefore not a vacant command.
- Several hyphenated names (`spine-cli`, `process-spine`, `harness-spine`) returned 404 on PyPI this day; they can still collide later.
- GitHub: org `spine` taken; many repos named `spine`; Esoteric Spine + Cacti + HEP + 2026 agent-orchestrator `synaptixs/spine` are the confusion set. A personal `ASabale/<name>` slug is a separate decision from PyPI `name =`.
