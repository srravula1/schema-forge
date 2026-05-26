"""Contact seniority overestimated — 'Senior Manager' classified as VP or higher.

Source: LinkedIn Sales Navigator title normalization guide; ZoomInfo job-function
taxonomy documentation (developer.zoominfo.com); r/sales discussion on seniority
mismatch in outbound targeting (2024).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_MANAGER_PATTERNS = re.compile(
    r"\b(senior manager|sr\. manager|sr manager|team lead|group manager|program manager)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {
    "label": type("L", (), {"value": "contact.seniority"})(),
    "text": "vp",
    "normalized_value": "vp",
})()
FIXTURE_SOURCE = SourceDoc(text="Jane Smith, Senior Manager of Sales Operations at Acme.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags VP/C-suite seniority assigned to titles that contain manager-level keywords."""
    if entity.label.value != "contact.seniority":
        return False, None
    extracted_seniority = (entity.normalized_value or entity.text).strip().lower()
    if extracted_seniority not in ("vp", "c_suite", "founder"):
        return False, None
    if _MANAGER_PATTERNS.search(source_doc.text):
        return True, "seniority may be inflated; title text suggests manager-level, not VP/C-suite"
    return False, None
