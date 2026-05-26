"""
Failure mode: RISE with SAP migration interpreted as Joule AI-implementation intent.

An account is reported as "migrating to RISE with SAP" and scored as a Joule pilot
candidate. In reality, RISE with SAP migration is a commercial and infrastructure
change — it moves the account from an on-premises SAP license to a cloud subscription
model. RISE migration is managed by an incumbent SI; it does not inherently include
an AI or Joule workstream.

RISE migration is a necessary but NOT sufficient signal for Joule implementation intent.
The account may complete the RISE migration entirely without any Joule activation if
there is no named AI project within the RISE program. The test: is there a named Joule
or BTP AI workstream in the RISE program? If the RISE migration is running without an
AI workstream, the account is a 12-18 month nurture, not an active pilot candidate.

Source: SAP-Joule engagement, qualification interview 2026-05-22.
"RISE migration mistaken for AI-impl intent." (Qualification interview §4, FM-SAP-05)
"A company migrating to RISE with SAP is an SAP implementation project; it does NOT
automatically mean they are buying a Joule implementation." (05_failure_modes_interview.md)
"RISE migration is a necessary but not sufficient condition." (Company overview §6)

Detection trigger: Tech adoption entity mentions RISE with SAP AND the source document
does not contain Joule-specific or BTP AI Core-specific project language within the
RISE migration context.
"""

from __future__ import annotations

import re
from typing import Any

# RISE migration language
_RISE_PATTERN = re.compile(
    r"\b(RISE with SAP|RISE migration|migrating to RISE|RISE contract"
    r"|RISE subscription|RISE implementation|RISE program|RISE project)\b",
    re.IGNORECASE,
)

# Joule or BTP AI Core project language (counterbalances the detection)
_JOULE_PROJECT_LANGUAGE = re.compile(
    r"\b(Joule implementation|Joule pilot|Joule workstream|Joule project"
    r"|BTP AI Core|GenAI Hub|AI workstream|AI in RISE|Joule use case"
    r"|activate Joule|enable Joule|Joule for|AI uplift|intelligent automation"
    r"|AI-assisted|AI-enabled in SAP)\b",
    re.IGNORECASE,
)

# Infrastructure/commercial RISE language that indicates non-AI migration
_INFRASTRUCTURE_LANGUAGE = re.compile(
    r"\b(cloud migration|data center|infrastructure|license conversion"
    r"|cloud subscription|commercial migration|BASIS team|landscape migration"
    r"|system migration|technical migration|cloud lift)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type(
    "E",
    (),
    {
        "label": type("L", (), {"value": "signal.tech_adoption"})(),
        "text": "The company is migrating to RISE with SAP",
        "normalized_value": "sap_rise",
        "confidence": 0.88,
    },
)()

FIXTURE_SOURCE = type(
    "S",
    (),
    {
        "text": (
            "The company announced their migration to RISE with SAP, a three-year "
            "cloud transformation program managed by Capgemini. The RISE migration "
            "covers commercial license conversion, infrastructure migration from "
            "on-premises data centers, and BASIS team upskilling. The project is "
            "currently in the planning phase for the cloud migration workstreams."
        )
    },
)()


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect RISE migration misinterpreted as Joule AI-implementation intent.

    Args:
        entity: An object with .label, .text, .normalized_value, .confidence attributes.
        source_doc: An object with .text attribute.

    Returns:
        (True, reason) if the failure mode is detected; (False, None) otherwise.
    """
    label = getattr(entity, "label", None)
    if label is None:
        return False, None

    label_value = label.value if hasattr(label, "value") else str(label)
    if label_value != "signal.tech_adoption":
        return False, None

    confidence = getattr(entity, "confidence", 0.0)
    if confidence < 0.5:
        return False, None

    entity_text = getattr(entity, "text", "") or ""
    normalized = getattr(entity, "normalized_value", "") or ""

    # Check if this entity is about RISE with SAP
    is_rise = bool(_RISE_PATTERN.search(entity_text)) or "rise" in normalized.lower()
    if not is_rise:
        return False, None

    source_text = getattr(source_doc, "text", "") or ""

    # If Joule or AI project language is present, the RISE migration includes AI — not a false positive
    has_joule_project = bool(_JOULE_PROJECT_LANGUAGE.search(source_text))
    if has_joule_project:
        return False, None

    # If purely infrastructure language, flag as potential false positive
    has_infrastructure = bool(_INFRASTRUCTURE_LANGUAGE.search(source_text))
    if not has_infrastructure:
        return False, None

    return (
        True,
        (
            f"RISE migration false positive: tech adoption entity {entity_text!r} "
            f"indicates RISE with SAP migration but no Joule or BTP AI Core project "
            f"language detected. RISE migration is a commercial/infrastructure change; "
            f"it does not automatically include Joule activation. Confirm whether the "
            f"RISE program includes a named AI workstream before treating as Joule "
            f"implementation intent. Recommend nurture until AI workstream is confirmed."
        ),
    )
