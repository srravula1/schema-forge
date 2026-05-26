"""Need articulated evidence extracted from the vendor's own marketing copy, not the prospect's voice.

Source: MEDDPICC framework on implicit vs explicit need (public documentation);
Gong call coaching on discovery vs marketing-speak (gong.io/blog/discovery-calls).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_MARKETING_COPY_INDICATORS = frozenset({
    "/blog/", "/resources/", "/ebooks/", "/whitepapers/", "/webinars/",
    "our solution", "we help you", "our platform", "we enable",
    "increase revenue", "reduce costs", "save time", "be more productive",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "qualification.need_articulated"})(), "text": "increase revenue and reduce costs"})()
FIXTURE_SOURCE = SourceDoc(
    url="https://vendor.com/blog/top-sales-challenges",
    text="Companies using our solution increase revenue and reduce costs by 30%.",
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags need-articulated evidence that appears to come from vendor marketing copy rather than the prospect's own words."""
    if entity.label.value != "qualification.need_articulated":
        return False, None
    url_lower = source_doc.url.lower()
    text_lower = source_doc.text.lower()
    for indicator in _MARKETING_COPY_INDICATORS:
        if indicator in url_lower or indicator in text_lower:
            return True, "need articulated may be vendor marketing copy, not prospect-stated need"
    return False, None
