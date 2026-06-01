"""
bdc_soi@v1 — schema for one loan-level row of a BDC Consolidated Schedule of Investments.

Decision D1 (see docs/STORY-private-credit-bdc-soi.md): a BDC SoI row is a *structured typed row*,
not the flat label/text entity that GTM uses. This domain therefore adopts the platform's existing
`position_mark@v1` shape as its entity, rather than the GtmEntity label/text/confidence shape. The
schema-module contract is honored via `extraction_guidance()` (covers every field) and a validation-
compatible Pydantic v2 model. `valid_links()` is empty: SoI rows relate by shared `instrument_id`
across holders, resolved downstream, not by intra-document entity links.

The comparable cross-holder **mark** is `fair_value_mark = fair_value / par * 100` (per $100 par),
computed per tranche. The mark is currency- and unit-independent (it is a ratio); face/NAV is not —
the ingester normalizes those (see modifiers.yaml: units).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_REF = "position_mark@v1"
MARK_BASIS = "fair_value / par * 100  (price per 100 par, per tranche, USD funded principal only)"


class Provenance(BaseModel):
    """Field/row lineage. No row persists without it (platform Principle 6)."""

    model_config = ConfigDict(extra="forbid")

    source_span: Optional[str] = Field(default=None, description="verbatim SoI row text")
    cik: Optional[str] = Field(default=None, description="filer CIK")
    accession: Optional[str] = Field(default=None, description="filing accession number")
    as_of_date: Optional[str] = Field(default=None, description="SoI as-of date (current period)")


class PositionMark(BaseModel):
    """One disclosed loan position. Mirrors platform `position_mark@v1` so generated gold and the
    spine ingester validate against the same shape."""

    model_config = ConfigDict(extra="forbid")

    holder: str = Field(description="disclosing holder / BDC name")
    borrower: str = Field(description="portfolio-company / obligor name")
    instrument_id: Optional[str] = Field(default=None, description="instrument id / normalized key")
    seniority: Optional[str] = Field(default=None, description="e.g. first_lien_senior_secured")
    maturity: Optional[str] = Field(default=None, description="instrument maturity (m/yyyy)")
    par: Optional[float] = Field(default=None, description="funded par / principal held (USD)")
    fair_value_mark: float = Field(description="fair-value mark = fair_value / par * 100")
    coupon_spread: Optional[str] = Field(default=None, description="reference rate + spread")
    pik_flag: bool = Field(default=False, description="paid-in-kind flag")
    non_accrual_flag: bool = Field(default=False, description="non-accrual status")
    as_of_date: str = Field(description="as-of date of the disclosure (current reporting period)")
    provenance: Provenance = Field(default_factory=Provenance)


def extraction_guidance() -> dict[str, str]:
    """{field: definition} covering every schema field — the SoI-reading half of the prompt."""
    return {
        "holder": "The disclosing BDC (the filer of the 10-Q/10-K).",
        "borrower": "Portfolio-company / obligor name, verbatim. Strip footnote markers like "
                    "'(3)(4)(9)' and '(dba X)' only for the resolution key, never from the display name.",
        "instrument_id": "Normalized issuer key used to resolve the same borrower across holders.",
        "seniority": "Tranche seniority, e.g. 'first_lien_senior_secured'. Only first-lien senior "
                     "secured TERM loans are the comparable cross-holder instrument.",
        "maturity": "Maturity date (m/yyyy). Corroborates same-instrument resolution across holders.",
        "par": "Funded par / principal HELD by this holder, in USD. An unfunded revolver/DDTL shows "
               "'—' — do not treat as par. For FX tranches the par is in local currency; exclude "
               "those (see fair_value_mark).",
        "fair_value_mark": MARK_BASIS + ". Compute per tranche; use the current reporting period only; "
                           "exclude non-USD tranches (par would be local-currency, FV USD).",
        "coupon_spread": "Reference rate + spread, e.g. 'S+ 5.00%' (USD/SOFR) vs 'E+'/'SONIA' (FX).",
        "pik_flag": "True if the coupon is paid-in-kind ('PIK').",
        "non_accrual_flag": "True if the holder marks the position non-accrual.",
        "as_of_date": "The CURRENT-period SoI date. A 10-Q embeds two SoIs (current + prior year-end); "
                      "use the current one only.",
    }


def valid_links() -> list:
    """SoI rows link by shared instrument across holders (resolved downstream), not intra-document."""
    return []
