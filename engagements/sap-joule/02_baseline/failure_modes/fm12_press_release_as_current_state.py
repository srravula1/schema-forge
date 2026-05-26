"""Account attributes extracted from a press release may reflect an announced future state, not current.

Source: Predictable Revenue blog on enrichment data freshness (predictablerevenue.com);
Sales Hacker article on data decay in outbound (saleshacker.com, 2024).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_PRESS_RELEASE_INDICATORS = re.compile(
    r"\b(press release|for immediate release|newswire|prnewswire|businesswire|globe newswire|pr\.com)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.employee_range"})(), "text": "1001-5000"})()
FIXTURE_SOURCE = SourceDoc(
    url="https://prnewswire.com/releases/acme-announces-expansion",
    text="FOR IMMEDIATE RELEASE: Acme Corp announces plan to grow to 5,000 employees by 2026.",
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags account attributes extracted from press releases that may be forward-looking announcements."""
    if entity.label.value not in (
        "account.employee_range", "account.revenue_range", "account.hq_location", "account.funding_stage"
    ):
        return False, None
    if (
        _PRESS_RELEASE_INDICATORS.search(source_doc.url)
        or _PRESS_RELEASE_INDICATORS.search(source_doc.text)
    ):
        return True, "account attribute extracted from press release; may reflect future/announced state, not current"
    return False, None
