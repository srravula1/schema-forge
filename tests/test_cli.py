"""CLI tests: all four subcommands parse and behave correctly."""

import pytest

from forge.cli import build_parser, main

SUBCOMMANDS = ["init", "extract-overrides", "generate", "validate"]


def test_all_subcommands_registered():
    parser = build_parser()
    actions = [a for a in parser._actions if a.dest == "command"]
    assert actions, "no subparsers registered"
    assert set(SUBCOMMANDS).issubset(set(actions[0].choices))


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_validate_nonexistent_engagement_exits_nonzero():
    # validate is implemented (EPIC F); nonexistent engagement dir → nonzero.
    assert main(["validate", "--engagement", "/tmp/__schema_forge_no_such_dir__"]) != 0


def test_generate_nonexistent_engagement_exits_nonzero():
    # generate is implemented (EPIC E); nonexistent engagement dir → nonzero.
    assert main(["generate", "--engagement", "/tmp/__schema_forge_no_such_dir__"]) != 0


def test_extract_overrides_nonexistent_dir_exits_nonzero():
    # extract-overrides is implemented (EPIC D); nonexistent engagement → nonzero.
    assert main(["extract-overrides", "--engagement", "/tmp/__schema_forge_no_such_dir__"]) != 0


def test_missing_required_arg_errors():
    with pytest.raises(SystemExit) as exc:
        main(["init"])  # missing --domain/--client/--output
    assert exc.value.code != 0
