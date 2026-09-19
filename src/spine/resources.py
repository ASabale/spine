"""Load packaged data files."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def data_root() -> Path:
    return Path(str(files("spine") / "data"))


def read_data(*parts: str) -> str:
    return (data_root().joinpath(*parts)).read_text(encoding="utf-8")
