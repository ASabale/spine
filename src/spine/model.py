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


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Contract:
    raw: dict
    source: str = "packaged"

    def __post_init__(self) -> None:
        self.validate()

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

    @property
    def ticket_statuses(self) -> list[str]:
        return list(self.raw["tickets"]["statuses"])

    @property
    def ticket_transitions(self) -> dict[str, list[str]]:
        return {k: list(v) for k, v in self.raw["tickets"]["transitions"].items()}

    def ticket_allowed(self, current: str, nxt: str) -> bool:
        return nxt in self.ticket_transitions.get(current, [])

    def validate(self) -> None:
        raw = self.raw
        if not isinstance(raw, dict):
            raise ContractError("contract must be a mapping")
        statuses = raw.get("statuses")
        if not isinstance(statuses, list) or not statuses or not all(isinstance(s, str) and s for s in statuses):
            raise ContractError("statuses must be a non-empty list of strings")
        status_set = set(statuses)
        transitions = raw.get("transitions")
        if not isinstance(transitions, dict):
            raise ContractError("transitions must be a mapping")
        for src, dests in transitions.items():
            if src not in status_set:
                raise ContractError(f"unknown transition source {src}")
            if not isinstance(dests, list) or not all(isinstance(d, str) for d in dests):
                raise ContractError(f"transitions[{src}] must be a list of strings")
            for dest in dests:
                if dest not in status_set:
                    raise ContractError(f"unknown transition target {dest}")
        missing = [s for s in statuses if s not in transitions]
        if missing:
            raise ContractError(f"status missing from transitions: {missing}")
        required = ((raw.get("profiles") or {}).get("software") or {}).get("required_before_done") or []
        if not isinstance(required, list):
            raise ContractError("profiles.software.required_before_done must be a list")
        for item in required:
            if item not in status_set:
                raise ContractError(f"required_before_done unknown status {item}")
        hours = (raw.get("claim") or {}).get("stale_hours")
        if not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
            raise ContractError("claim.stale_hours must be a positive int")
        try:
            int(raw.get("version"))
        except (TypeError, ValueError):
            raise ContractError("version must be an int") from None
        tickets = raw.get("tickets")
        if not isinstance(tickets, dict):
            raise ContractError("tickets must be a mapping")
        t_statuses = tickets.get("statuses")
        if not isinstance(t_statuses, list) or not t_statuses or not all(isinstance(s, str) and s for s in t_statuses):
            raise ContractError("tickets.statuses must be a non-empty list of strings")
        t_status_set = set(t_statuses)
        t_transitions = tickets.get("transitions")
        if not isinstance(t_transitions, dict):
            raise ContractError("tickets.transitions must be a mapping")
        for src, dests in t_transitions.items():
            if src not in t_status_set:
                raise ContractError(f"unknown ticket transition source {src}")
            if not isinstance(dests, list) or not all(isinstance(d, str) for d in dests):
                raise ContractError(f"tickets.transitions[{src}] must be a list of strings")
            for dest in dests:
                if dest not in t_status_set:
                    raise ContractError(f"unknown ticket transition target {dest}")
        t_missing = [s for s in t_statuses if s not in t_transitions]
        if t_missing:
            raise ContractError(f"ticket status missing from transitions: {t_missing}")

    def software_required(self) -> list[str]:
        return list(self.raw["profiles"]["software"]["required_before_done"])

    def next_gates(self, current: str, *, software: bool = True) -> list[str]:
        nxt = list(self.transitions.get(current, []))
        if current == "doing" and not software:
            if "done" not in nxt:
                nxt.append("done")
        return nxt


def _from_text(text: str, source: str) -> Contract:
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ContractError(f"invalid contract YAML: {exc}") from exc
    return Contract(raw, source=source)


def packaged_contract() -> Contract:
    return _from_text(read_data("contract.yaml"), "packaged")


def load_contract(root: Path | None = None) -> Contract:
    if root is not None:
        path = root / SPEC_ROOT / "contract.yaml"
        if path.exists():
            return _from_text(path.read_text(encoding="utf-8"), str(path))
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
