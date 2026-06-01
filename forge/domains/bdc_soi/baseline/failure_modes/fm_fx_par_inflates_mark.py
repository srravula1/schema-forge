"""A mark computed from a foreign-currency par against a USD fair value — inflates the mark above par.

Source: CalPERS ARCC×OBDC run, 2026-06-01. OBDC's Bamboo and Flexera EUR term loans show par in € but
amortized cost / fair value in USD; FV/par then faked marks of 104.99 and 102.36. USD-only from here.
"""

from __future__ import annotations

from forge.domains.bdc_soi.baseline.failure_modes import SourceDoc
from forge.domains.bdc_soi.baseline.position_mark import PositionMark

_FX_MARKERS = ("€", "£", "E+", "Euribor", "SONIA", "SA+", "EUR term", "GBP term")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    mark = getattr(entity, "fair_value_mark", None)
    if mark is None:
        return False, None
    if any(m in source_doc.text for m in _FX_MARKERS) and mark > 100.5:
        return True, (
            f"FX tranche (non-USD par vs USD fair value): FV/par={mark} is not a valid mark — "
            "exclude non-USD tranches from the cross-holder comparison"
        )
    return False, None


FIXTURE_ENTITY = PositionMark(
    holder="Blue Owl Capital Corp (OBDC)", borrower="Bamboo US BidCo LLC",
    seniority="first_lien_senior_secured", fair_value_mark=115.2, par=4.65, as_of_date="2026-03-31",
)
FIXTURE_SOURCE = SourceDoc(
    text="Bamboo US BidCo LLC First lien senior secured EUR term loan E+ 5.00% 9/2030 € 4,650 4,825 5,358"
)
