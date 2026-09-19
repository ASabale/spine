from pathlib import Path
from unittest.mock import patch

from spine.evolve import evolve, set_pack
from spine.initcmd import README, init_target


def test_set_pack_rewrites_default_pack(tmp_path: Path):
    init_target(tmp_path)
    set_pack(tmp_path, "example/other")
    text = (tmp_path / "docs/spine/wires.yaml").read_text(encoding="utf-8")
    assert "default_pack: example/other" in text
    assert text.count("default_pack:") == 1


def test_evolve_refresh_without_npx(tmp_path: Path):
    init_target(tmp_path)
    binder = tmp_path / ".agents/skills/new/SKILL.md"
    binder.write_text("stale\n", encoding="utf-8")
    with patch("spine.evolve.shutil.which", return_value=None):
        notes = evolve(tmp_path)
    assert any("npx not found" in n for n in notes)
    text = binder.read_text(encoding="utf-8")
    assert "stale" not in text
    assert "spine new" in text


def test_evolve_refresh_restores_repo_readme(tmp_path: Path):
    init_target(tmp_path)
    readme = tmp_path / "docs/spine/README.md"
    readme.write_text("operator edits drifted\n", encoding="utf-8")
    with patch("spine.evolve.shutil.which", return_value=None):
        evolve(tmp_path)
    assert readme.read_text(encoding="utf-8") == README


def test_repo_readme_matches_packaged():
    repo = Path(__file__).resolve().parent.parent / "docs/spine/README.md"
    assert repo.read_text(encoding="utf-8") == README
