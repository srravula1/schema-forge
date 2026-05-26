"""Funding stage inferred from company valuation or market cap rather than from an actual funding event.

Source: Crunchbase funding stage taxonomy documentation; PitchBook stage definitions;
r/SaaS discussion on 'unicorn' label misuse in prospecting (2024).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_VALUATION_TERMS = re.compile(
    r"\b(valued at|valuation of|unicorn|decacorn|market cap|worth \$|valued at \$)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.funding_stage"})(), "text": "series_b"})()
FIXTURE_SOURCE = SourceDoc(text="Acme Corp is valued at $1.2B, joining the unicorn club.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags funding stage extracted from valuation language rather than an explicit funding round announcement."""
    if entity.label.value != "account.funding_stage":
        return False, None
    if _VALUATION_TERMS.search(source_doc.text):
        return True, "funding stage may be inferred from valuation/unicorn language rather than a specific round"
    return False, None
