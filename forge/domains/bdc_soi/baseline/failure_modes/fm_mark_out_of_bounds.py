"""A term-loan mark with fair value ABOVE par — implausible for a funded USD loan; FX or misattribution.

Source: CalPERS ARCC×OBDC run, 2026-06-01. Dropping empty SoI cells collapsed columns, so FV/par
occasionally divided by a wrong cell and produced marks like 149; FX tranches (EUR par vs USD FV)
produced 104.99. Only an UPPER bound is reliable: a USD term loan cannot mark above ~par. A LOW mark
is NOT an error — distressed first-lien loans legitimately mark in the single digits to 40s (real,
verified in the same run: Pluralsight 5.63, Walker Edison 0.94). Flagging low marks would false-alarm
on exactly the distressed names the engine exists to surface, so this gate is upper-bound only.
"""

from __future__ import annotations

from forge.domains.bdc_soi.baseline.failure_modes import SourceDoc
from forge.domains.bdc_soi.baseline.position_mark import PositionMark

_HI = 103.0


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    mark = getattr(entity, "fair_value_mark", None)
    if mark is None:
        return False, None
    if mark > _HI:
        return True, (
            f"mark {mark} > {_HI} (fair value exceeds par) for a USD term loan — "
            "likely FX or column misattribution"
        )
    return False, None


FIXTURE_ENTITY = PositionMark(
    holder="Ares Capital Corp (ARCC)", borrower="APG Intermediate Holdings Corporation",
    seniority="first_lien_senior_secured", fair_value_mark=149.0, par=6.3, as_of_date="2026-03-31",
)
FIXTURE_SOURCE = SourceDoc(
    text="APG Intermediate Holdings Corporation Class A membership units 01/2020 9,750,000 9.8 6.3"
)
