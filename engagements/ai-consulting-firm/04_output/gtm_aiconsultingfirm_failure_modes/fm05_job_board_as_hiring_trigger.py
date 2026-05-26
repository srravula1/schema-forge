"""Hiring trigger extracted from a generic job board aggregator page, not the company's own posting.

Source: r/sales discussion on Apollo intent data including job board noise (2024);
PredictLeads documentation on signal source quality (predictleads.com/signals/hiring).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_JOB_BOARD_DOMAINS = frozenset({
    "indeed.com", "glassdoor.com", "ziprecruiter.com", "monster.com",
    "dice.com", "simplyhired.com", "careerbuilder.com", "talent.com",
    "jooble.org", "jobserve.com",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "signal.hiring_trigger"})(), "text": "hiring 5 SDRs"})()
FIXTURE_SOURCE = SourceDoc(url="https://www.indeed.com/jobs?q=SDR&l=New+York", text="Hiring 5 SDRs in New York.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags hiring trigger sourced from a third-party job board, not the company's own site."""
    if entity.label.value != "signal.hiring_trigger":
        return False, None
    for domain in _JOB_BOARD_DOMAINS:
        if domain in source_doc.url.lower():
            return True, f"hiring trigger from job board aggregator: {domain}"
    return False, None
