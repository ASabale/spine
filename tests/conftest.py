import pytest


@pytest.fixture(autouse=True)
def spine_human(monkeypatch):
    monkeypatch.setenv("SPINE_HUMAN", "1")
