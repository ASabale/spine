from __future__ import annotations

import shutil
from pathlib import Path

from spine.model import EXEC_DIRS, EXEC_ROOT, HARNESS_SKILL_ROOTS, SPEC_DIRS, SPEC_ROOT
from spine.resources import data_root, read_data

README = """# spine artifacts

Sit-down in this directory:

```
spine prime
```

Humans can run `spine doctor` then `spine next` / `spine status`. The `## Next` block is the next command. CLI owns status, owner, claim, links, numbers. Agents own content.

Checked-in **spec tier** (this tree):

- `maps/` — planning maps (index only)
- `tickets/` — map tickets (`NN-slug.md`)
- `work-items/` — execution work items
- `decisions/` — durable decisions
- `wires.yaml` — binder concern → skills.sh craft skills
- `contract.yaml` — statuses and transitions (do not restate in skills)

Checked-in **proofs** live in `.spine/evals/` and `.spine/reviews/` so a clone can verify the gates. The rest of `.spine/` stays gitignored (`handoffs`, `doctor`, `claims`, `events.jsonl`, `coord.db`, `migrate`).

Craft: `spine wire --install` (skills.sh). Bodies are not vendored here.
"""

GITIGNORE_BLOCK = """# spine execution tier
.spine/*
!.spine/evals/
!.spine/reviews/
"""


def _ensure_gitignore(text: str) -> str:
    """Ignore runtime files under `.spine/` and keep eval and review YAML."""
    lines = text.splitlines()
    stripped = [ln.strip() for ln in lines]
    complete = (
        ".spine/*" in stripped
        and "!.spine/evals/" in stripped
        and "!.spine/reviews/" in stripped
        and ".spine/" not in stripped
    )
    if complete:
        return text if text.endswith("\n") or text == "" else text + "\n"
    owned = {
        "# spine execution tier",
        ".spine/",
        ".spine/*",
        "!.spine/evals/",
        "!.spine/reviews/",
    }
    kept = [ln for ln in lines if ln.strip() not in owned]
    block = GITIGNORE_BLOCK.strip("\n")
    base = "\n".join(kept).rstrip()
    if base:
        return base + "\n" + block + "\n"
    return block + "\n"

MAP = """# Map

## Destination

## Notes

## Decisions so far

## Not yet specified

## Out of scope
"""


def _copy_tree(src: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dest / item.name
        if item.is_dir():
            _copy_tree(item, target)
        else:
            shutil.copy2(item, target)


def init_target(root: Path, *, refresh: bool = False) -> list[str]:
    notes: list[str] = []
    for name in SPEC_DIRS:
        p = root / SPEC_ROOT / name
        p.mkdir(parents=True, exist_ok=True)
        notes.append(f"ensure {p.relative_to(root)}")
    for name in EXEC_DIRS:
        p = root / EXEC_ROOT / name
        p.mkdir(parents=True, exist_ok=True)
        notes.append(f"ensure {p.relative_to(root)}")

    readme = root / SPEC_ROOT / "README.md"
    if refresh or not readme.exists():
        readme.write_text(README, encoding="utf-8")
        notes.append("wrote docs/spine/README.md")

    wires = root / SPEC_ROOT / "wires.yaml"
    if refresh or not wires.exists():
        wires.write_text(read_data("wires.yaml"), encoding="utf-8")
        notes.append("wrote docs/spine/wires.yaml")

    contract = root / SPEC_ROOT / "contract.yaml"
    if refresh or not contract.exists():
        contract.write_text(read_data("contract.yaml"), encoding="utf-8")
        notes.append("wrote docs/spine/contract.yaml")

    mapp = root / SPEC_ROOT / "maps" / "map.md"
    if not mapp.exists():
        mapp.write_text(MAP, encoding="utf-8")
        notes.append("wrote docs/spine/maps/map.md")

    gi = root / ".gitignore"
    existing = gi.read_text(encoding="utf-8") if gi.exists() else ""
    updated = _ensure_gitignore(existing)
    if updated != existing:
        gi.write_text(updated, encoding="utf-8")
        notes.append("updated .gitignore")

    binder_src = data_root() / "binder"
    for harness in HARNESS_SKILL_ROOTS:
        dest = root / harness
        dest.mkdir(parents=True, exist_ok=True)
        if refresh or not any(dest.glob("*/SKILL.md")):
            _copy_tree(binder_src, dest)
            notes.append(f"copied binder → {harness}")
        else:
            for skill_dir in binder_src.iterdir():
                target = dest / skill_dir.name
                _copy_tree(skill_dir, target)
            notes.append(f"refreshed binder → {harness}")
    return notes
