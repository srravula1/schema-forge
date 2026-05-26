"""Deterministic merge engine (EPIC E): baseline + overrides -> output.

No LLM in this path; identical inputs must produce byte-identical outputs.

Public API
----------
run_generate(engagement_dir, client, now) -> None
    Merge 02_baseline/ + 03_overrides/ and write 04_output/ + manifest.yaml.

Pure merge helpers (no I/O):
    merge_schema(baseline_schema_text, bundle, client) -> str
    merge_modifiers(baseline_modifiers_text, bundle) -> str
    merge_policy(baseline_policy_text, bundle) -> str
    build_manifest(baseline_version, override_files, changes, now) -> dict
"""

from __future__ import annotations

import hashlib
import shutil
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from forge.overrides import ChannelOverrides, IcpOverrides, ModifierOverrides, OverrideBundle, PolicyOverrides, load_overrides


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _slugify(client: str) -> str:
    """Return a safe filename slug for the client name."""
    return client.replace("-", "").replace("_", "").replace(" ", "").lower()


# ---------------------------------------------------------------------------
# Schema merge (Story E2 — icp + channel overrides)
# ---------------------------------------------------------------------------


def merge_schema(baseline_text: str, bundle: OverrideBundle, client: str) -> str:
    """Generate a self-contained schema module from baseline + overrides.

    The output module must:
    - Be self-contained (no spine import, no schema-forge import)
    - Expose GtmLabel, GtmEntity, extraction_guidance(), valid_links()
    - Cover all base labels + custom signals in extraction_guidance()
    """
    slug = _slugify(client)

    # --- Collect ICP guidance additions ---
    icp_additions: dict[str, list[str]] = {}  # label_value -> extra sentences
    icp_disq_comments: list[str] = []

    for label_val, lf in sorted(bundle.icp.filters.items()):
        parts: list[str] = []
        if lf.preferred:
            joined = ", ".join(lf.preferred)
            parts.append(f"For this engagement, preferred values are: {joined}.")
        if lf.include:
            joined = ", ".join(lf.include)
            parts.append(f"Restrict to: {joined}.")
        if lf.exclude:
            joined = ", ".join(lf.exclude)
            parts.append(f"Exclude: {joined}.")
        if parts:
            icp_additions[label_val] = parts
            icp_disq_comments.append(
                f"    # {label_val}: {lf.rationale}"
            )

    # --- Collect custom signals ---
    custom_signals = [
        s for s in bundle.channel.custom_signals if s.add_to_schema
    ]
    custom_signals_sorted = sorted(custom_signals, key=lambda s: s.name)

    # --- Collect signal weights ---
    signal_weights_sorted = sorted(bundle.channel.signal_weights.items())

    # --- Collect policy rules ---
    disq_rules = bundle.policy.disqualification_rules
    auto_pass_rules = bundle.policy.auto_pass_rules
    hil_rules = bundle.policy.hil_rules

    # --- Build the custom label enum entries ---
    custom_enum_lines: list[str] = []
    for sig in custom_signals_sorted:
        val = f"custom.{sig.name.lower()}"
        # enum name: strip leading S_ if present, else use name directly
        enum_name = sig.name
        custom_enum_lines.append(f"    {enum_name} = {val!r}")

    # --- Build extraction_guidance additions for custom signals ---
    custom_guidance_lines: list[str] = []
    for sig in custom_signals_sorted:
        val = f"custom.{sig.name.lower()}"
        custom_guidance_lines.append(
            f"        {val!r}: {sig.definition!r},"
        )

    # --- Build icp guidance additions ---
    icp_guidance_lines: list[str] = []
    for label_val, sentences in sorted(icp_additions.items()):
        extra = " ".join(sentences)
        icp_guidance_lines.append(
            f"    _guidance[{label_val!r}] = _guidance.get({label_val!r}, '') + ' ' + {extra!r}"
        )

    # --- Build disqualification rule comments for policy section ---
    disq_rule_lines: list[str] = []
    for rule in disq_rules:
        disq_rule_lines.append(
            f"    # DISQUALIFY: {rule.condition}\n    # Rationale: {rule.rationale}"
        )
    auto_pass_lines: list[str] = []
    for rule in auto_pass_rules:
        auto_pass_lines.append(
            f"    # AUTO_PASS: {rule.condition}\n    # Rationale: {rule.rationale}"
        )
    hil_rule_lines: list[str] = []
    for rule in hil_rules:
        hil_rule_lines.append(
            f"    # HIL: {rule.condition}\n    # Rationale: {rule.rationale}"
        )

    # --- Signal weight lines ---
    sw_lines: list[str] = []
    for label_val, weight in signal_weights_sorted:
        sw_lines.append(f"    {label_val!r}: {weight!r},")

    has_custom = bool(custom_enum_lines)
    has_icp = bool(icp_guidance_lines)
    has_sw = bool(sw_lines)
    has_disq = bool(disq_rule_lines)
    has_auto = bool(auto_pass_lines)
    has_hil = bool(hil_rule_lines)

    custom_enum_block = ""
    if has_custom:
        custom_enum_block = (
            "\n\n    # --- Custom signals (from channel_overrides) ---\n"
            + "\n".join(custom_enum_lines)
        )

    custom_guidance_block = ""
    if custom_guidance_lines:
        custom_guidance_block = (
            "\n        # Custom signals\n"
            + "\n".join(custom_guidance_lines)
        )

    icp_guidance_block = ""
    if icp_guidance_lines:
        icp_guidance_block = (
            "\n    # ICP overrides — narrow value space\n"
            + "\n".join(icp_guidance_lines)
        )

    sw_block = ""
    if has_sw:
        sw_block = (
            "\n\nSIGNAL_WEIGHTS: dict[str, float] = {\n"
            + "\n".join(sw_lines)
            + "\n}"
        )

    policy_block_parts: list[str] = []
    if has_disq:
        policy_block_parts.append("\n    # --- Disqualification rules ---\n" + "\n".join(disq_rule_lines))
    if has_auto:
        policy_block_parts.append("\n    # --- Auto-pass rules ---\n" + "\n".join(auto_pass_lines))
    if has_hil:
        policy_block_parts.append("\n    # --- HIL rules ---\n" + "\n".join(hil_rule_lines))

    policy_rules_block = ""
    if policy_block_parts:
        policy_rules_block = (
            "\n\ndef client_policy_rules() -> None:\n"
            "    \"\"\"Buyer-specific policy rules (from policy_overrides).\"\"\"\n"
            "    pass"
            + "".join(policy_block_parts)
        )

    # Rebuild the extraction_guidance function to include custom signals + icp additions
    # by appending a call to _apply_client_overrides().
    out = f'''\
"""
gtm_{slug}@v1 — client-specific GTM schema derived from gtm@v1 baseline.

This module is self-contained. No spine or schema-forge imports are needed.
Drop this file into spine/schema/ to integrate.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GtmLabel(str, Enum):
    """GTM label union. Base labels + client-specific custom signals."""

    # --- Account family ---
    A_COMPANY_NAME = "account.company_name"
    A_DOMAIN = "account.domain"
    A_INDUSTRY = "account.industry"
    A_EMPLOYEE_RANGE = "account.employee_range"
    A_REVENUE_RANGE = "account.revenue_range"
    A_HQ_LOCATION = "account.hq_location"
    A_TECH_STACK_ITEM = "account.tech_stack_item"
    A_FUNDING_STAGE = "account.funding_stage"

    # --- Contact family ---
    C_FULL_NAME = "contact.full_name"
    C_TITLE = "contact.title"
    C_SENIORITY = "contact.seniority"
    C_DEPARTMENT = "contact.department"
    C_EMAIL = "contact.email"
    C_LINKEDIN_URL = "contact.linkedin_url"

    # --- Signal family ---
    S_HIRING_TRIGGER = "signal.hiring_trigger"
    S_FUNDING_TRIGGER = "signal.funding_trigger"
    S_TECH_ADOPTION = "signal.tech_adoption"
    S_PAIN_POINT_MENTION = "signal.pain_point_mention"
    S_COMPETITOR_MENTION = "signal.competitor_mention"
    S_INTENT_TOPIC = "signal.intent_topic"

    # --- Engagement family ---
    E_EMAIL_OPEN = "engagement.email_open"
    E_EMAIL_REPLY = "engagement.email_reply"
    E_MEETING_BOOKED = "engagement.meeting_booked"
    E_CALL_TRANSCRIPT_REF = "engagement.call_transcript_ref"
    E_FORM_SUBMIT = "engagement.form_submit"

    # --- Qualification family ---
    Q_BUDGET_CONFIRMED = "qualification.budget_confirmed"
    Q_AUTHORITY_IDENTIFIED = "qualification.authority_identified"
    Q_NEED_ARTICULATED = "qualification.need_articulated"
    Q_TIMELINE_STATED = "qualification.timeline_stated"
    Q_DISPOSITION = "qualification.disposition"{custom_enum_block}


class GtmEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: GtmLabel
    text: str = Field(..., description="The raw extracted span from the source.")
    normalized_value: Optional[str] = Field(default=None)
    confidence: float = Field(..., ge=0.0, le=1.0)


class GtmEntityLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_label: GtmLabel
    to_label: GtmLabel
    relation: str


def extraction_guidance() -> dict[str, str]:
    """Return {{label_value: human_definition}} for every label including custom signals."""
    _guidance: dict[str, str] = {{
        "account.company_name": "The legal or commonly-used name of a company being discussed.",
        "account.domain": "The primary web domain of a company (e.g. \\'acme.com\\').",
        "account.industry": "The industry the company operates in. Use the most specific form stated.",
        "account.employee_range": (
            "Employee count as a bucket. Use one of: \\'1-10\\', \\'11-50\\', \\'51-200\\', "
            "\\'201-1000\\', \\'1001-5000\\', \\'5000+\\'. Map exact counts to the right bucket."
        ),
        "account.revenue_range": (
            "Annual revenue bucket. Use one of: \\'<1M\\', \\'1-10M\\', \\'10-50M\\', "
            "\\'50-250M\\', \\'250M-1B\\', \\'1B+\\'."
        ),
        "account.hq_location": "Headquarters city/region/country, as stated.",
        "account.tech_stack_item": (
            "A specific technology, tool, or vendor the company uses. Extract one entity per technology."
        ),
        "account.funding_stage": (
            "Funding stage. Use one of: \\'bootstrapped\\', \\'pre_seed\\', \\'seed\\', \\'series_a\\', "
            "\\'series_b\\', \\'series_c\\', \\'series_d_plus\\', \\'public\\', \\'acquired\\'."
        ),
        "contact.full_name": "A person\\'s full name when referenced as a professional contact.",
        "contact.title": "The exact job title as stated.",
        "contact.seniority": (
            "Seniority bucket. Use one of: \\'ic\\', \\'manager\\', \\'director\\', \\'vp\\', \\'c_suite\\', \\'founder\\'."
        ),
        "contact.department": (
            "Department bucket. Use one of: \\'engineering\\', \\'product\\', \\'sales\\', \\'marketing\\', "
            "\\'revops\\', \\'cs\\', \\'finance\\', \\'hr\\', \\'legal\\', \\'operations\\', \\'other\\'."
        ),
        "contact.email": "A professional email address for the contact.",
        "contact.linkedin_url": "A LinkedIn profile URL for the contact.",
        "signal.hiring_trigger": (
            "A mention that the company is hiring for a specific role or team in a way "
            "that signals buying intent."
        ),
        "signal.funding_trigger": "A funding event with timing or amount.",
        "signal.tech_adoption": "A statement that the company has adopted or deployed a specific technology recently.",
        "signal.pain_point_mention": "A stated problem, frustration, or gap. Extract the pain phrase as-stated.",
        "signal.competitor_mention": "A named competitor product or vendor.",
        "signal.intent_topic": "A topic the account is actively researching.",
        "engagement.email_open": "A recorded email open event.",
        "engagement.email_reply": "A recorded email reply event.",
        "engagement.meeting_booked": "A booked or scheduled meeting reference.",
        "engagement.call_transcript_ref": "A reference to or excerpt from a sales call transcript.",
        "engagement.form_submit": "A form submission (demo request, content download, etc.).",
        "qualification.budget_confirmed": "Explicit evidence that budget exists or has been allocated. Quote the evidence.",
        "qualification.authority_identified": "Explicit evidence that the decision-maker has been identified. Quote the evidence.",
        "qualification.need_articulated": "Explicit evidence that a need or use case has been articulated. Quote the evidence.",
        "qualification.timeline_stated": "Explicit evidence of a buying timeline or compelling event. Quote the evidence.",
        "qualification.disposition": (
            "The overall qualification verdict. Use one of: \\'qualified\\', \\'nurture\\', \\'disqualified\\'."
        ),{custom_guidance_block}
    }}
{icp_guidance_block}
    return _guidance


def valid_links() -> list[GtmEntityLink]:
    return [
        GtmEntityLink(from_label=GtmLabel.C_FULL_NAME, to_label=GtmLabel.A_COMPANY_NAME, relation="works_at"),
        GtmEntityLink(from_label=GtmLabel.C_TITLE, to_label=GtmLabel.C_FULL_NAME, relation="title_of"),
        GtmEntityLink(from_label=GtmLabel.S_HIRING_TRIGGER, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.S_FUNDING_TRIGGER, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.S_TECH_ADOPTION, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.S_PAIN_POINT_MENTION, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.E_EMAIL_REPLY, to_label=GtmLabel.C_FULL_NAME, relation="from_contact"),
        GtmEntityLink(from_label=GtmLabel.E_MEETING_BOOKED, to_label=GtmLabel.C_FULL_NAME, relation="with_contact"),
        GtmEntityLink(from_label=GtmLabel.Q_BUDGET_CONFIRMED, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.Q_AUTHORITY_IDENTIFIED, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.Q_NEED_ARTICULATED, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.Q_TIMELINE_STATED, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.Q_DISPOSITION, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
    ]
{sw_block}{policy_rules_block}
'''
    return out


