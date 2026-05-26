"""Funding trigger extracted from announcement that is >12 months old, not a fresh signal.

Source: Clay community discussion on stale enrichment data causing false outbound triggers
(clay.com community; multiple threads 2024-2025); PredictLeads trigger event freshness docs
(predictleads.com/signals).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "signal.funding_trigger"})(), "text": "raised $15M Series A"})()
FIXTURE_SOURCE = SourceDoc(text="In 2021 the company raised a $15M Series A round led by Accel.")


_STALE_YEAR_PATTERN = re.compile(r"\b(201[0-9]|2020|2021|2022)\b")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags funding trigger text referencing a year likely more than 12 months past."""
    if entity.label.value != "signal.funding_trigger":
        return False, None
    match = _STALE_YEAR_PATTERN.search(source_doc.text)
    if match:
        return True, f"funding trigger may reference stale year: {match.group(0)}"
    return False, None
