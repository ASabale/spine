from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from spine.resources import read_data

SPEC_ROOT = Path("docs/spine")
EXEC_ROOT = Path(".spine")
SPEC_DIRS = ("maps", "tickets", "work-items", "decisions")
EXEC_DIRS = ("evals", "reviews", "handoffs", "doctor", "claims")
HARNESS_SKILL_ROOTS = (
    Path(".agents/skills"),
    Path(".claude/skills"),
    Path(".cursor/skills"),
)
TICKET_STATUSES = {"open", "claimed", "resolved"}


@dataclass(frozen=True)
class Contract:
    raw: dict
    source: str = "packaged"

    @property
    def version(self) -> int:
        return int(self.raw["version"])

    @property
    def statuses(self) -> list[str]:
        return list(self.raw["statuses"])

    @property
    def transitions(self) -> dict[str, list[str]]:
        return {k: list(v) for k, v in self.raw["transitions"].items()}

    @property
    def stale_hours(self) -> int:
        return int(self.raw["claim"]["stale_hours"])

    def allowed(self, current: str, nxt: str) -> bool:
        return nxt in self.transitions.get(current, [])

    def software_required(self) -> list[str]:
        return list(self.raw["profiles"]["software"]["required_before_done"])

    def next_gates(self, current: str, *, software: bool = True) -> list[str]:
        nxt = list(self.transitions.get(current, []))
        if current == "doing" and not software:
            if "done" not in nxt:
                nxt.append("done")
        return nxt


def packaged_contract() -> Contract:
    return Contract(yaml.safe_load(read_data("contract.yaml")), source="packaged")


def load_contract(root: Path | None = None) -> Contract:
    if root is not None:
        path = root / SPEC_ROOT / "contract.yaml"
        if path.exists():
            return Contract(yaml.safe_load(path.read_text(encoding="utf-8")), source=str(path))
    return packaged_contract()


def parse_front(text: str) -> tuple[dict[str, str], str]:
    """Parse simple `Key: value` header until blank line."""
    lines = text.splitlines()
    meta: dict[str, str] = {}
    i = 0
    if lines and lines[0].startswith("# "):
        meta["Title"] = lines[0][2:].strip()
        i = 1
        if i < len(lines) and lines[i] == "":
            i += 1
    while i < len(lines) and lines[i] != "" and ":" in lines[i] and not lines[i].startswith("#"):
        k, _, v = lines[i].partition(":")
        meta[k.strip()] = v.strip()
        i += 1
    body = "\n".join(lines[i:]).lstrip("\n")
    return meta, body


def dump_front(meta: dict[str, str], body: str, title: str | None = None) -> str:
    title = title or meta.get("Title", "untitled")
    keys = [k for k in meta if k != "Title"]
    header = [f"# {title}", ""]
    for k in keys:
        header.append(f"{k}: {meta[k]}")
    return "\n".join(header) + "\n\n" + body.lstrip("\n")
