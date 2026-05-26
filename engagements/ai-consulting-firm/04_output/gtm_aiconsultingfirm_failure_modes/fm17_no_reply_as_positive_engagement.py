"""Email reply extracted from an auto-reply, OOO, or bounce message — not a real prospect reply.

Source: Instantly.ai deliverability guide on auto-reply detection (instantly.ai/blog);
Lemlist blog on bounce and OOO handling (lemlist.com/blog); Smartlead FAQ on reply detection.
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_AUTO_REPLY_PATTERNS = re.compile(
    r"\b(out of office|auto.?reply|automatic reply|on vacation|on leave|ooo\b|i am away|"
    r"bounce|undeliverable|delivery failure|mail delivery failed|noreply|no-reply|donotreply)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "engagement.email_reply"})(), "text": "Re: Your outreach"})()
FIXTURE_SOURCE = SourceDoc(text="Out of Office: I will be away until Jan 10. For urgent matters contact my manager.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags email replies that are auto-replies, OOO messages, or bounces rather than real prospect replies."""
    if entity.label.value != "engagement.email_reply":
        return False, None
    if _AUTO_REPLY_PATTERNS.search(source_doc.text):
        return True, "email reply appears to be an auto-reply, OOO, or bounce — not a real prospect reply"
    return False, None
