"""
Tests for gtm@v1 baseline schema. Adapted from docs/test_gtm_schema.py with:
- spine registry / load_schema removed (no spine here)
- direct import from forge.domains.gtm.baseline.gtm_schema
"""

import pytest
from pydantic import ValidationError

from forge.domains.gtm.baseline.gtm_schema import (
    GtmEntity,
    GtmEntityLink,
    GtmLabel,
    extraction_guidance,
    valid_links,
)


def test_gtm_schema_accepts_gtm_label():
    e = GtmEntity(label=GtmLabel.A_COMPANY_NAME, text="Acme Corp", confidence=0.82)
    assert e.label == GtmLabel.A_COMPANY_NAME


def test_gtm_schema_rejects_unknown_labels():
    with pytest.raises(ValidationError):
        GtmEntity(label="question", text="x", confidence=0.5)
    with pytest.raises(ValidationError):
        GtmEntity(label="menu.nm", text="x", confidence=0.5)


def test_gtm_confidence_bounded():
    with pytest.raises(ValidationError):
        GtmEntity(label=GtmLabel.A_COMPANY_NAME, text="x", confidence=1.5)
    with pytest.raises(ValidationError):
        GtmEntity(label=GtmLabel.A_COMPANY_NAME, text="x", confidence=-0.1)
    with pytest.raises(ValidationError):
        GtmEntity(label=GtmLabel.A_COMPANY_NAME, text="x")


def test_gtm_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        GtmEntity(label=GtmLabel.A_COMPANY_NAME, text="x", confidence=0.5, unknown_field="y")


def test_gtm_normalized_value_optional():
    e1 = GtmEntity(label=GtmLabel.C_SENIORITY, text="VP of Sales", confidence=0.9)
    assert e1.normalized_value is None
    e2 = GtmEntity(
        label=GtmLabel.C_SENIORITY,
        text="VP of Sales",
        normalized_value="vp",
        confidence=0.9,
    )
    assert e2.normalized_value == "vp"


def test_extraction_guidance_covers_every_label():
    guidance = extraction_guidance()
    enum_values = {lbl.value for lbl in GtmLabel}
    guidance_keys = set(guidance.keys())
    missing = enum_values - guidance_keys
    extra = guidance_keys - enum_values
    assert not missing, f"labels missing from extraction_guidance: {missing}"
    assert not extra, f"unknown labels in extraction_guidance: {extra}"


def test_extraction_guidance_has_30_labels():
    assert len(extraction_guidance()) == 30


def test_valid_links_reference_real_labels():
    enum_values = {lbl.value for lbl in GtmLabel}
    for link in valid_links():
        assert link.from_label.value in enum_values
        assert link.to_label.value in enum_values


def test_valid_links_count():
    assert len(valid_links()) == 13


def test_gtm_label_families():
    labels = list(GtmLabel)
    account = [l for l in labels if l.value.startswith("account.")]
    contact = [l for l in labels if l.value.startswith("contact.")]
    signal = [l for l in labels if l.value.startswith("signal.")]
    engagement = [l for l in labels if l.value.startswith("engagement.")]
    qualification = [l for l in labels if l.value.startswith("qualification.")]
    assert len(account) == 8
    assert len(contact) == 6
    assert len(signal) == 6
    assert len(engagement) == 5
    assert len(qualification) == 5
    assert len(account) + len(contact) + len(signal) + len(engagement) + len(qualification) == 30


def test_entity_link_extra_forbidden():
    with pytest.raises(ValidationError):
        GtmEntityLink(
            from_label=GtmLabel.C_FULL_NAME,
            to_label=GtmLabel.A_COMPANY_NAME,
            relation="works_at",
            bogus="field",
        )
