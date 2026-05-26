"""Timeline extracted from generic fiscal year or annual planning language, not a specific buying timeline.

Source: MEDDPICC compelling event definition (public framework); Clari blog on timeline
qualification (clari.com/blog/meddpicc-timeline); Winning by Design SPICED framework
on timing indicators (winningbydesign.com).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_FISCAL_GENERIC = re.compile(
    r"\b(next fiscal year|end of year|eoy|eofy|annual budget|annual planning|"
    r"fiscal [0-9]{2,4}|fy[0-9]{2,4}|q[1-4] [0-9]{4}|next quarter|this year|"
    r"sometime this year|when budget is approved|pending board approval)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "qualification.timeline_stated"})(), "text": "next fiscal year"})()
FIXTURE_SOURCE = SourceDoc(text="We're planning to evaluate solutions next fiscal year during annual planning.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags timeline evidence that is generic fiscal/planning language without a specific compelling event or deadline."""
    if entity.label.value != "qualification.timeline_stated":
        return False, None
    combined = entity.text + " " + source_doc.text
    if _FISCAL_GENERIC.search(combined):
        return True, "timeline is generic fiscal/planning language; look for a specific compelling event or deadline"
    return False, None
