"""
Tests for synthetic_gold.jsonl: every record parses and each entity validates against GtmEntity.
"""

import json
import pathlib

import pytest
from pydantic import ValidationError

from forge.domains.gtm.baseline.gtm_schema import GtmEntity, GtmLabel

GOLD_PATH = pathlib.Path(__file__).resolve().parent.parent / "forge/domains/gtm/baseline/synthetic_gold.jsonl"


def _load_records():
    assert GOLD_PATH.exists(), f"synthetic_gold.jsonl not found at {GOLD_PATH}"
    records = []
    with open(GOLD_PATH, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            records.append((i, json.loads(line)))
    return records


RECORDS = _load_records()


def test_record_count():
    assert len(RECORDS) >= 200, f"Expected at least 200 records, got {len(RECORDS)}"


def test_all_records_have_required_fields():
    required = {"source_doc_id", "source_type", "grounding_sources", "entities"}
    for i, record in RECORDS:
        missing = required - set(record.keys())
        assert not missing, f"Record {i} missing fields: {missing}"


def test_all_entities_validate():
    valid_label_values = {lbl.value for lbl in GtmLabel}
    errors = []
    for i, record in RECORDS:
        for j, entity in enumerate(record.get("entities", [])):
            try:
                GtmEntity(**entity)
            except (ValidationError, Exception) as e:
                errors.append(f"Record {i}, entity {j} ({entity.get('label')}): {e}")
    assert not errors, f"Entity validation errors:\n" + "\n".join(errors[:10])


def test_all_labels_are_valid_gtm_labels():
    valid_label_values = {lbl.value for lbl in GtmLabel}
    for i, record in RECORDS:
        for j, entity in enumerate(record.get("entities", [])):
            label = entity.get("label")
            assert label in valid_label_values, (
                f"Record {i}, entity {j}: unknown label '{label}'"
            )


def test_confidence_bounds():
    for i, record in RECORDS:
        for j, entity in enumerate(record.get("entities", [])):
            conf = entity.get("confidence")
            assert conf is not None, f"Record {i}, entity {j}: missing confidence"
            assert 0.0 <= conf <= 1.0, (
                f"Record {i}, entity {j}: confidence {conf} out of [0,1]"
            )


def test_grounding_sources_present():
    for i, record in RECORDS:
        sources = record.get("grounding_sources", [])
        assert isinstance(sources, list) and len(sources) > 0, (
            f"Record {i}: grounding_sources must be a non-empty list"
        )


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


def test_label_coverage():
    all_labels_seen = set()
    for _, record in RECORDS:
        for entity in record.get("entities", []):
            all_labels_seen.add(entity.get("label"))
    required_labels = {
        "account.company_name", "account.industry", "account.funding_stage",
        "contact.full_name", "contact.seniority", "contact.department",
        "signal.intent_topic", "signal.pain_point_mention",
        "qualification.disposition",
    }
    missing = required_labels - all_labels_seen
    assert not missing, f"Labels never seen in gold corpus: {missing}"
