"""Pain point extracted from a vendor's own case study page — the pain is historical, not current.

Source: r/sales discussion on Gong/Salesforce case study scraping producing false pain signals
(2024); Predictable Revenue blog on intent signal false positives from case studies.
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_CASE_STUDY_INDICATORS = frozenset({
    "case study", "customer story", "success story", "case_study",
    "/customers/", "/case-studies/", "/success-stories/", "/testimonials/",
    "how we helped", "how acme helped",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "signal.pain_point_mention"})(), "text": "we couldn't scale our pipeline"})()
FIXTURE_SOURCE = SourceDoc(url="https://vendor.com/customers/acme-success-story", text="Before using us, Acme said: 'we couldn't scale our pipeline'.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags pain points extracted from vendor case study pages, which represent resolved past pain."""
    if entity.label.value != "signal.pain_point_mention":
        return False, None
    url_lower = source_doc.url.lower()
    text_lower = source_doc.text.lower()
    for indicator in _CASE_STUDY_INDICATORS:
        if indicator in url_lower or indicator in text_lower:
            return True, "pain point extracted from vendor case study; pain may be historical, not current"
    return False, None
