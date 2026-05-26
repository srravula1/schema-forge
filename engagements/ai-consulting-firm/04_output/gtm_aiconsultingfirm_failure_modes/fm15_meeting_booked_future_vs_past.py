"""Meeting booked signal extracted from a cancelled or past meeting reference, not an active booking.

Source: Gong call-coaching taxonomy on engagement event accuracy (gong.io/blog);
r/sales discussion on CRM event data hygiene (2024).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_NEGATIVE_INDICATORS = re.compile(
    r"\b(cancelled?|rescheduled|no[- ]show|declined|rejected|missed|didn't? meet|could not meet)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "engagement.meeting_booked"})(), "text": "meeting booked for Thursday"})()
FIXTURE_SOURCE = SourceDoc(text="The Thursday meeting was cancelled by the prospect.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags meeting booked signals when the source text contains cancellation or no-show language."""
    if entity.label.value != "engagement.meeting_booked":
        return False, None
    if _NEGATIVE_INDICATORS.search(source_doc.text):
        return True, "meeting booking may reference a cancelled or failed meeting, not an active booking"
    return False, None
