"""schema-forge CLI.

Four subcommands, mapped to the workflow in docs/schema_forge_plan.md §3:

    init               scaffold an engagement directory (EPIC C)
    extract-overrides  LLM-normalize interviews into override YAML (EPIC D)
    generate           deterministic merge baseline + overrides -> output (EPIC E)
    validate           sanity battery over the generated output (EPIC F)

This module ships the argument surface and dispatch. Each command currently
delegates to a stub that exits non-zero until its epic lands; later epics
replace the stub body, not the CLI wiring.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_NOT_IMPLEMENTED = 2


def _stub(command: str, epic: str) -> int:
    print(
        f"schema-forge {command}: not implemented yet (tracked by {epic}).",
        file=sys.stderr,
    )
    return _NOT_IMPLEMENTED


def cmd_init(args: argparse.Namespace) -> int:
    return _stub("init", "EPIC C")


def cmd_extract_overrides(args: argparse.Namespace) -> int:
    return _stub("extract-overrides", "EPIC D")


def cmd_generate(args: argparse.Namespace) -> int:
    return _stub("generate", "EPIC E")


def cmd_validate(args: argparse.Namespace) -> int:
    return _stub("validate", "EPIC F")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schema-forge",
        description="Generate the five spine artifacts from a domain baseline + buyer overrides.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="scaffold an engagement directory")
    p_init.add_argument("--domain", required=True, help="domain key, e.g. 'gtm'")
    p_init.add_argument("--client", required=True, help="client slug, e.g. 'ai-consulting-firm'")
    p_init.add_argument("--output", required=True, type=Path, help="engagement directory to create")
    p_init.set_defaults(func=cmd_init)

    p_over = sub.add_parser("extract-overrides", help="LLM-normalize interviews into override YAML")
    p_over.add_argument("--engagement", required=True, type=Path, help="engagement directory")
    p_over.set_defaults(func=cmd_extract_overrides)

    p_gen = sub.add_parser("generate", help="deterministic merge baseline + overrides -> output")
    p_gen.add_argument("--engagement", required=True, type=Path, help="engagement directory")
    p_gen.set_defaults(func=cmd_generate)

    p_val = sub.add_parser("validate", help="sanity battery over the generated output")
    p_val.add_argument("--engagement", required=True, type=Path, help="engagement directory")
    p_val.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
