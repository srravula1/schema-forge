"""A senior secured term-loan mark outside a plausible band — almost always a column/row misattribution.

Source: CalPERS ARCC×OBDC run, 2026-06-01. Dropping empty SoI cells collapsed columns, so FV/par
occasionally divided by a wrong cell (a share count, an equity line) and produced marks like 149.
A first-lien senior secured term loan marks in ~[60, 103]; anything outside is a parse error to review.
"""

from __future__ import annotations

from forge.domains.bdc_soi.baseline.failure_modes import SourceDoc
from forge.domains.bdc_soi.baseline.position_mark import PositionMark

_LO, _HI = 50.0, 103.0


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    mark = getattr(entity, "fair_value_mark", None)
    if mark is None:
        return False, None
    if mark < _LO or mark > _HI:
        return True, (
            f"mark {mark} outside plausible [{_LO}, {_HI}] for a senior secured term loan — "
            "likely column/row misattribution (FV divided by the wrong cell)"
        )
    return False, None


FIXTURE_ENTITY = PositionMark(
    holder="Ares Capital Corp (ARCC)", borrower="APG Intermediate Holdings Corporation",
    seniority="first_lien_senior_secured", fair_value_mark=149.0, par=6.3, as_of_date="2026-03-31",
)
FIXTURE_SOURCE = SourceDoc(
    text="APG Intermediate Holdings Corporation Class A membership units 01/2020 9,750,000 9.8 6.3"
)
