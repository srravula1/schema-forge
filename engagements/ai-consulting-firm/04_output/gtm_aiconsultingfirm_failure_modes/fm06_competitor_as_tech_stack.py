"""Competitor product name extracted as A_TECH_STACK_ITEM instead of S_COMPETITOR_MENTION.

Source: Gong call-coaching taxonomy on competitor mention misclassification
(gong.io/blog/competitive-intelligence); Clay community enrichment accuracy threads (2024).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_KNOWN_COMPETITORS = frozenset({
    "salesforce", "hubspot", "outreach", "salesloft", "apollo", "zoominfo",
    "clearbit", "bombora", "6sense", "demandbase", "drift", "gong",
    "chorus", "clari", "people.ai", "clay",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.tech_stack_item"})(), "text": "Salesforce"})()
FIXTURE_SOURCE = SourceDoc(text="They currently use Salesforce but are looking to migrate.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags when a well-known GTM competitor is labeled as a tech stack item rather than competitor mention."""
    if entity.label.value != "account.tech_stack_item":
        return False, None
    text_lower = entity.text.strip().lower()
    context_lower = source_doc.text.lower()
    if text_lower in _KNOWN_COMPETITORS:
        competitor_context = any(
            phrase in context_lower for phrase in
            ("looking to replace", "looking to migrate", "migrate away", "switching from",
             "evaluating alternatives", "competitor", "replace with", "move away")
        )
        if competitor_context:
            return True, f"'{entity.text}' appears in competitor-replacement context; consider S_COMPETITOR_MENTION"
    return False, None
