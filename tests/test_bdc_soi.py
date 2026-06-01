"""
Tests for the bdc_soi domain (private-credit BDC Schedule-of-Investments → position marks).

Mirrors the GTM domain's discipline:
  - every failure-mode module exposes detect() + fixtures, and its fixture triggers the mode
  - the gold corpus parses and every entity validates against the position_mark schema
  - extraction_guidance() covers every schema field
Plus targeted detector behavior (the real CalPERS bugs are caught; clean marks pass) and the
HIL policy routes divergences correctly.
"""

import importlib
import json
import pathlib
import pkgutil

import pytest
from pydantic import ValidationError

import forge.domains.bdc_soi.baseline.failure_modes as fm_pkg
from forge.domains.bdc_soi.baseline import policy
from forge.domains.bdc_soi.baseline.failure_modes import SourceDoc
from forge.domains.bdc_soi.baseline.position_mark import (
    PositionMark,
    extraction_guidance,
    valid_links,
)

# --- failure-mode library -------------------------------------------------------------------

def _load_fm_modules():
    out = []
    prefix = fm_pkg.__name__ + "."
    for _, name, _ in pkgutil.iter_modules(fm_pkg.__path__):
        if name.startswith("_"):
            continue
        out.append((name, importlib.import_module(prefix + name)))
    return out


FM_MODULES = _load_fm_modules()


def test_failure_modes_present():
    # the five CalPERS-derived modes
    names = {n for n, _ in FM_MODULES}
    assert {
        "fm_fx_par_inflates_mark", "fm_mark_out_of_bounds", "fm_unfunded_revolver_counted",
        "fm_cross_period_blend", "fm_entity_overmerge",
    } <= names


@pytest.mark.parametrize("name,mod", FM_MODULES, ids=[n for n, _ in FM_MODULES])
def test_detect_contract(name, mod):
    assert callable(getattr(mod, "detect", None)), f"{name} must expose detect()"
    result = mod.detect(mod.FIXTURE_ENTITY, mod.FIXTURE_SOURCE)
    assert isinstance(result, tuple) and len(result) == 2, f"{name}.detect must return a 2-tuple"
    assert isinstance(result[0], bool)


@pytest.mark.parametrize("name,mod", FM_MODULES, ids=[n for n, _ in FM_MODULES])
def test_fixture_triggers(name, mod):
    detected, reason = mod.detect(mod.FIXTURE_ENTITY, mod.FIXTURE_SOURCE)
    assert detected, f"{name}: fixture should trigger the mode"
    assert reason and isinstance(reason, str)


def test_fx_detector_targeted():
    from forge.domains.bdc_soi.baseline.failure_modes import fm_fx_par_inflates_mark as fx
    # the real bug: OBDC Bamboo EUR tranche faked 115
    bad = PositionMark(holder="OBDC", borrower="Bamboo", fair_value_mark=115.2, as_of_date="x")
    eur = SourceDoc(text="First lien senior secured EUR term loan E+ 5.00% € 4,650 5,358")
    assert fx.detect(bad, eur)[0] is True
    # a clean USD mark at par is NOT flagged
    ok = PositionMark(holder="OBDC", borrower="Hyland", fair_value_mark=100.0, as_of_date="x")
    usd = SourceDoc(text="First lien senior secured loan S+ 5.00% 65,965 65,965")
    assert fx.detect(ok, usd)[0] is False


def test_out_of_bounds_is_upper_bound_only():
    from forge.domains.bdc_soi.baseline.failure_modes import fm_mark_out_of_bounds as ob
    src = SourceDoc(text="First lien senior secured loan")
    # PetVet's real 86.01 and deep-distress marks (Pluralsight 5.63, Walker Edison 0.94) must PASS —
    # a low mark is the signal, not an error
    for valid in (86.01, 5.63, 0.94, 100.97):
        assert ob.detect(PositionMark(holder="h", borrower="b", fair_value_mark=valid,
                                      as_of_date="x"), src)[0] is False
    # only fair-value-above-par (FX / column misattribution) is flagged
    assert ob.detect(PositionMark(holder="h", borrower="b", fair_value_mark=149.0,
                                  as_of_date="x"), src)[0] is True


# --- gold corpus ----------------------------------------------------------------------------

GOLD = pathlib.Path(__file__).resolve().parent.parent / \
    "forge/domains/bdc_soi/baseline/bdc_soi_gold.jsonl"


def _gold_records():
    assert GOLD.exists(), f"gold not found at {GOLD}"
    recs = []
    for line in GOLD.read_text(encoding="utf-8").splitlines():
        if line.strip():
            recs.append(json.loads(line))
    return recs


GOLD_RECORDS = _gold_records()


def test_gold_records_have_required_fields():
    required = {"source_doc_id", "source_type", "grounding_sources", "entities"}
    for i, r in enumerate(GOLD_RECORDS):
        assert required <= set(r), f"record {i} missing {required - set(r)}"


def test_gold_entities_validate_and_carry_provenance():
    n = 0
    for i, r in enumerate(GOLD_RECORDS):
        for j, ent in enumerate(r["entities"]):
            try:
                pm = PositionMark(**ent)
            except (ValidationError, Exception) as exc:  # noqa: BLE001
                pytest.fail(f"record {i} entity {j} invalid: {exc}")
            assert pm.provenance.cik and pm.provenance.accession, "every mark traces to a filing"
            n += 1
    assert n >= 12, f"expected the verified CalPERS set, got {n} entities"


def test_gold_contains_the_headline_divergence():
    # PetVet on both sides: 86.01 (ARCC) vs 90.00 (OBDC)
    marks = {(e["holder"][:4], round(e["fair_value_mark"], 2))
             for r in GOLD_RECORDS for e in r["entities"] if "PetVet" in e["borrower"]}
    assert ("Ares", 86.01) in marks and ("Blue", 90.0) in marks


# --- schema + policy ------------------------------------------------------------------------

def test_guidance_covers_every_field():
    fields = set(PositionMark.model_fields) - {"provenance"}
    covered = set(extraction_guidance())
    assert fields <= covered, f"guidance missing: {fields - covered}"
    assert valid_links() == []


def test_policy_routes_divergence_and_stressed_names():
    assert policy.disposition(3.99, min_mark=86.01) == "route_to_analyst"   # PetVet
    assert policy.disposition(0.0, min_mark=86.01) == "route_to_analyst"    # stressed even if flat
    assert policy.disposition(0.0, min_mark=100.0) == "log_consistent"      # at par, agree
    assert policy.disposition(0.2, non_accrual_disagreement=True) == "route_to_analyst"
