"""Scaffold an engagement directory for schema-forge init (EPIC C1).

Entry point: init_engagement(domain, client, output) -> None.
Raises ValueError for invalid inputs; raises FileExistsError if output is non-empty.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

VALID_DOMAINS = {"gtm"}

_FORGE_DIR = Path(__file__).parent

_TEMPLATES_DIR = _FORGE_DIR / "templates"
_INTERVIEW_TEMPLATES = [
    "01_company_overview.md",
    "02_icp_interview.md",
    "03_channel_interview.md",
    "04_qualification_interview.md",
    "05_failure_modes_interview.md",
    "06_gold_records.md",
    "INTERVIEW_PLAYBOOK.md",
]

_GOLD_CSV_HEADER = (
    "record_id,company_name,company_size_employees,industry,contact_title,"
    "contact_seniority,deal_source,disposition,disposition_reason,raw_notes\n"
)

_ICP_OVERRIDES_YAML = """\
# icp_overrides.yaml — filled in by extract-overrides (EPIC D)
# Narrows the valid value space for account-family labels.
# Example:
# A_EMPLOYEE_RANGE:
#   include: ["11-50", "51-200"]
#   exclude: ["1-10", "201-1000", "1001-5000", "5000+"]
#   rationale: "..."
"""

_CHANNEL_OVERRIDES_YAML = """\
# channel_overrides.yaml — filled in by extract-overrides (EPIC D)
# Adds engagement family weights and new signal definitions.
# Example:
# signal_weights:
#   S_HIRING_TRIGGER: 0.3
#   S_PAIN_POINT_MENTION: 0.9
# custom_signals:
#   - name: S_EXAMPLE
#     definition: "..."
#     rationale: "..."
#     add_to_schema: true
"""

_MODIFIER_OVERRIDES_YAML = """\
# modifier_overrides.yaml — filled in by extract-overrides (EPIC D)
# Adds or restricts modifier-ontology entries.
# Example:
# intent_topics:
#   add:
#     - "LLM evaluation"
#   deprioritize:
#     - "data warehouse migration"
"""

_POLICY_OVERRIDES_YAML = """\
# policy_overrides.yaml — filled in by extract-overrides (EPIC D)
# Buyer-specific qualification rules layered on the baseline policy.
# Example:
# disqualification_rules:
#   - condition: "A_EMPLOYEE_RANGE in [1-10]"
#     rationale: "..."
# auto_pass_rules:
#   - condition: "Q_BUDGET_CONFIRMED AND Q_AUTHORITY_IDENTIFIED AND confidence > 0.7"
#     rationale: "..."
"""


def _baseline_dir(domain: str) -> Path:
    return _FORGE_DIR / "domains" / domain / "baseline"


def init_engagement(domain: str, client: str, output: Path) -> None:
    if domain not in VALID_DOMAINS:
        raise ValueError(
            f"Unknown domain {domain!r}. Valid domains: {sorted(VALID_DOMAINS)}"
        )

    output = output.resolve()

    if output.exists() and any(output.iterdir()):
        raise FileExistsError(
            f"Output directory {output} is non-empty. "
            "Remove it or choose a different path to avoid clobbering."
        )

    output.mkdir(parents=True, exist_ok=True)

    _create_interview_inputs(output)
    _copy_baseline(domain, output)
    _create_overrides(output)
    _create_output_dir(output)
    _write_manifest(domain, client, output)


def _create_interview_inputs(output: Path) -> None:
    dest = output / "01_interview_inputs"
    dest.mkdir()
    for name in _INTERVIEW_TEMPLATES:
        src = _TEMPLATES_DIR / name
        if src.exists():
            shutil.copy2(src, dest / name)
    (dest / "06_gold_records.csv").write_text(_GOLD_CSV_HEADER, encoding="utf-8")


def _copy_baseline(domain: str, output: Path) -> None:
    src = _baseline_dir(domain)
    dest = output / "02_baseline"
    dest.mkdir()

    for item in src.iterdir():
        if item.name == "__init__.py" or item.name.startswith("_gen_"):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(item, dest / item.name)


def _create_overrides(output: Path) -> None:
    dest = output / "03_overrides"
    dest.mkdir()
    (dest / "icp_overrides.yaml").write_text(_ICP_OVERRIDES_YAML, encoding="utf-8")
    (dest / "channel_overrides.yaml").write_text(_CHANNEL_OVERRIDES_YAML, encoding="utf-8")
    (dest / "modifier_overrides.yaml").write_text(_MODIFIER_OVERRIDES_YAML, encoding="utf-8")
    (dest / "policy_overrides.yaml").write_text(_POLICY_OVERRIDES_YAML, encoding="utf-8")
    (dest / "failure_mode_additions").mkdir()


def _create_output_dir(output: Path) -> None:
    (output / "04_output").mkdir()


def _write_manifest(domain: str, client: str, output: Path) -> None:
    manifest = {
        "domain": domain,
        "client": client,
        "baseline_version": f"{domain}_v2.0",
        "generated_at": None,
        "overrides": {},
        "output": {
            "schema": None,
            "changes_from_baseline": [],
        },
    }
    manifest_path = output / "manifest.yaml"
    manifest_path.write_text(
        yaml.dump(manifest, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