# ---------------------------------------------------------------------------
# Modifiers merge (Story E2 — modifier_overrides)
# ---------------------------------------------------------------------------


def merge_modifiers(baseline_text: str, bundle: OverrideBundle) -> str:
    """Apply modifier_overrides to the baseline YAML and return deterministic YAML text."""
    data: Any = yaml.safe_load(baseline_text) or {}

    mo = bundle.modifier
    if mo.intent_topics is not None:
        it = mo.intent_topics
        signal_section = data.setdefault("signal", {})
        intent_section = signal_section.setdefault("intent_topics", {})
        topics_map = intent_section.setdefault("topics", {})

        if it.add:
            client_topics = sorted(set(it.add))
            topics_map["client_specific"] = client_topics

        if it.deprioritize:
            intent_section["deprioritized"] = sorted(set(it.deprioritize))

    return yaml.dump(data, default_flow_style=False, sort_keys=True, allow_unicode=True)


# ---------------------------------------------------------------------------
# Policy merge (Story E2 — policy_overrides)
# ---------------------------------------------------------------------------


def merge_policy(baseline_text: str, bundle: OverrideBundle) -> str:
    """Append buyer-specific rules to the baseline policy module."""
    lines: list[str] = [baseline_text.rstrip()]

    po = bundle.policy

    rule_sections: list[str] = []

    if po.disqualification_rules:
        block = ["", "# --- Client disqualification rules (from policy_overrides) ---"]
        for rule in po.disqualification_rules:
            block.append(f"# DISQUALIFY if: {rule.condition}")
            block.append(f"# Rationale: {rule.rationale}")
        rule_sections.append("\n".join(block))

    if po.auto_pass_rules:
        block = ["", "# --- Client auto-pass rules (from policy_overrides) ---"]
        for rule in po.auto_pass_rules:
            block.append(f"# AUTO_PASS if: {rule.condition}")
            block.append(f"# Rationale: {rule.rationale}")
        rule_sections.append("\n".join(block))

    if po.hil_rules:
        block = ["", "# --- Client HIL rules (from policy_overrides) ---"]
        for rule in po.hil_rules:
            block.append(f"# HIL if: {rule.condition}")
            block.append(f"# Rationale: {rule.rationale}")
        rule_sections.append("\n".join(block))

    if rule_sections:
        lines.append("")
        lines.append("")
        lines.append("# ============================================================")
        lines.append("# CLIENT-SPECIFIC POLICY RULES — generated by schema-forge generate")
        lines.append("# ============================================================")
        lines.extend(rule_sections)

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Manifest builder (Story E3)
# ---------------------------------------------------------------------------


