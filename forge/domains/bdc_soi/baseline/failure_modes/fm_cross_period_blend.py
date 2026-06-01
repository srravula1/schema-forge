"""A row whose text spans two reporting periods — the SoI was not period-segmented (blend risk).

Source: CalPERS ARCC×OBDC run, 2026-06-01. Each 10-Q embeds the current-period SoI AND the prior
fiscal year-end SoI as a comparative. Parsing both and blending them corrupted par (e.g. OBDC Cambrex
appeared as both 916-par/2025-12-31 and 785-par/2026-03-31). Only the current period is valid.
"""

from __future__ import annotations

import re

from forge.domains.bdc_soi.baseline.failure_modes import SourceDoc
from forge.domains.bdc_soi.baseline.position_mark import PositionMark

_PERIOD_RE = re.compile(
    r"(?:march|june|september|december)\s+\d{1,2},\s+20\d{2}", re.IGNORECASE
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    periods = {m.group(0).lower() for m in _PERIOD_RE.finditer(source_doc.text)}
    if len(periods) >= 2:
        return True, (
            f"row text spans two reporting periods {sorted(periods)} — SoI not period-segmented; "
            "use the current period only"
        )
    return False, None


FIXTURE_ENTITY = PositionMark(
    holder="Blue Owl Capital Corp (OBDC)", borrower="Cambrex Corporation",
    seniority="first_lien_senior_secured", fair_value_mark=99.78, par=916.0, as_of_date="ambiguous",
)
FIXTURE_SOURCE = SourceDoc(
    text="As of March 31, 2026 ... Cambrex Corporation First lien senior secured loan ... "
         "As of December 31, 2025 ... Cambrex Corporation First lien senior secured loan"
)
