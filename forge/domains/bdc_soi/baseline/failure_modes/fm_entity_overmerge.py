"""Two distinct issuers collapsed under one normalized key — an over-eager entity-resolution merge.

Source: CalPERS ARCC×OBDC run, 2026-06-01. Aggressive name normalization risks merging distinct
borrowers that share a leading token (e.g. 'Bamboo Purchaser, Inc.' — a nursery rollup — vs
'Bamboo US BidCo LLC' — a biopharma). The resolver must keep them separate and corroborate with
instrument attributes (seniority + maturity), not collapse on name alone.
"""

from __future__ import annotations

from forge.domains.bdc_soi.baseline.failure_modes import SourceDoc
from forge.domains.bdc_soi.baseline.position_mark import PositionMark


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    md = getattr(source_doc, "metadata", {}) or {}
    if md.get("distinct_instruments_under_one_key"):
        key = md.get("norm_key", "?")
        members = md.get("members", [])
        return True, (
            f"normalized key '{key}' merges distinct issuers {members} — do not collapse on name; "
            "corroborate with seniority + maturity"
        )
    return False, None


FIXTURE_ENTITY = PositionMark(
    holder="Ares Capital Corp (ARCC)", borrower="Bamboo Purchaser, Inc.",
    seniority="first_lien_senior_secured", fair_value_mark=47.6, par=8.2, as_of_date="2026-03-31",
)
FIXTURE_SOURCE = SourceDoc(
    text="Bamboo Purchaser, Inc. vs Bamboo US BidCo LLC",
    metadata={
        "distinct_instruments_under_one_key": True,
        "norm_key": "bamboo",
        "members": ["Bamboo Purchaser, Inc.", "Bamboo US BidCo LLC"],
    },
)
