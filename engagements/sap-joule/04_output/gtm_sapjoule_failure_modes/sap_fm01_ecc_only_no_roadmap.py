"""
Failure mode: ECC-only account flagged as pilot-ready despite no S/4HANA roadmap.

An account running SAP ECC 6.0 with a large SAP user base is scored as high-priority
because of the large SAP footprint. Reality: without a funded S/4HANA migration program
or a named RISE/GROW contract, the account cannot access SAP Joule (which requires
S/4HANA or BTP). The large ECC footprint is a "SAP user" signal, not a "Joule buyer"
signal. Until the account has a confirmed S/4 migration timeline or BTP entitlement,
it is a multi-year nurture account, not an active pilot candidate.

Source: SAP-Joule engagement, ICP interview 2026-05-21.
"L1 (energy company, DQ'd after Readiness Assessment). ECC 6.0, no S/4 roadmap,
~6,500 SAP users. They wanted 'AI in SAP' but the ECC architecture made Joule
integration prohibitively complex." (ICP interview §3)
"SAP Joule requires S/4HANA or RISE with SAP; it is not available on ECC 6.0
without a migration project already in progress."
(SAP Help Portal: https://help.sap.com/docs/joule, System Requirements section)

Detection trigger: A_TECH_STACK_ITEM entity mentions SAP ECC (or ECC 6.0) as the
ERP core AND there is no S/4HANA tech stack entity present AND there is no
S_S4_MIGRATION_TIMELINE signal in the source document. When all three conditions
are met and the entity has high confidence, flag as ECC-only false-positive.
"""

from __future__ import annotations

import re
from typing import Any

# Patterns that indicate SAP ECC presence
_ECC_PATTERN = re.compile(
    r"\b(ECC|ECC\s*6\.0|SAP\s+ECC|R/3|mySAP|SAP\s+ERP\s+6)\b",
    re.IGNORECASE,
)

# Patterns that indicate S/4HANA presence (counterbalances the ECC signal)
_S4_PATTERN = re.compile(
    r"\b(S/4HANA|S4HANA|S/4|RISE\s+with\s+SAP|GROW\s+with\s+SAP|S/4HANA\s+Cloud|RISE)\b",
    re.IGNORECASE,
)

# Patterns that indicate a migration timeline (counterbalances the ECC signal)
_MIGRATION_PATTERN = re.compile(
    r"\b(migrat|migration\s+plan|roadmap|go.live|greenfield|brownfield|S/4\s+project)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type(
    "E",
    (),
    {
        "label": type("L", (), {"value": "account.tech_stack_item"})(),
        "text": "SAP ECC 6.0",
        "normalized_value": "sap_ecc_6",
        "confidence": 0.92,
    },
)()

FIXTURE_SOURCE = type(
    "S",
    (),
    {
        "text": (
            "The company runs SAP ECC 6.0 for all financial and materials management "
            "operations, with approximately 3,200 licensed SAP users across 8 plants. "
            "The SAP landscape has been stable for seven years. No cloud migration "
            "program has been announced; the IT team plans to maintain the current "
            "ECC installation through the next budget cycle."
        )
    },
)()


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect ECC-only account incorrectly flagged as Joule pilot-ready.

    Args:
        entity: An object with .label, .text, .normalized_value, .confidence attributes.
        source_doc: An object with .text attribute (the source document text).

    Returns:
        (True, reason) if the failure mode is detected; (False, None) otherwise.
    """
    label = getattr(entity, "label", None)
    if label is None:
        return False, None

    label_value = label.value if hasattr(label, "value") else str(label)
    if label_value != "account.tech_stack_item":
        return False, None

    confidence = getattr(entity, "confidence", 0.0)
    if confidence < 0.5:
        return False, None

    entity_text = getattr(entity, "text", "") or ""
    normalized = getattr(entity, "normalized_value", "") or ""

    # Check if the entity is specifically an ECC reference
    is_ecc = bool(_ECC_PATTERN.search(entity_text)) or "ecc" in normalized.lower()
    if not is_ecc:
        return False, None

    source_text = getattr(source_doc, "text", "") or ""

    # If S/4HANA is also mentioned, the account may already be on the migration path
    has_s4 = bool(_S4_PATTERN.search(source_text))
    if has_s4:
        return False, None

    # If migration language is present, do not flag
    has_migration = bool(_MIGRATION_PATTERN.search(source_text))
    if has_migration:
        return False, None

    return (
        True,
        (
            f"ECC-only false positive: entity {entity_text!r} indicates SAP ECC "
            f"without evidence of S/4HANA migration roadmap or RISE/GROW subscription. "
            f"SAP Joule requires S/4HANA or BTP; this account is not Joule-ready "
            f"without a confirmed migration program. Recommend nurture, not active pipeline."
        ),
    )
