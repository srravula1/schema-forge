"""Contact email extracted is a personal address (gmail, yahoo, etc.), not a business email.

Source: Smartlead deliverability guide on personal vs work email bounce rates
(smartlead.ai/blog/email-deliverability); r/sales discussion on prospecting to
personal emails (2024).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_PERSONAL_DOMAINS = frozenset({
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "protonmail.com", "aol.com", "me.com", "mac.com", "live.com",
    "msn.com", "ymail.com", "proton.me",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "contact.email"})(), "text": "john.doe@gmail.com"})()
FIXTURE_SOURCE = SourceDoc(text="Contact me at john.doe@gmail.com for inquiries.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags contact emails from known personal/consumer email providers."""
    if entity.label.value != "contact.email":
        return False, None
    email = entity.text.strip().lower()
    if "@" not in email:
        return False, None
    domain = email.split("@", 1)[1]
    if domain in _PERSONAL_DOMAINS:
        return True, f"personal email domain detected: {domain}"
    return False, None
