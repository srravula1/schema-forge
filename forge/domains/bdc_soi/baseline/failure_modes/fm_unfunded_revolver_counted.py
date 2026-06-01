"""An unfunded revolver / delayed-draw line counted as a funded position — yields a meaningless mark.

Source: CalPERS ARCC×OBDC run, 2026-06-01. Revolver and delayed-draw rows often show '—' for funded
par (e.g. OBDC PetVet revolver: par 1,830, fair value '—'). A mark requires funded par; these don't
have one and must not enter the comparison.
"""

from __future__ import annotations

from forge.domains.bdc_soi.baseline.failure_modes import SourceDoc
from forge.domains.bdc_soi.baseline.position_mark import PositionMark

_UNFUNDED_TYPES = ("revolv", "delayed draw")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    par = getattr(entity, "par", None)
    mark = getattr(entity, "fair_value_mark", None)
    is_unfunded_type = any(t in source_doc.text.lower() for t in _UNFUNDED_TYPES)
    if is_unfunded_type and mark is not None and (par is None or par == 0):
        return True, (
            "unfunded revolver / delayed-draw line (par '—'/0) should not yield a mark — "
            "exclude undrawn commitments from the cross-holder comparison"
        )
    return False, None


FIXTURE_ENTITY = PositionMark(
    holder="Blue Owl Capital Corp (OBDC)", borrower="PetVet Care Centers, LLC",
    seniority="first_lien_senior_secured", fair_value_mark=100.0, par=0.0, as_of_date="2026-03-31",
)
FIXTURE_SOURCE = SourceDoc(
    text="PetVet Care Centers, LLC First lien senior secured revolving loan S+ 6.00% 11/2029 1,830 1,630 —"
)
