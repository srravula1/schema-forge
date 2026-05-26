"""Account domain extracted from an email signature's legal disclaimer footer, not the primary company domain.

Source: HubSpot blog on CRM data normalization pitfalls (hubspot.com/blog); Clay community
thread on domain extraction from email footers (2025).
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_LEGAL_FOOTER_INDICATORS = re.compile(
    r"\b(confidential|privileged|disclaimer|this email|this message|intended recipient|"
    r"unsubscribe|legal notice|copyright \d{4}|all rights reserved)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.domain"})(), "text": "legalnotices.bigcorp.com"})()
FIXTURE_SOURCE = SourceDoc(
    text="John Smith | ACME Corp\nThis message is confidential. See legalnotices.bigcorp.com for full disclaimer.",
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags account domains extracted from legal footer/disclaimer sections of emails."""
    if entity.label.value != "account.domain":
        return False, None
    if _LEGAL_FOOTER_INDICATORS.search(source_doc.text):
        domain = entity.text.strip().lower()
        if any(sub in domain for sub in ("legal", "privacy", "notices", "disclaimer", "info", "noreply")):
            return True, f"domain '{entity.text}' may be from legal footer, not primary company domain"
    return False, None