def build_manifest(
    baseline_version: str,
    client: str,
    override_files: dict[str, Path],
    changes: list[str],
    now: datetime,
    output_schema_filename: str,
) -> dict[str, Any]:
    """Build the manifest dict. Pure function — no I/O."""
    overrides_section: dict[str, str] = {}
    for name in sorted(override_files):
        p = override_files[name]
        if p.exists():
            overrides_section[name] = f"sha256:{_sha256(p)}"

    return {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "baseline_version": baseline_version,
        "client": client,
        "overrides": overrides_section,
        "output": {
            "schema": output_schema_filename,
            "changes_from_baseline": changes,
        },
    }


# ---------------------------------------------------------------------------
# Change-log builder
# ---------------------------------------------------------------------------


def _collect_changes(bundle: OverrideBundle, override_files: dict[str, Path]) -> list[str]:
    """Return a sorted, deterministic list of human-readable change descriptions."""
    changes: list[str] = []

    # ICP changes
    icp_file = "icp_overrides.yaml"
    for label_val, lf in sorted(bundle.icp.filters.items()):
        parts: list[str] = []
        if lf.include:
            parts.append(f"include {lf.include}")
        if lf.exclude:
            parts.append(f"exclude {lf.exclude}")
        if lf.preferred:
            parts.append(f"preferred {lf.preferred}")
        if parts:
            desc = f"{label_val}: {'; '.join(parts)} — {lf.rationale} ({icp_file})"
            changes.append(desc)

    # Channel changes — signal weights
    channel_file = "channel_overrides.yaml"
    for label_val, weight in sorted(bundle.channel.signal_weights.items()):
        changes.append(
            f"signal_weight {label_val}={weight} ({channel_file})"
        )
    # Channel changes — custom signals
    for sig in sorted(bundle.channel.custom_signals, key=lambda s: s.name):
        if sig.add_to_schema:
            changes.append(
                f"added custom signal {sig.name}: {sig.definition} — {sig.rationale} ({channel_file})"
            )

    # Modifier changes
    modifier_file = "modifier_overrides.yaml"
    mo = bundle.modifier
    if mo.intent_topics is not None:
        it = mo.intent_topics
        if it.add:
            changes.append(
                f"added intent_topics {sorted(it.add)} — {it.rationale} ({modifier_file})"
            )
        if it.deprioritize:
            changes.append(
                f"deprioritized intent_topics {sorted(it.deprioritize)} — {it.rationale} ({modifier_file})"
            )

    # Policy changes
    policy_file = "policy_overrides.yaml"
    for rule in bundle.policy.disqualification_rules:
        changes.append(
            f"disqualify rule: {rule.condition} — {rule.rationale} ({policy_file})"
        )
    for rule in bundle.policy.auto_pass_rules:
        changes.append(
            f"auto_pass rule: {rule.condition} — {rule.rationale} ({policy_file})"
        )
    for rule in bundle.policy.hil_rules:
        changes.append(
            f"hil rule: {rule.condition} — {rule.rationale} ({policy_file})"
        )

    return changes


