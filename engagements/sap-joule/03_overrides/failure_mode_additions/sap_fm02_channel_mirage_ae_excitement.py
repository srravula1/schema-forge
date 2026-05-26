"""
Failure mode: SAP AE excitement without end-customer budget = channel mirage.

An SAP Account Executive refers an account with high enthusiasm. The AE describes
the account as "a perfect Joule account" or "they have budget." We treat the referral
as qualified. After 45+ days in discovery, the end-customer's finance team confirms
there is no IT project budget allocated. The AE was not lying — the CIO had expressed
interest at a QBR — but interest is not budget. The AE has quota incentive to nominate
co-sell partners regardless of end-customer readiness; their enthusiasm is a channel
signal, not a buyer signal.

Source: SAP-Joule engagement, channel interview 2026-05-21.
"L3 — SAP AE-referred retail company. SAP AE was extremely enthusiastic. Turns out
the end-customer's CIO was 'supportive in principle' but had no allocated Joule budget."
"We now require end-customer budget evidence before any co-sell goes active in our CRM."
(Company overview §6, channel interview §2)
"SAP AEs get quota credit for co-sells and have every incentive to refer us into an
account, even if the end-customer has zero Joule budget." (Company overview §6)

Detection trigger: The source document contains strong co-sell language (AE enthusiasm,
co-sell referral framing) combined with Q_BUDGET_CONFIRMED absence AND the budget
evidence coming only from the AE's assertion rather than the end-customer directly.
"""

from __future__ import annotations

import re
from typing import Any

# Co-sell framing language from SAP AEs
_COSELL_LANGUAGE = re.compile(
    r"\b(co.?sell|co sell|referred by SAP|SAP account executive|SAP AE|SAP rep"
    r"|my SAP contact|SAP field|the AE says|our SAP rep says|SAP quota"
    r"|SAP referral|introduce you to)\b",
    re.IGNORECASE,
)

# AE enthusiasm language that does NOT constitute end-customer budget confirmation
_AE_ASSERTION_LANGUAGE = re.compile(
    r"\b(they have budget|ready to move forward|interested in Joule|perfect account"
    r"|great opportunity|they want to|I think they|they should|they might"
    r"|supportive in principle|expressed interest)\b",
    re.IGNORECASE,
)

# Direct end-customer budget evidence (this counterbalances the detection)
_ENDCUSTOMER_BUDGET_LANGUAGE = re.compile(
    r"\b(CIO confirmed|CFO confirmed|budget allocated|PO issued|project code"
    r"|procurement approval|signed by|authorized by|budget line item|opex budget"
    r"|capex budget|board approved|steering committee approved)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type(
    "E",
    (),
    {
        "label": type("L", (), {"value": "qualification.budget_confirmed"})(),
        "text": "they have budget for a Joule pilot this quarter",
        "normalized_value": None,
        "confidence": 0.78,
    },
)()

FIXTURE_SOURCE = type(
    "S",
    (),
    {
        "text": (
            "Our SAP Account Executive referred this account. She says they have budget "
            "and are ready to move forward with a Joule pilot. The CIO expressed interest "
            "at the last QBR. I think they should be able to allocate the funds. "
            "We should set up an intro call as soon as possible."
        )
    },
)()


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect channel mirage: AE excitement without end-customer budget evidence.

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
    if label_value != "qualification.budget_confirmed":
        return False, None

    confidence = getattr(entity, "confidence", 0.0)
    if confidence < 0.5:
        return False, None

    source_text = getattr(source_doc, "text", "") or ""

    has_cosell = bool(_COSELL_LANGUAGE.search(source_text))
    has_ae_assertion = bool(_AE_ASSERTION_LANGUAGE.search(source_text))
    has_endcustomer_evidence = bool(_ENDCUSTOMER_BUDGET_LANGUAGE.search(source_text))

    if not has_cosell:
        return False, None

    if has_ae_assertion and not has_endcustomer_evidence:
        entity_text = getattr(entity, "text", "")
        return (
            True,
            (
                f"Channel mirage: budget evidence {entity_text!r} appears to come from "
                f"SAP AE assertion, not direct end-customer confirmation. "
                f"Co-sell language detected in source, AE-assertion language detected, "
                f"but no direct end-customer budget confirmation (CIO/CFO statement, "
                f"PO, or budget line item). Route to Alliances Owner to verify before "
                f"activating in pipeline."
            ),
        )

    return False, None
