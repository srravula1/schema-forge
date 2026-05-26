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
from typing import Any

import yaml

_NOT_IMPLEMENTED = 2

# Header written at the top of every proposed override file (Story D3).
_PROPOSED_HEADER = "# PROPOSED — review before generate\n"

# Interview files to read, in order, mapped to the override target they feed.
_INTERVIEW_TARGETS: list[tuple[str, str]] = [
    ("02_icp_interview.md", "icp"),
    ("03_channel_interview.md", "channel"),
    ("04_qualification_interview.md", "policy"),
    ("05_failure_modes_interview.md", "modifier"),
]

# Override file names for each target.
_TARGET_FILES: dict[str, str] = {
    "icp": "icp_overrides.yaml",
    "channel": "channel_overrides.yaml",
    "modifier": "modifier_overrides.yaml",
    "policy": "policy_overrides.yaml",
}


def _stub(command: str, epic: str) -> int:
    print(
        f"schema-forge {command}: not implemented yet (tracked by {epic}).",
        file=sys.stderr,
    )
    return _NOT_IMPLEMENTED


def cmd_init(args: argparse.Namespace) -> int:
    return _stub("init", "EPIC C")


def cmd_extract_overrides(
    args: argparse.Namespace,
    *,
    _normalizer: Any = None,
) -> int:
    """LLM-normalize interview answers into proposed override YAML (EPIC D).

    Story D2: reads ``01_interview_inputs/*.md``, calls the normalizer, and
    writes structured YAML into ``03_overrides/``.

    Story D3: every written file carries a ``# PROPOSED — review before generate``
    header and a ``_source_snippet`` field with the interview excerpt that produced
    each override.  The command prints an instruction to review before running
    ``generate``.

    The normalizer is injectable for tests; production uses AnthropicNormalizer.
    """
    from forge.normalizer import AnthropicNormalizer
    from forge.overrides import (
        IcpOverrides,
        ChannelOverrides,
        ModifierOverrides,
        PolicyOverrides,
        check_label_refs,
        load_overrides,
    )

    engagement = args.engagement.resolve()
    interviews_dir = engagement / "01_interview_inputs"
    overrides_dir = engagement / "03_overrides"

    if not engagement.is_dir():
        print(
            f"extract-overrides: engagement directory not found: {engagement}",
            file=sys.stderr,
        )
        return 1

    if not interviews_dir.is_dir():
        print(
            f"extract-overrides: 01_interview_inputs/ not found in {engagement}",
            file=sys.stderr,
        )
        return 1

    overrides_dir.mkdir(parents=True, exist_ok=True)

    normalizer = _normalizer if _normalizer is not None else AnthropicNormalizer()

    _model_map = {
        "icp": IcpOverrides,
        "channel": ChannelOverrides,
        "modifier": ModifierOverrides,
        "policy": PolicyOverrides,
    }

    for interview_filename, target in _INTERVIEW_TARGETS:
        interview_path = interviews_dir / interview_filename
        if not interview_path.exists():
            print(
                f"  [skip] {interview_filename} not found — skipping {target} overrides",
            )
            continue

        interview_text = interview_path.read_text()
        print(f"  [normalize] {interview_filename} → {_TARGET_FILES[target]}")

        proposed: dict[str, Any] = normalizer.propose(interview_text, target)

        # Validate the proposed dict against the D1 schema before writing.
        model_cls = _model_map[target]
        validated = model_cls.model_validate(proposed)

        # Build the YAML document with a source snippet (Story D3).
        out_dict = validated.model_dump(exclude_none=True)

        # Attach the source snippet at the top level so reviewers can trace it.
        # We take the first 500 chars of the interview as the snippet.
        snippet = interview_text.strip()[:500].replace("\n", " ")
        out_dict["_source_snippet"] = snippet
        out_dict["reviewed"] = False

        out_path = overrides_dir / _TARGET_FILES[target]
        yaml_body = yaml.dump(out_dict, allow_unicode=True, sort_keys=False, default_flow_style=False)
        out_path.write_text(_PROPOSED_HEADER + yaml_body)

    # Validate label references in what we just wrote.
    try:
        bundle = load_overrides(overrides_dir)
        label_errors = check_label_refs(bundle)
        if label_errors:
            print("  [warn] label reference errors:", file=sys.stderr)
            for err in label_errors:
                print(f"    - {err}", file=sys.stderr)
    except Exception as exc:
        print(f"  [warn] could not validate overrides: {exc}", file=sys.stderr)

    print(
        "\nProposed overrides written to:\n"
        f"  {overrides_dir}\n\n"
        "NEXT STEP: Review and edit the files in 03_overrides/ before running:\n"
        "  schema-forge generate --engagement <dir>"
    )
    return 0


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
