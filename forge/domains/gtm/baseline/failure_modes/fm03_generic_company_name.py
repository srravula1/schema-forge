"""Company name extracted is a generic word rather than a specific organization name.

Source: Clay community enrichment-failure posts on "company" or "Inc" extracted as
company names; HubSpot's CRM data quality guide (hubspot.com/blog/crm-data-quality).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

_GENERIC_NAMES = frozenset({
    "company", "corporation", "inc", "llc", "ltd", "corp", "organization",
    "enterprise", "startup", "firm", "business", "vendor", "client",
    "the company", "a company", "this company",
})

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "account.company_name"})(), "text": "the company"})()
FIXTURE_SOURCE = SourceDoc(text="The company announced layoffs today.")


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags company names that are generic words, not real organization names."""
    if entity.label.value != "account.company_name":
        return False, None
    normalized = entity.text.strip().lower().rstrip(".")
    if normalized in _GENERIC_NAMES or len(normalized) <= 3:
        return True, f"company name appears generic: '{entity.text}'"
    return False, None
