"""
Failure mode: "Joule interest" extracted from SAP's own marketing copy, not prospect intent.

A prospect downloaded an SAP whitepaper on "Joule for Finance" from SAP's own website.
Intent-data providers flag the account as "high intent for Joule." The Joule interest
entity is extracted from a SAP marketing email forwarded to the prospect, an SAP SAPPHIRE
keynote transcript, or content from sap.com describing Joule benefits — not from a
statement by the prospect about their own evaluation or need.

The source of the Joule interest signal matters critically: SAP's own marketing materials
describe Joule as a feature of S/4HANA and BTP. If the "Joule interest" signal comes
from SAP-authored content (SAP website, SAP whitepaper, SAP event keynote, SAP partner
marketing), it reflects SAP's promotional activity, not the prospect's buying intent.
A prospect who receives and reads a Joule whitepaper is not the same as a prospect
who says "we need to implement Joule for our FI period-close."

Source: SAP-Joule engagement, qualification interview 2026-05-22.
"'Joule interest' from SAP's own marketing campaign reach, not the prospect's own
initiative. A prospect who downloaded an SAP whitepaper on Joule and got into our
nurture is not the same as a prospect who called us because their CIO asked them to
evaluate Joule." (Qualification interview §4, FM-SAP-04)
05_failure_modes_interview.md FM-SAP-04.

Detection trigger: Joule-related intent topic extracted from source text that contains
SAP-authored content markers (sap.com URLs, SAP whitepaper language, SAP event framing)
rather than prospect-authored statements about their own evaluation.
"""

from __future__ import annotations

import re
from typing import Any

# SAP-authored content markers
_SAP_AUTHORED_MARKERS = re.compile(
    r"\b(sap\.com|help\.sap\.com|news\.sap\.com|sapphirenow|sap-insider"
    r"|SAP whitepaper|SAP blog|SAP press release|SAP keynote|SAP event"
    r"|powered by SAP|SAP announces|discover how SAP|SAP is excited to"
    r"|available in SAP|with SAP you can|Joule is SAP's|SAP Joule helps"
    r"|built into SAP|embedded in SAP)\b",
    re.IGNORECASE,
)

# Prospect-originated intent language (counterbalances the detection)
_PROSPECT_INTENT_MARKERS = re.compile(
    r"\b(we are evaluating|we need Joule|our CIO asked|we want to implement"
    r"|we're looking for|we've decided to|we plan to activate|our team is"
    r"|we would like to|we are considering|we have been exploring|our CFO asked"
    r"|I'm reaching out because|we have a project|we have budget for)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type(
    "E",
    (),
    {
        "label": type("L", (), {"value": "signal.intent_topic"})(),
        "text": "SAP Joule for Finance",
        "normalized_value": "SAP Joule",
        "confidence": 0.72,
    },
)()

FIXTURE_SOURCE = type(
    "S",
    (),
    {
        "text": (
            "From: marketing@sap.com\n"
            "Subject: Discover how SAP Joule transforms Finance operations\n\n"
            "SAP Joule is SAP's AI copilot, built into S/4HANA and BTP. "
            "Joule helps Finance teams automate period-close, reduce manual steps, "
            "and generate variance analysis narratives. Available in SAP S/4HANA Cloud "
            "and RISE with SAP. Learn more at sap.com/joule"
        )
    },
)()


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect Joule interest extracted from SAP marketing copy, not prospect intent.

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

    # Check if this is a Joule-related intent topic
    joule_related = bool(
        re.search(r"\b(Joule|SAP AI|BTP AI|S/4HANA AI|SAP Copilot)\b", entity_text, re.IGNORECASE)
        or re.search(r"\b(joule|sap_ai|btp_ai)\b", normalized.lower())
    )
    if not joule_related:
        return False, None

    source_text = getattr(source_doc, "text", "") or ""

    has_sap_authored = bool(_SAP_AUTHORED_MARKERS.search(source_text))
    if not has_sap_authored:
        return False, None

    has_prospect_intent = bool(_PROSPECT_INTENT_MARKERS.search(source_text))
    if has_prospect_intent:
        return False, None

    return (
        True,
        (
            f"SAP marketing attribution: Joule intent topic {entity_text!r} extracted "
            f"from SAP-authored content (SAP marketing materials, sap.com, or SAP event "
            f"transcript) rather than prospect-originated statement. Intent-data attribution "
            f"from SAP's own marketing reach does not indicate prospect buying intent. "
            f"Flag as low-confidence intent; do not treat as S_JOULE_INTEREST signal. "
            f"Requires direct prospect confirmation of Joule evaluation."
        ),
    )
