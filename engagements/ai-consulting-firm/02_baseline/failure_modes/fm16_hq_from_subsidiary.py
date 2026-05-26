"""HQ location extracted from a subsidiary office page, not the parent company's headquarters.

Source: Clay community posts on ZoomInfo/Clearbit HQ location enrichment errors for
multi-national companies (2024); Apollo.io help docs on company location data.
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_SUBSIDIARY_INDICATORS = frozenset({
    "regional office", "branch office", "subsidiary", "division",
    "our office in", "office in", "location in", "we are located in",
    "/office/", "/location/", "/contact-us/", "contact-us", "/contact/",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.hq_location"})(), "text": "Austin, TX"})()
FIXTURE_SOURCE = SourceDoc(
    url="https://bigcorp.com/contact-us",
    text="Our Austin, TX office is located at 123 Main Street. Visit our headquarters page for global offices.",
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags HQ location extracted from a page that describes a regional/subsidiary office."""
    if entity.label.value != "account.hq_location":
        return False, None
    url_lower = source_doc.url.lower()
    text_lower = source_doc.text.lower()
    for indicator in _SUBSIDIARY_INDICATORS:
        if indicator in url_lower or indicator in text_lower:
            return True, "HQ location may be a subsidiary/regional office, not corporate headquarters"
    return False, None
