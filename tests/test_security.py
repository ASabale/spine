from pathlib import Path

import pytest

from spine.artifacts import new_ticket, resolve_artifact
from spine.evolve import install_cmd, install_wires
from spine.initcmd import init_target


def test_resolve_rejects_symlink_escape(tmp_path: Path):
    init_target(tmp_path)
    new_ticket(tmp_path, "Inside")
    outside = tmp_path / "outside.md"
    outside.write_text("secret\n", encoding="utf-8")
    link = tmp_path / "docs/spine/tickets/evil.md"
    link.symlink_to(outside)
    with pytest.raises(FileNotFoundError):
        resolve_artifact(tmp_path, str(link))
    with pytest.raises(FileNotFoundError):
        resolve_artifact(tmp_path, "evil")


def test_new_ticket_slug_cannot_escape(tmp_path: Path):
    init_target(tmp_path)
    path = new_ticket(tmp_path, "../../etc/passwd")
    assert path.parent.name == "tickets"
    assert ".." not in path.name
    assert path.is_file()
    assert path.resolve().is_relative_to((tmp_path / "docs/spine").resolve())


def test_install_cmd_is_argv_list():
    cmd = install_cmd("mattpocock/skills", ["tdd"])
    assert cmd[0] == "npx"
    assert all(isinstance(x, str) for x in cmd)
    assert "-s" in cmd


def test_no_shell_true_in_product():
    import inspect

    import spine.artifacts as artifacts
    import spine.evolve as evolve

    assert "shell=True" not in inspect.getsource(evolve)
    assert "shell=True" not in inspect.getsource(artifacts)
    assert inspect.getsource(install_wires).count("subprocess.run") >= 1
