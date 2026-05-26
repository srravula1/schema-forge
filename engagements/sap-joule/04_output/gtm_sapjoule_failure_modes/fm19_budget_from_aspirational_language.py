"""Budget confirmed extracted from aspirational or hypothetical language, not actual budget commitment.

Source: MEDDPICC framework; Clari blog on budget qualification signals (clari.com/blog);
Gong call analysis on budget discovery patterns (gong.io/blog/discovery-questions).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_ASPIRATIONAL_PATTERNS = re.compile(
    r"\b(would like to|hoping to|plan to|considering|evaluating|if we had budget|"
    r"ideally|we might|we may|potentially|in the future|next year|next quarter|"
    r"we're thinking about|exploring options)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "qualification.budget_confirmed"})(), "text": "we're hoping to invest in a solution next quarter"})()
FIXTURE_SOURCE = SourceDoc(text="We're hoping to invest in a solution next quarter if the board approves.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags budget confirmed evidence that uses aspirational, conditional, or hypothetical language."""
    if entity.label.value != "qualification.budget_confirmed":
        return False, None
    combined = (entity.text + " " + source_doc.text).strip()
    if _ASPIRATIONAL_PATTERNS.search(combined):
        return True, "budget confirmation contains aspirational/conditional language; may not be actual commitment"
    return False, None
