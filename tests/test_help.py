from spine.cli import main


def test_help_mentions_sit_down(capsys):
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    out = capsys.readouterr().out
    assert "Sit-down" in out
    assert "doctor" in out
    assert "status" in out
    assert "## Next" in out
    assert "next" in out
    assert "show" in out
    assert "prime" in out
    assert "show" in out
    assert "next" in out
    assert "run" in out
