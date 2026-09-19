from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import yaml

from spine.initcmd import init_target
from spine.resources import read_data


def _npx() -> str | None:
    return shutil.which("npx")


def load_wires(root: Path) -> dict:
    path = root / "docs/spine/wires.yaml"
    text = path.read_text(encoding="utf-8") if path.exists() else read_data("wires.yaml")
    return yaml.safe_load(text) or {}


def install_cmd(pack: str, skills: list[str], npx: str = "npx") -> list[str]:
    cmd = [npx, "--yes", "skills", "add", pack, "-y"]
    seen: set[str] = set()
    for name in skills:
        if name and name not in seen:
            seen.add(name)
            cmd.extend(["-s", name])
    return cmd


def skills_for_pack(wires: dict, pack: str) -> list[str]:
    names: list[str] = []
    for spec in (wires.get("concerns") or {}).values():
        if not isinstance(spec, dict):
            continue
        if spec.get("pack") != pack:
            continue
        names.extend(spec.get("skills") or [])
    return names


def install_wires(root: Path, *, extra_pack: str | None = None) -> list[str]:
    notes: list[str] = []
    npx = _npx()
    wires = load_wires(root)
    pack = extra_pack or wires.get("default_pack") or "mattpocock/skills"
    skills = skills_for_pack(wires, pack)
    if not npx:
        notes.append(
            "npx not found; skip craft install. Binder skills are already copied. "
            f"Run: {' '.join(install_cmd(pack, skills))}"
        )
        return notes
    cmd = install_cmd(pack, skills, npx)
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    notes.append(f"$ {' '.join(cmd)} exit={proc.returncode}")
    if proc.stdout:
        notes.append(proc.stdout[-2000:])
    if proc.returncode != 0 and proc.stderr:
        notes.append(proc.stderr[-1000:])
    return notes


def evolve(root: Path) -> list[str]:
    notes = init_target(root, refresh=True)
    npx = _npx()
    if npx:
        proc = subprocess.run([npx, "--yes", "skills", "update"], cwd=root, capture_output=True, text=True)
        notes.append(f"skills update exit={proc.returncode}")
        if proc.stdout:
            notes.append(proc.stdout[-1500:])
    else:
        notes.append("npx not found; refreshed binder from wheel only")
    return notes


def set_pack(root: Path, pack: str) -> None:
    path = root / "docs/spine/wires.yaml"
    text = path.read_text(encoding="utf-8") if path.exists() else read_data("wires.yaml")
    lines = []
    replaced = False
    for line in text.splitlines():
        if line.startswith("default_pack:"):
            lines.append(f"default_pack: {pack}")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        lines.insert(0, f"default_pack: {pack}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
