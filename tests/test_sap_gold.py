"""
Tests for sap_gold.jsonl — the SAP-Joule engagement v0 gold corpus.

Asserts:
  1. Every record parses and has required fields.
  2. Every entity label is a valid GtmLabel in gtm_sapjoule_v1.py.
  3. Every entity validates against GtmEntity.
  4. Corpus contains ~200 records.
  5. Channel-affiliation mix is present (end_customer, channel_partner).
  6. Disposition spread is present (qualified, nurture, disqualified).
  7. The generator is deterministic (re-run produces identical bytes).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLD_PATH = REPO_ROOT / "engagements" / "sap-joule" / "gold" / "sap_gold.jsonl"
GENERATOR_PATH = REPO_ROOT / "engagements" / "sap-joule" / "gold" / "_gen_sap_gold.py"
SCHEMA_PATH = REPO_ROOT / "engagements" / "sap-joule" / "04_output" / "gtm_sapjoule_v1.py"


# ---------------------------------------------------------------------------
# Module loading helpers
# ---------------------------------------------------------------------------

def _load_schema():
    spec = importlib.util.spec_from_file_location("_sap_gold_schema", SCHEMA_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_sap_gold_schema"] = mod
    try:
        spec.loader.exec_module(mod)
        mod.GtmEntity.model_rebuild()
    finally:
        sys.modules.pop("_sap_gold_schema", None)
    return mod


_SCHEMA_MOD = _load_schema()
_VALID_LABEL_VALUES = {lbl.value for lbl in _SCHEMA_MOD.GtmLabel}


def _load_records() -> list[tuple[int, dict]]:
    assert GOLD_PATH.exists(), f"sap_gold.jsonl not found at {GOLD_PATH}"
    records = []
    with open(GOLD_PATH, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            records.append((i, json.loads(line)))
    return records


RECORDS = _load_records()


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------

def test_record_count():
    assert len(RECORDS) >= 200, f"Expected at least 200 records, got {len(RECORDS)}"
    assert len(RECORDS) <= 210, f"Expected ~200 records, got {len(RECORDS)}"


def test_all_records_have_required_fields():
    required = {"source_doc_id", "source_type", "grounding_sources", "entities"}
    for i, record in RECORDS:
        missing = required - set(record.keys())
        assert not missing, f"Record {i} ({record.get('source_doc_id')}): missing fields {missing}"


def test_source_doc_ids_unique():
    ids = [record.get("source_doc_id") for _, record in RECORDS]
    assert len(ids) == len(set(ids)), "source_doc_id values must be unique"


def test_source_types_are_valid():
    valid_types = {"linkedin_post", "website_page", "crm_note", "call_transcript", "email"}
    for i, record in RECORDS:
        src_type = record.get("source_type")
        assert src_type in valid_types, (
            f"Record {i}: invalid source_type '{src_type}'. Must be one of {valid_types}"
        )


def test_each_record_has_entities():
    for i, record in RECORDS:
        entities = record.get("entities", [])
        assert len(entities) > 0, f"Record {i}: entities list must not be empty"


def test_grounding_sources_present():
    for i, record in RECORDS:
        sources = record.get("grounding_sources", [])
        assert isinstance(sources, list) and len(sources) > 0, (
            f"Record {i}: grounding_sources must be a non-empty list"
        )


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def test_all_labels_are_valid_gtm_labels():
    """Every entity label must be a valid GtmLabel value in gtm_sapjoule_v1.py."""
    errors = []
    for i, record in RECORDS:
        for j, entity in enumerate(record.get("entities", [])):
            label = entity.get("label")
            if label not in _VALID_LABEL_VALUES:
                errors.append(f"Record {i}, entity {j}: unknown label '{label}'")
    assert not errors, "Unknown labels found:\n" + "\n".join(errors[:10])


def test_all_entities_validate_against_gtm_entity():
    """Every entity must validate against GtmEntity from gtm_sapjoule_v1.py."""
    errors = []
    for i, record in RECORDS:
        for j, entity in enumerate(record.get("entities", [])):
            try:
                _SCHEMA_MOD.GtmEntity(**entity)
            except Exception as e:
                errors.append(f"Record {i}, entity {j} ({entity.get('label')}): {e}")
    assert not errors, "GtmEntity validation errors:\n" + "\n".join(errors[:10])


def test_confidence_bounds():
    for i, record in RECORDS:
        for j, entity in enumerate(record.get("entities", [])):
            conf = entity.get("confidence")
            assert conf is not None, f"Record {i}, entity {j}: missing confidence"
            assert 0.0 <= conf <= 1.0, (
                f"Record {i}, entity {j}: confidence {conf} out of [0, 1]"
            )


# ---------------------------------------------------------------------------
# SAP-specific label coverage
# ---------------------------------------------------------------------------

def test_custom_signals_present_in_corpus():
    """All 6 custom SAP signals must appear at least once in the corpus."""
    expected_custom = {
        "custom.s_s4_migration_timeline",
        "custom.s_joule_interest",
        "custom.s_clean_core_initiative",
        "custom.s_rise_adoption",
        "custom.s_sap_field_co_sell",
        "custom.s_si_partner_involved",
    }
    seen = set()
    for _, record in RECORDS:
        for entity in record.get("entities", []):
            seen.add(entity.get("label"))
    missing = expected_custom - seen
    assert not missing, f"Custom SAP signals never seen in gold corpus: {missing}"


def test_required_label_coverage():
    """Core labels must appear across the corpus."""
    required_labels = {
        "account.company_name",
        "account.industry",
        "account.tech_stack_item",
        "account.revenue_range",
        "account.employee_range",
        "contact.full_name",
        "contact.seniority",
        "contact.affiliation",
        "signal.intent_topic",
        "signal.pain_point_mention",
        "qualification.disposition",
    }
    seen = set()
    for _, record in RECORDS:
        for entity in record.get("entities", []):
            seen.add(entity.get("label"))
    missing = required_labels - seen
    assert not missing, f"Required labels never seen in gold corpus: {missing}"


# ---------------------------------------------------------------------------
# Channel affiliation mix
# ---------------------------------------------------------------------------

def test_affiliation_mix_present():
    """Both end_customer and channel_partner affiliations must be present."""
    affiliations = {}
    for _, record in RECORDS:
        for entity in record.get("entities", []):
            if entity.get("label") == "contact.affiliation":
                val = entity.get("text") or entity.get("normalized_value", "")
                affiliations[val] = affiliations.get(val, 0) + 1

    assert "end_customer" in affiliations, "No end_customer affiliation found in corpus"
    assert "channel_partner" in affiliations, "No channel_partner affiliation found in corpus"

    total = sum(affiliations.values())
    end_customer_pct = affiliations.get("end_customer", 0) / total
    channel_pct = affiliations.get("channel_partner", 0) / total

    # Spec: ~50% end_customer, ~50% channel (sap_field + SI combined)
    assert 0.35 <= end_customer_pct <= 0.65, (
        f"end_customer affiliation out of range: {end_customer_pct:.1%} (expected ~50%)"
    )
    assert 0.35 <= channel_pct <= 0.65, (
        f"channel_partner affiliation out of range: {channel_pct:.1%} (expected ~50%)"
    )


def test_sap_field_cosell_signal_present():
    """custom.s_sap_field_co_sell must appear (sap-field channel records)."""
    seen = any(
        entity.get("label") == "custom.s_sap_field_co_sell"
        for _, record in RECORDS
        for entity in record.get("entities", [])
    )
    assert seen, "custom.s_sap_field_co_sell not found in any record"


def test_si_partner_signal_present():
    """custom.s_si_partner_involved must appear (SI/Big4 channel records)."""
    seen = any(
        entity.get("label") == "custom.s_si_partner_involved"
        for _, record in RECORDS
        for entity in record.get("entities", [])
    )
    assert seen, "custom.s_si_partner_involved not found in any record"


# ---------------------------------------------------------------------------
# Disposition spread
# ---------------------------------------------------------------------------

def test_disposition_spread_present():
    """qualified, nurture, and disqualified must all appear."""
    dispositions = {}
    for _, record in RECORDS:
        for entity in record.get("entities", []):
            if entity.get("label") == "qualification.disposition":
                val = entity.get("text", "")
                dispositions[val] = dispositions.get(val, 0) + 1

    for required in ("qualified", "nurture", "disqualified"):
        assert required in dispositions, (
            f"disposition '{required}' not found in corpus. Seen: {dispositions}"
        )


def test_disposition_values_are_valid():
    """All disposition values must be one of the allowed set."""
    valid_dispositions = {"qualified", "nurture", "disqualified"}
    for i, record in RECORDS:
        for entity in record.get("entities", []):
            if entity.get("label") == "qualification.disposition":
                val = entity.get("text", "")
                assert val in valid_dispositions, (
                    f"Record {i}: invalid disposition value '{val}'"
                )


def test_disposition_nurture_is_largest_group():
    """nurture should be the majority disposition (realistic pipeline mix)."""
    dispositions: dict[str, int] = {}
    for _, record in RECORDS:
        for entity in record.get("entities", []):
            if entity.get("label") == "qualification.disposition":
                val = entity.get("text", "")
                dispositions[val] = dispositions.get(val, 0) + 1

    nurture_count = dispositions.get("nurture", 0)
    qualified_count = dispositions.get("qualified", 0)
    disqualified_count = dispositions.get("disqualified", 0)
    total = nurture_count + qualified_count + disqualified_count

    assert nurture_count >= qualified_count, (
        f"nurture ({nurture_count}) should be >= qualified ({qualified_count})"
    )
    assert total == len(RECORDS), f"Expected {len(RECORDS)} disposition entities, got {total}"


# ---------------------------------------------------------------------------
# Real anchor records
# ---------------------------------------------------------------------------

def test_ferrero_anchor_record_present():
    """Ferrero (real anchor, Indeed JOB_3) must be present and correctly labeled."""
    ferrero_records = [
        record for _, record in RECORDS
        if any(e.get("label") == "account.company_name" and e.get("text") == "Ferrero"
               for e in record.get("entities", []))
    ]
    assert ferrero_records, "Ferrero anchor record not found in corpus"

    record = ferrero_records[0]
    # Must cite the Indeed job
    assert any("JOB_3" in src for src in record.get("grounding_sources", [])), (
        "Ferrero record must cite Indeed JOB_3 in grounding_sources"
    )
    # Must be end_customer
    affiliations = [
        e.get("normalized_value") or e.get("text")
        for e in record.get("entities", [])
        if e.get("label") == "contact.affiliation"
    ]
    assert "end_customer" in affiliations, "Ferrero record must have end_customer affiliation"


def test_w3global_anchor_record_present():
    """w3global (real anchor, Indeed JOB_1) must be present."""
    w3_records = [
        record for _, record in RECORDS
        if any(e.get("label") == "account.company_name" and e.get("text") == "w3global"
               for e in record.get("entities", []))
    ]
    assert w3_records, "w3global anchor record not found in corpus"
    record = w3_records[0]
    assert any("JOB_1" in src for src in record.get("grounding_sources", [])), (
        "w3global record must cite Indeed JOB_1 in grounding_sources"
    )


def test_real_anchor_grounding_cites_indeed():
    """All three anchor records (Ferrero, w3global, Quintile) must cite Indeed URLs."""
    real_company_names = {"Ferrero", "w3global", "Quintile Advisory"}
    for company in real_company_names:
        company_records = [
            record for _, record in RECORDS
            if any(e.get("label") == "account.company_name" and e.get("text") == company
                   for e in record.get("entities", []))
        ]
        assert company_records, f"No record found for real anchor '{company}'"
        record = company_records[0]
        sources = record.get("grounding_sources", [])
        has_indeed = any("indeed.com" in src or "JOB_" in src for src in sources)
        assert has_indeed, f"{company} record must cite Indeed URL in grounding_sources. Got: {sources}"


def test_synthetic_accounts_have_synthetic_grounding():
    """All synthetic (non-anchor) records must cite the Vibe distribution."""
    real_companies = {"Ferrero", "w3global", "Quintile Advisory"}
    for _, record in RECORDS:
        company_entities = [
            e for e in record.get("entities", [])
            if e.get("label") == "account.company_name"
        ]
        if not company_entities:
            continue
        company_name = company_entities[0].get("text", "")
        if company_name in real_companies:
            continue
        sources = record.get("grounding_sources", [])
        has_vibe = any("Vibe" in src or "n=30,316" in src for src in sources)
        assert has_vibe, (
            f"Synthetic record for '{company_name}' must cite Vibe distribution in grounding_sources. "
            f"Got: {sources}"
        )


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

def test_generator_is_deterministic(tmp_path: Path):
    """Re-running the generator with same SEED produces byte-identical output."""
    output_1 = tmp_path / "sap_gold_run1.jsonl"
    output_2 = tmp_path / "sap_gold_run2.jsonl"

    spec = importlib.util.spec_from_file_location("_gen_sap_gold_run1", GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main(output_1)

    spec2 = importlib.util.spec_from_file_location("_gen_sap_gold_run2", GENERATOR_PATH)
    assert spec2 is not None and spec2.loader is not None
    mod2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mod2)
    mod2.main(output_2)

    bytes1 = output_1.read_bytes()
    bytes2 = output_2.read_bytes()
    assert bytes1 == bytes2, "Generator is not deterministic: two runs produced different output"


def test_committed_jsonl_matches_generator_output(tmp_path: Path):
    """Committed sap_gold.jsonl must match fresh generator output (determinism check)."""
    regen_path = tmp_path / "sap_gold_regen.jsonl"

    spec = importlib.util.spec_from_file_location("_gen_sap_gold_regen", GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main(regen_path)

    committed = GOLD_PATH.read_bytes()
    regenerated = regen_path.read_bytes()
    assert committed == regenerated, (
        "Committed sap_gold.jsonl does not match fresh generator output. "
        "Run _gen_sap_gold.py and re-commit the output."
    )
