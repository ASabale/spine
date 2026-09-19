from pathlib import Path

from spine.resources import data_root


def test_binder_next_mentions_prime():
    text = (data_root() / "binder/next/SKILL.md").read_text(encoding="utf-8")
    assert text.lstrip().startswith("---")
    desc = text.split("description:", 1)[1].split("\n", 1)[0].strip()
    assert desc[0].isupper() or desc[0].islower()
    assert desc.split()[0][0].isalpha()
    assert "Pick" in desc.split(".")[0] or desc.split()[0][0].isupper()
    assert "spine prime" in text


def test_agents_md_sitdown_is_prime():
    text = Path("AGENTS.md").read_text(encoding="utf-8")
    session = text.split("## Every session", 1)[1].split("## ", 1)[0]
    assert "spine prime" in session
