import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRD = ROOT / "scripts/ralph/prd.json"


def test_ralph_prd_stories_are_small_and_checkable():
    data = json.loads(PRD.read_text(encoding="utf-8"))
    assert data["project"] == "spine"
    stories = data["userStories"]
    assert stories
    for story in stories:
        assert story["id"].startswith("US-")
        assert story["title"]
        assert isinstance(story["priority"], int)
        assert isinstance(story["passes"], bool)
        criteria = story["acceptanceCriteria"]
        assert 2 <= len(criteria) <= 8
        joined = " ".join(criteria).lower()
        assert "pytest" in joined or "tests" in joined
        assert len(story["title"].split()) <= 12
