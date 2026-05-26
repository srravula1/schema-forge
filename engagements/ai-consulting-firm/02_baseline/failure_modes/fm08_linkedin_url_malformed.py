"""LinkedIn URL extracted is malformed or points to company page instead of a person profile.

Source: Clay community documentation on LinkedIn URL enrichment failures
(clay.com community, 2024-2025); ZoomInfo API documentation on profile URL validation.
"""

import re
from forge.domains.gtm.baseline.failure_modes import SourceDoc

_VALID_PERSON_PATTERN = re.compile(r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?$")
_COMPANY_PATTERN = re.compile(r"linkedin\.com/company/")

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "contact.linkedin_url"})(), "text": "https://www.linkedin.com/company/acme-corp"})()
FIXTURE_SOURCE = SourceDoc(text="Follow us at linkedin.com/company/acme-corp")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags LinkedIn URLs that are company pages or do not match the /in/ person URL pattern."""
    if entity.label.value != "contact.linkedin_url":
        return False, None
    url = entity.text.strip()
    if _COMPANY_PATTERN.search(url):
        return True, "LinkedIn URL points to company page, not a person profile"
    if not _VALID_PERSON_PATTERN.match(url):
        return True, f"LinkedIn URL does not match expected /in/<slug> pattern: {url}"
    return False, None
