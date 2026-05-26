"""Model extracts intent signal from the vendor's own product page, not a prospect signal.

Source: 6sense published guidance on first-party vs third-party intent
(6sense.com/platform/intent-data); r/sales thread on Apollo false intent signals (2024).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "signal.intent_topic"})(), "text": "data warehouse solutions"})()
FIXTURE_SOURCE = SourceDoc(url="https://acme.com/products/data-warehouse", text="We offer best-in-class data warehouse solutions.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags intent extracted from vendor's own /products or /solutions page."""
    if entity.label.value != "signal.intent_topic":
        return False, None
    url = source_doc.url.lower()
    if any(seg in url for seg in ("/product", "/solution", "/platform", "/feature")):
        return True, f"intent extracted from vendor's own product/solution page: {source_doc.url}"
    return False, None
