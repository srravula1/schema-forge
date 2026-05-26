"""Tech adoption signal extracted from a vendor's partner/integration page, not the prospect's own adoption.

Source: BuiltWith technology detection methodology (builtwith.com/about); Clay community
thread on tech stack enrichment false positives from partner listings (2024).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_PARTNER_INDICATORS = frozenset({
    "/partners/", "/integrations/", "/ecosystem/", "/marketplace/",
    "partner page", "integration directory", "app marketplace",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "signal.tech_adoption"})(), "text": "deployed Snowflake"})()
FIXTURE_SOURCE = SourceDoc(
    url="https://snowflake.com/partners/acme-corp",
    text="Acme Corp is a certified Snowflake partner offering data migration services.",
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags tech adoption signals from partner/integration directories rather than the prospect's own content."""
    if entity.label.value != "signal.tech_adoption":
        return False, None
    url_lower = source_doc.url.lower()
    text_lower = source_doc.text.lower()
    for indicator in _PARTNER_INDICATORS:
        if indicator in url_lower or indicator in text_lower:
            return True, "tech adoption signal may come from vendor partner page, not prospect's own adoption"
    return False, None
