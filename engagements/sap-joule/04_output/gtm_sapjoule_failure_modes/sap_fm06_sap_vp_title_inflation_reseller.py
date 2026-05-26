"""
Failure mode: "SAP VP" title at a small SAP reseller or boutique SI treated
as SAP SE co-sell contact.

A contact with the title "VP of SAP Consulting" or "VP, SAP Practice" at a small
SAP boutique reseller or regional SI is flagged as a SAP-field co-sell contact
(sap_field affiliation). In reality, this is a senior individual contributor at a
10-50 person shop that resells or implements SAP but has no co-sell relationship
with SAP SE and cannot introduce us to end-customer accounts via any official
SAP partner program.

The "SAP VP" title refers to their practice area specialization, not an SAP SE
employment relationship. SAP SE co-sell contacts must be SAP SE employees with
co-sell portal access — they are Regional VPs, Area VPs, or Account Executives
employed directly by SAP SE, not by a partner firm.

Source: SAP-Joule engagement, ICP interview 2026-05-21.
"'SAP VP' title inflation at a small reseller. We have had contacts with 'VP of
SAP Consulting' at 10-person reseller shops who cannot make a buying decision for
themselves, let alone introduce us to their end customers." (ICP interview §4)
"Title inflation in the SAP ecosystem is significant." (Qualification interview §4)
05_failure_modes_interview.md FM-SAP-06.

Detection trigger: Contact title contains "SAP" and "VP" or "Vice President" AND
the company in the source doc appears to be a small SAP reseller/boutique SI
(employee count or language indicates < 200 employees at a consulting/reselling firm).
"""

from __future__ import annotations

import re
from typing import Any

# Patterns that indicate a SAP-field-like title
_SAP_VP_TITLE_PATTERN = re.compile(
    r"\b(VP|Vice President|Vice-President)\b.*\bSAP\b"
    r"|\bSAP\b.*\b(VP|Vice President|Vice-President)\b"
    r"|\bSAP\s+(Practice|Consulting|Services|Solutions)\s+(VP|Lead|Head|Director|Partner)\b",
    re.IGNORECASE,
)

# Small partner/reseller framing (indicates not SAP SE employee)
_SMALL_PARTNER_LANGUAGE = re.compile(
    r"\b(SAP partner|SAP reseller|SAP boutique|SAP consulting firm"
    r"|SAP implementation partner|SAP VAR|value-added reseller"
    r"|gold partner|silver partner|platinum partner|SAP certified partner"
    r"|regional SAP|boutique SI|specialist SAP firm)\b",
    re.IGNORECASE,
)

# SAP SE employment markers (counterbalances the detection — real SAP SE employees)
_SAP_SE_EMPLOYEE_MARKERS = re.compile(
    r"\b(SAP SE|SAP AG|employed by SAP|SAP account executive|SAP AE team"
    r"|SAP sales team|SAP regional VP|SAP area VP|SAP field organization"
    r"|SAP co.?sell|co.?sell program|SAP partner portal|co.?sell portal)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type(
    "E",
    (),
    {
        "label": type("L", (), {"value": "contact.title"})(),
        "text": "VP of SAP Consulting",
        "normalized_value": "vp|sap_field",
        "confidence": 0.85,
    },
)()

FIXTURE_SOURCE = type(
    "S",
    (),
    {
        "text": (
            "Marcus Heinz, VP of SAP Consulting at Nexus SAP Partners — a boutique SAP "
            "implementation partner with 35 consultants specializing in SAP Business One "
            "and S/4HANA for mid-market companies. Nexus is an SAP Gold Partner serving "
            "the DACH region. Marcus reached out on LinkedIn expressing interest in "
            "collaborating on Joule projects."
        )
    },
)()


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect title inflation: SAP VP at a boutique reseller mistaken for SAP SE co-sell.

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
    if label_value != "contact.title":
        return False, None

    confidence = getattr(entity, "confidence", 0.0)
    if confidence < 0.5:
        return False, None

    entity_text = getattr(entity, "text", "") or ""
    normalized = getattr(entity, "normalized_value", "") or ""

    # Check if the title looks like a SAP VP title
    is_sap_vp_title = bool(_SAP_VP_TITLE_PATTERN.search(entity_text))
    if not is_sap_vp_title:
        return False, None

    # If normalized_value indicates sap_field affiliation, check the source
    is_tagged_sap_field = "sap_field" in normalized.lower()
    if not is_tagged_sap_field:
        return False, None

    source_text = getattr(source_doc, "text", "") or ""

    # If the source confirms SAP SE employment, this is a real SAP-field contact
    has_sap_se_markers = bool(_SAP_SE_EMPLOYEE_MARKERS.search(source_text))
    if has_sap_se_markers:
        return False, None

    # If the source indicates a small SAP partner/reseller, this is title inflation
    has_small_partner = bool(_SMALL_PARTNER_LANGUAGE.search(source_text))
    if not has_small_partner:
        return False, None

    return (
        True,
        (
            f"SAP VP title inflation: contact title {entity_text!r} tagged as "
            f"sap_field but source indicates a boutique SAP partner/reseller, not "
            f"an SAP SE employee. This contact cannot provide SAP co-sell program "
            f"referrals to end-customer accounts. Remove sap_field affiliation tag; "
            f"treat as SI-partner contact or direct relationship, not a co-sell signal."
        ),
    )
