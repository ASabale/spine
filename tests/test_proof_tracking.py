import subprocess
from pathlib import Path

from spine.doctor import doctor
from spine.initcmd import init_target


def _ignored(root: Path, rel: str) -> bool:
    proc = subprocess.run(
        ["git", "check-ignore", "-q", "--", rel],
        cwd=root,
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0


def test_init_tracks_eval_and_review_yaml(tmp_path: Path):
    init_target(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / ".spine/evals/item.md").write_text("passed: true\n", encoding="utf-8")
    (tmp_path / ".spine/reviews/item.md").write_text("verdict: approve\n", encoding="utf-8")
    (tmp_path / ".spine/claims").mkdir(exist_ok=True)
    (tmp_path / ".spine/claims/item.claim").write_text("ada\n", encoding="utf-8")
    (tmp_path / ".spine/coord.db").write_bytes(b"not a database")
    (tmp_path / ".spine/events.jsonl").write_text("{}\n", encoding="utf-8")
    assert not _ignored(tmp_path, ".spine/evals/item.md")
    assert not _ignored(tmp_path, ".spine/reviews/item.md")
    assert _ignored(tmp_path, ".spine/coord.db")
    assert _ignored(tmp_path, ".spine/claims/item.claim")
    assert _ignored(tmp_path, ".spine/events.jsonl")


def test_init_upgrades_a_directory_ignore(tmp_path: Path):
    (tmp_path / ".gitignore").write_text("dist/\n.spine/\n", encoding="utf-8")
    init_target(tmp_path)
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "dist/" in text
    assert all(line.strip() != ".spine/" for line in text.splitlines())
    assert ".spine/*" in text
    assert "!.spine/evals/" in text
    assert "!.spine/reviews/" in text
    init_target(tmp_path)
    assert (tmp_path / ".gitignore").read_text(encoding="utf-8") == text


def test_doctor_reports_hidden_proofs_without_editing(tmp_path: Path):
    init_target(tmp_path)
    gi = tmp_path / ".gitignore"
    gi.write_text("# spine execution tier\n.spine/\n", encoding="utf-8")
    msgs = doctor(tmp_path, apply=True)
    assert any("hides .spine/evals and .spine/reviews" in m for m in msgs)
    assert gi.read_text(encoding="utf-8") == "# spine execution tier\n.spine/\n"
