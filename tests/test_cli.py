"""CLI skeleton: all four subcommands parse; stubs exit non-zero until their epic lands."""

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


@pytest.mark.parametrize(
    "argv",
    [
        # init is implemented (EPIC C1); remaining three are stubs
        ["extract-overrides", "--engagement", "/tmp/x"],
        ["generate", "--engagement", "/tmp/x"],
        ["validate", "--engagement", "/tmp/x"],
    ],
)
def test_stub_commands_exit_nonzero(argv):
    assert main(argv) != 0


def test_missing_required_arg_errors():
    with pytest.raises(SystemExit) as exc:
        main(["init"])  # missing --domain/--client/--output
    assert exc.value.code != 0
