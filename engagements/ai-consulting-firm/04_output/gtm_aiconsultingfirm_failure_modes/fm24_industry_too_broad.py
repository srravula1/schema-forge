"""Industry extracted is a top-level NAICS sector rather than the specific sub-industry — too broad for ICP filtering.

Source: NAICS 2022 industry taxonomy hierarchy (census.gov/naics); Crunchbase category
specificity guidance (crunchbase.com/categories); LinkedIn industry list specificity
notes (linkedin.com/help/linkedin/answer/6957).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_OVERLY_BROAD_INDUSTRIES = frozenset({
    "technology", "tech", "information technology", "it", "services", "business services",
    "professional services", "financial services", "healthcare", "manufacturing",
    "retail", "media", "software", "internet", "industry", "sector",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.industry"})(), "text": "technology"})()
FIXTURE_SOURCE = SourceDoc(text="Acme Corp is a technology company focused on enterprise software.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags industry extractions that are top-level sector labels too broad for meaningful ICP filtering."""
    if entity.label.value != "account.industry":
        return False, None
    industry_lower = entity.text.strip().lower()
    if industry_lower in _OVERLY_BROAD_INDUSTRIES:
        return True, f"industry '{entity.text}' is too broad for ICP filtering; extract specific sub-industry if available"
    return False, None
