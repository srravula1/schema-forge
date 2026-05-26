"""
Failure mode: Big4 / large IT consulting MD relationship without a live prime contract.

A Managing Director at a Big4 SAP practice cultivates us as a potential Joule
subcontractor. We invest in the relationship (partner events, reference calls, joint
proposal preparation) over 3-4 months. The prime contract for the SAP transformation
program is either not won or delayed 12+ months. The MD relationship is real; there
is no billable deal. The signals that triggered the relationship (MD expressed interest,
partner event attendance, proposal prep conversations) are all channel relationship
activity, not closed-deal activity.

Source: SAP-Joule engagement, channel interview 2026-05-21.
"We have been cultivated by two separate SI partners for months, attending their
partner events, doing reference calls, and being presented in proposals — then the
prime contract was either lost to another SI or delayed 12 months." (Channel interview §3)
"We now require a signed prime contract or final-stage LOI before investing delivery
capacity in an SI-partner pursuit." (Company overview §6)
05_failure_modes_interview.md FM-SAP-03.

Detection trigger: Need articulated mentions subcontracting or partner pull-through
language, but the source document does not contain prime contract confirmation language.
The need may be a partner-originated attribution, not an end-customer-confirmed need.
"""

from __future__ import annotations

import re
from typing import Any

# SI-partner pull-through language
_SI_PARTNER_LANGUAGE = re.compile(
    r"\b(subcontract|SI partner|Big4|Big 4|Deloitte|Accenture|Capgemini|KPMG"
    r"|PwC|EY|McKinsey|NTT Data|Wipro|Infosys SAP|Cognizant SAP"
    r"|Managing Director|MD SAP|partner event|prime contract|prime bid"
    r"|transformation program|proposed us as|presented us in)\b",
    re.IGNORECASE,
)

# Prime contract confirmation language
_PRIME_CONTRACT_LANGUAGE = re.compile(
    r"\b(signed prime contract|prime contract signed|SOW signed|LOI signed"
    r"|final.stage LOI|contract executed|master services agreement"
    r"|named subcontractor|SOW slot confirmed|subcontract signed|work order)\b",
    re.IGNORECASE,
)

# Speculative language that indicates the prime is NOT signed yet
_SPECULATIVE_LANGUAGE = re.compile(
    r"\b(bidding on|proposal stage|exploring subcontractors|could be a fit"
    r"|might bring us in|evaluating partners|hope to bring|pending contract"
    r"|waiting to hear|proposal submitted|not yet signed|if we win)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type(
    "E",
    (),
    {
        "label": type("L", (), {"value": "qualification.need_articulated"})(),
        "text": "Deloitte wants us to run the Joule workstream on their S/4 transformation",
        "normalized_value": None,
        "confidence": 0.80,
    },
)()

FIXTURE_SOURCE = type(
    "S",
    (),
    {
        "text": (
            "The Managing Director from Deloitte SAP practice reached out. They are "
            "bidding on a large S/4HANA transformation program and want to include us "
            "as a Joule subcontractor in their proposal. They're hoping to bring us in "
            "if they win. The proposal is submitted but we're waiting to hear. "
            "The MD has been very engaged and we've done three reference calls."
        )
    },
)()


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect partner mirage: Big4 MD relationship without a live prime contract.

    Args:
        entity: An object with .label, .text, .confidence attributes.
        source_doc: An object with .text attribute.

    Returns:
        (True, reason) if the failure mode is detected; (False, None) otherwise.
    """
    label = getattr(entity, "label", None)
    if label is None:
        return False, None

    label_value = label.value if hasattr(label, "value") else str(label)
    if label_value != "qualification.need_articulated":
        return False, None

    confidence = getattr(entity, "confidence", 0.0)
    if confidence < 0.5:
        return False, None

    source_text = getattr(source_doc, "text", "") or ""

    has_si_partner = bool(_SI_PARTNER_LANGUAGE.search(source_text))
    if not has_si_partner:
        return False, None

    has_prime_contract = bool(_PRIME_CONTRACT_LANGUAGE.search(source_text))
    if has_prime_contract:
        return False, None

    has_speculative = bool(_SPECULATIVE_LANGUAGE.search(source_text))
    if not has_speculative:
        return False, None

    entity_text = getattr(entity, "text", "")
    return (
        True,
        (
            f"Partner mirage: need {entity_text!r} attributed to an SI-partner "
            f"relationship but no signed prime contract detected in source. "
            f"SI-partner language and speculative/bidding language present. "
            f"Route to SI-Partner Lead to confirm prime contract status before "
            f"activating in pipeline. Do not invest delivery capacity until "
            f"prime contract is signed or final-stage LOI is confirmed."
        ),
    )
