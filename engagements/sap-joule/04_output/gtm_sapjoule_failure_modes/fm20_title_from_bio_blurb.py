"""Job title extracted from a speaker bio or past-tense conference bio, not a current role.

Source: AI SDR failure posts on LinkedIn on stale title extraction from event sites (2024);
Sales Hacker article on contact data decay (saleshacker.com).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_BIO_INDICATORS = re.compile(
    r"\b(keynote speaker|panelist|speaker bio|formerly|previously|used to be|was the|"
    r"conference|summit|webinar|at the time of|ex-|former)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "contact.title"})(), "text": "VP of Sales"})()
FIXTURE_SOURCE = SourceDoc(
    url="https://saastr.com/speakers/jane-smith",
    text="Jane Smith, formerly VP of Sales at Acme Corp. Now an advisor.",
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags job titles extracted from speaker bios or conference pages that may reflect past roles."""
    if entity.label.value != "contact.title":
        return False, None
    if _BIO_INDICATORS.search(source_doc.text):
        return True, "job title may be from a speaker bio or conference page reflecting a past role"
    return False, None
