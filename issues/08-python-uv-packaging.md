# Python uv packaging

Type: grilling
Status: resolved
Blocked by: 01, 17

## Question

How is the CLI packaged so a stranger runs it with uv (`uvx <name>` or `uv tool install`)? Python version floor, package name (follows [Name the public toolkit](01-name-the-toolkit.md)), entrypoint, whether the contract file and binder skills ship inside the package.

Use [Packaging and name](17-packaging-and-name.md).

Recommended: Python 3.11+, package name = product name, console script `spine`, data files include `contract` + binder `SKILL.md`. Stranger does not clone this repo to work in a target.

## Answer

Python **3.11+**. Distribution name **spine-cli**. Console script **spine** (`[project.scripts]`). Build backend ships **contract** + binder **SKILL.md** as package data (`importlib.resources`); init copies skills into harness discovery roots. Stranger install: `uvx --from spine-cli spine` or `uv tool install spine-cli` then `spine`. Does not clone this repo. Does not fetch skills from GitHub at init.
