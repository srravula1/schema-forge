"""
Tests for gtm@v1. Mirrors the C-1 acceptance shape from CORD-STORIES.md exactly:
  - the schema coexists with funsd@v1 and cord@v1
  - GTM labels validate; FUNSD/CORD labels are rejected
  - extraction_guidance() covers every label in the enum (the prompt-builder contract)
"""

import pytest
from pydantic import ValidationError

from spine.schema.registry import load_schema
from spine.schema.gtm import GtmLabel, extraction_guidance, valid_links


def test_gtm_funsd_cord_schemas_coexist():
    """All three resolve to distinct models simultaneously — registry mechanism unchanged."""
    funsd = load_schema("funsd@v1")
    cord = load_schema("cord@v1")
    gtm = load_schema("gtm@v1")
    assert funsd is not cord is not gtm
    # spot-check: gtm is the GtmEntity model
    assert gtm.__name__ == "GtmEntity"


def test_gtm_schema_accepts_gtm_label():
    Gtm = load_schema("gtm@v1")
    e = Gtm(label=GtmLabel.A_COMPANY_NAME, text="Acme Corp", confidence=0.82)
    assert e.label == GtmLabel.A_COMPANY_NAME


def test_gtm_schema_rejects_funsd_and_cord_labels():
    """A GTM entity must reject question/answer (FUNSD) and menu.nm (CORD)."""
    Gtm = load_schema("gtm@v1")
    with pytest.raises(ValidationError):
        Gtm(label="question", text="x", confidence=0.5)
    with pytest.raises(ValidationError):
        Gtm(label="menu.nm", text="x", confidence=0.5)


def test_gtm_confidence_bounded():
    """Same contract as funsd@v2 / cord@v1: required and [0,1]."""
    Gtm = load_schema("gtm@v1")
    with pytest.raises(ValidationError):
        Gtm(label=GtmLabel.A_COMPANY_NAME, text="x", confidence=1.5)
    with pytest.raises(ValidationError):
        Gtm(label=GtmLabel.A_COMPANY_NAME, text="x")  # missing


def test_extraction_guidance_covers_every_label():
    """Prompt-builder contract: schema-driven extraction must define every label."""
    guidance = extraction_guidance()
    enum_values = {lbl.value for lbl in GtmLabel}
    guidance_keys = set(guidance.keys())
    missing = enum_values - guidance_keys
    extra = guidance_keys - enum_values
    assert not missing, f"labels missing from extraction_guidance: {missing}"
    assert not extra, f"unknown labels in extraction_guidance: {extra}"


def test_valid_links_reference_real_labels():
    """Declared link types must use real labels in both directions."""
    enum_values = {lbl.value for lbl in GtmLabel}
    for link in valid_links():
        assert link.from_label.value in enum_values
        assert link.to_label.value in enum_values