# ---------------------------------------------------------------------------
# Main entry point (Story E1)
# ---------------------------------------------------------------------------


def run_generate(
    engagement_dir: Path,
    client: str,
    *,
    now: datetime | None = None,
) -> None:
    """Merge 02_baseline/ + 03_overrides/ and write 04_output/ + manifest.yaml.

    Deterministic: identical inputs + same ``now`` produce byte-identical outputs.
    ``now`` defaults to UTC now; injectable for tests.
    """
    if now is None:
        now = datetime.now(timezone.utc).replace(microsecond=0)

    baseline_dir = engagement_dir / "02_baseline"
    overrides_dir = engagement_dir / "03_overrides"
    output_dir = engagement_dir / "04_output"

    slug = _slugify(client)

    # Load overrides (missing files produce empty defaults)
    bundle = load_overrides(overrides_dir)

    # Read baseline files
    schema_text = (baseline_dir / "gtm_schema.py").read_text()
    modifiers_text = (baseline_dir / "modifiers.yaml").read_text()
    policy_text = (baseline_dir / "policy.py").read_text()
    gold_text = (baseline_dir / "synthetic_gold.jsonl").read_text()
    baseline_fm_dir = baseline_dir / "failure_modes"

    # Discover the baseline version from manifest.yaml in engagement root
    manifest_path = engagement_dir / "manifest.yaml"
    baseline_version = "gtm_v1.0"
    if manifest_path.exists():
        manifest_data = yaml.safe_load(manifest_path.read_text()) or {}
        baseline_version = manifest_data.get("baseline_version", baseline_version)

    # --- Generate output artifacts ---
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Schema
    schema_filename = f"gtm_{slug}_v1.py"
    schema_out = merge_schema(schema_text, bundle, client)
    (output_dir / schema_filename).write_text(schema_out, encoding="utf-8")

    # 2. Modifiers YAML
    modifiers_filename = f"gtm_{slug}_modifiers.yaml"
    modifiers_out = merge_modifiers(modifiers_text, bundle)
    (output_dir / modifiers_filename).write_text(modifiers_out, encoding="utf-8")

    # 3. Policy
    policy_filename = f"gtm_{slug}_policy.py"
    policy_out = merge_policy(policy_text, bundle)
    (output_dir / policy_filename).write_text(policy_out, encoding="utf-8")

    # 4. Failure modes — copy baseline + client additions
    fm_out_dir = output_dir / f"gtm_{slug}_failure_modes"
    if fm_out_dir.exists():
        shutil.rmtree(fm_out_dir)
    fm_out_dir.mkdir()

    if baseline_fm_dir.exists():
        for fm_file in sorted(baseline_fm_dir.iterdir()):
            if fm_file.name.startswith("_") or fm_file.suffix != ".py":
                continue
            shutil.copy2(fm_file, fm_out_dir / fm_file.name)

    client_fm_dir = overrides_dir / "failure_mode_additions"
    client_fm_files: list[str] = []
    if client_fm_dir.exists():
        for fm_file in sorted(client_fm_dir.iterdir()):
            if fm_file.suffix == ".py" and not fm_file.name.startswith("_"):
                shutil.copy2(fm_file, fm_out_dir / fm_file.name)
                client_fm_files.append(fm_file.name)

    # 5. Gold — carried from baseline unchanged
    gold_filename = f"gtm_{slug}_gold.jsonl"
    (output_dir / gold_filename).write_text(gold_text, encoding="utf-8")

    # --- Collect changes for manifest ---
    override_file_paths: dict[str, Path] = {
        "icp_overrides.yaml": overrides_dir / "icp_overrides.yaml",
        "channel_overrides.yaml": overrides_dir / "channel_overrides.yaml",
        "modifier_overrides.yaml": overrides_dir / "modifier_overrides.yaml",
        "policy_overrides.yaml": overrides_dir / "policy_overrides.yaml",
    }

    changes = _collect_changes(bundle, override_file_paths)
    for fname in sorted(client_fm_files):
        changes.append(f"added failure_mode {fname} (failure_mode_additions/{fname})")

    # --- Write manifest ---
    manifest_dict = build_manifest(
        baseline_version=baseline_version,
        client=client,
        override_files={k: v for k, v in override_file_paths.items() if v.exists()},
        changes=changes,
        now=now,
        output_schema_filename=schema_filename,
    )
    manifest_path.write_text(
        yaml.dump(manifest_dict, default_flow_style=False, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )
