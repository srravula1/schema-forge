"""Revenue range inferred from funding amount — conflating funding raised with annual revenue.

Source: Apollo.io enrichment accuracy discussion (r/sales, 2024); HubSpot blog on
company data quality pitfalls (hubspot.com/blog/company-data-enrichment).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_FUNDING_TERMS = re.compile(r"\b(raised|funding|round|series [abcde]|seed|venture)\b", re.IGNORECASE)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.revenue_range"})(), "text": "10-50M"})()
FIXTURE_SOURCE = SourceDoc(text="The startup raised $15M in Series A funding last quarter.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags revenue range extracted from text that is clearly about funding, not revenue."""
    if entity.label.value != "account.revenue_range":
        return False, None
    if _FUNDING_TERMS.search(source_doc.text):
        return True, "revenue range may be derived from funding text, not actual revenue"
    return False, None
