"""
Failure mode: Clean core SAP initiative interpreted as immediate AI readiness.

An account discussing their "clean core SAP strategy" is flagged as Joule-ready.
In reality, clean core is a prerequisite to S/4HANA migration — it involves removing
custom code and side-by-side extensions to prepare for S/4HANA cloud deployment.
The clean core work itself does not mean the account has S/4HANA, has BTP, has Joule
access, or has a named AI project. Clean core can precede a RISE migration that will
eventually include Joule — but the Joule readiness window is 12-24 months away when
the account is only in the clean core phase.

This failure mode is the inverse of FM-SAP-09 (clean core that DID signal readiness,
missed). The key distinguishing evidence: does the clean core initiative mention a
target RISE/S/4 migration date within 12 months? If yes, it is a warm nurture signal.
If no RISE target is mentioned, the clean core work is preparatory and the account
remains 18-24 months away from Joule readiness.

Source: SAP-Joule engagement, failure modes interview 2026-05-22.
"An account was publicly discussing their 'clean core SAP strategy'. This was treated
as a signal that they were Joule-ready. In reality, clean core work is a prerequisite
to S/4HANA migration, not a signal of AI readiness." (FM-SAP-07)
"The account was 18-24 months from being Joule-implementable." (05_failure_modes_interview.md)
SAP Clean Core guidance: https://www.sap.com/products/erp/s4hana-erp/clean-core.html

Detection trigger: Intent topic entity references clean core AND the source document
does not contain a confirmed migration timeline or RISE contract announcement within 12 months.
"""

from __future__ import annotations

import re
from typing import Any

# Clean core language
_CLEAN_CORE_PATTERN = re.compile(
    r"\b(clean core|clean-core|SAP clean core|ABAP custom code reduction"
    r"|custom code elimination|side.by.side extensions|ABAP cloud"
    r"|SAP clean core strategy|clean core assessment|BAdI|BADI)\b",
    re.IGNORECASE,
)

# Near-term migration language (counterbalances the detection — indicates real readiness)
_NEAR_TERM_MIGRATION = re.compile(
    r"\b(RISE contract|RISE subscription|S/4 go.live|go.live within"
    r"|migrat\w+ in \d{4}|migration target|target date|Q[1-4] 20\d\d"
    r"|by Q[1-4]|this year|next year|within 12 months|within the year"
    r"|in 2025|in 2026|in 2027 H1|planned migration|confirmed migration)\b",
    re.IGNORECASE,
)

# Preparatory language without timeline (indicates early-stage, not imminent)
_PREPARATORY_LANGUAGE = re.compile(
    r"\b(preparing for|getting ready|laying the groundwork|foundation for"
    r"|prereq\w*|prerequisite|first step toward|before we migrate"
    r"|before the migration|evaluation phase|assessment phase|planning phase)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type(
    "E",
    (),
    {
        "label": type("L", (), {"value": "signal.intent_topic"})(),
        "text": "clean core SAP strategy",
        "normalized_value": "clean core SAP",
        "confidence": 0.78,
    },
)()

FIXTURE_SOURCE = type(
    "S",
    (),
    {
        "text": (
            "The company announced a clean core SAP initiative led by their SAP CoE team. "
            "The initiative focuses on removing custom ABAP code and side-by-side extensions "
            "as part of their preparation for cloud migration. They are in the evaluation "
            "phase, laying the groundwork for a future S/4HANA migration. No specific "
            "migration timeline has been announced yet."
        )
    },
)()


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect clean core initiative misinterpreted as immediate Joule AI readiness.

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
    if label_value != "signal.intent_topic":
        return False, None

    confidence = getattr(entity, "confidence", 0.0)
    if confidence < 0.4:
        return False, None

    entity_text = getattr(entity, "text", "") or ""
    normalized = getattr(entity, "normalized_value", "") or ""

    # Check if this is a clean core intent topic
    is_clean_core = bool(
        _CLEAN_CORE_PATTERN.search(entity_text)
        or _CLEAN_CORE_PATTERN.search(normalized)
    )
    if not is_clean_core:
        return False, None

    source_text = getattr(source_doc, "text", "") or ""

    # If a near-term migration timeline is confirmed, this is a warm signal, not a false positive
    has_near_term_migration = bool(_NEAR_TERM_MIGRATION.search(source_text))
    if has_near_term_migration:
        return False, None

    # If preparatory language is present without a timeline, flag as false positive
    has_preparatory = bool(_PREPARATORY_LANGUAGE.search(source_text))
    if not has_preparatory:
        return False, None

    return (
        True,
        (
            f"Clean core false positive: intent topic {entity_text!r} indicates clean "
            f"core SAP work but no confirmed migration timeline detected. Clean core is "
            f"a prerequisite to S/4HANA migration, not a signal of Joule readiness. "
            f"Without a confirmed RISE/S/4 migration date within 12 months, this account "
            f"is 18-24 months from Joule implementation readiness. "
            f"Flag as S_CLEAN_CORE_INITIATIVE nurture signal; do not activate in pipeline."
        ),
    )
