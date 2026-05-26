"""Form submission engagement extracted from a spam/bot submission rather than a real prospect request.

Source: HubSpot spam form submission documentation (knowledge.hubspot.com);
r/sales discussion on inbound lead quality from demo request forms (2024);
Clearbit's guide to form enrichment and spam filtering (clearbit.com/blog).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_SPAM_SIGNALS = re.compile(
    r"\b(test@|spam@|noreply@|bot@|fake@|disposable|mailinator|guerrillamail|"
    r"throwam|trashmail|yopmail|tempmail|xxx|asdf|qwerty|123456|click here|buy now)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "engagement.form_submit"})(), "text": "demo request submitted"})()
FIXTURE_SOURCE = SourceDoc(
    text="Form submission from: test@mailinator.com. Message: asdf asdf click here.",
    metadata={"submitter_email": "test@mailinator.com"},
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags form submissions that contain spam-indicator patterns in the text or submitter email."""
    if entity.label.value != "engagement.form_submit":
        return False, None
    combined = source_doc.text + " " + source_doc.metadata.get("submitter_email", "")
    if _SPAM_SIGNALS.search(combined):
        return True, "form submission may be spam/bot; spam indicators detected in submission content"
    return False, None
