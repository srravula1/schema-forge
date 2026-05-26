"""Employee count extracted as exact number placed in wrong bucket (e.g. 201 employees → '51-200').

Source: Salesforce lead scoring standard documentation on headcount normalization
(trailhead.salesforce.com); HubSpot company size property documentation.
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_NUMBER_PATTERN = re.compile(r"\b(\d{2,5})\s*(?:employees?|people|staff|headcount|team members?)\b", re.IGNORECASE)

_BUCKET_MAP = [
    (1, 10, "1-10"),
    (11, 50, "11-50"),
    (51, 200, "51-200"),
    (201, 1000, "201-1000"),
    (1001, 5000, "1001-5000"),
]


def _correct_bucket(n: int) -> str:
    for lo, hi, label in _BUCKET_MAP:
        if lo <= n <= hi:
            return label
    return "5000+"


FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.employee_range"})(), "text": "51-200"})()
FIXTURE_SOURCE = SourceDoc(text="The company has 201 employees across three offices.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags employee range bucket that doesn't match the exact headcount stated in the source text."""
    if entity.label.value != "account.employee_range":
        return False, None
    match = _NUMBER_PATTERN.search(source_doc.text)
    if not match:
        return False, None
    exact_count = int(match.group(1))
    correct = _correct_bucket(exact_count)
    if correct != entity.text.strip():
        return True, f"employee count {exact_count} should map to '{correct}', got '{entity.text}'"
    return False, None
