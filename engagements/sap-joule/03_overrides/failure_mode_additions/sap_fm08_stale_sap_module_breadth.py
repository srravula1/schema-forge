"""
Failure mode: Multiple SAP module mentions creating a false breadth signal from stale data.

An account with job postings and LinkedIn content mentioning FI, CO, MM, SD, PP, QM,
HR, and EWM modules is scored as having a "rich SAP footprint." In reality, many of
these module mentions come from historical job postings (hiring for ABAP developers
who worked on these modules 5+ years ago) or from a legacy ECC implementation that
has not been meaningfully upgraded. Only a subset of modules may be actively used in
a current, maintained configuration. The breadth of module mentions is historical
documentation, not current active deployment.

The extraction failure: inferring a current, active SAP module footprint from the full
set of historical module mentions without distinguishing between currently maintained
modules and legacy/inactive implementations. For Joule readiness, the relevant question
is: which modules are actively used in the CURRENT SAP landscape (especially if on
S/4HANA), not which modules have ever been installed.

Source: SAP-Joule engagement, failure modes interview 2026-05-22.
"An account had FI, CO, MM, SD, PP, QM, and HR all mentioned in their job postings
and LinkedIn content. This was interpreted as a 'rich SAP footprint' and scored highly.
In reality, many of these modules were in a legacy ECC implementation that had not been
upgraded in years." (FM-SAP-08)
SAP module lifecycle documentation: https://support.sap.com/en/my-support/systems-installations/erp.html

Detection trigger: Multiple SAP module tech stack entities extracted from source text
where the module mentions come from historical job postings or past-tense language
rather than present-tense active system descriptions.
"""

from __future__ import annotations

import re
from typing import Any

_SAP_MODULE_PATTERN = re.compile(
    r"\b(SAP\s+)?(FI|CO|MM|SD|PP|QM|HCM|HR|EWM|PM|PS|WM|SRM|CRM|SCM|APO|BW)\b",
    re.IGNORECASE,
)

# Historical/stale language
_HISTORICAL_LANGUAGE = re.compile(
    r"\b(years? ago|was responsible for|worked on|maintained|supported|legacy"
    r"|previous role|former|experienced in|background in|expertise in"
    r"|used to|historically|in the past|2015|2016|2017|2018|2019|2020"
    r"|15 years of|10 years of|experience with)\b",
    re.IGNORECASE,
)

# Active/current language (counterbalances the detection)
_ACTIVE_LANGUAGE = re.compile(
    r"\b(currently running|active (SAP )?system|live production|production environment"
    r"|our current SAP|we use|we run|actively using|in production today"
    r"|our S/4|on RISE|our ECC system today|day.to.day operations)\b",
    re.IGNORECASE,
)

FIXTURE_ENTITY = type(
    "E",
    (),
    {
        "label": type("L", (), {"value": "account.tech_stack_item"})(),
        "text": "SAP PP, QM, and EWM",
        "normalized_value": "SAP PP",
        "confidence": 0.65,
    },
)()

FIXTURE_SOURCE = type(
    "S",
    (),
    {
        "text": (
            "Senior SAP Consultant — experienced in FI, CO, MM, SD, PP, QM, HR/HCM, "
            "and EWM. 15 years of SAP experience across multiple ECC implementations. "
            "Background in full lifecycle SAP projects from 2009 to 2021. Previously "
            "maintained legacy ECC modules at manufacturing clients. Currently seeking "
            "new opportunities in SAP consulting."
        )
    },
)()


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect stale SAP module breadth creating a false footprint signal.

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
    if label_value != "account.tech_stack_item":
        return False, None

    confidence = getattr(entity, "confidence", 0.0)
    if confidence < 0.4:
        return False, None

    entity_text = getattr(entity, "text", "") or ""

    # Check if this involves SAP modules
    module_matches = _SAP_MODULE_PATTERN.findall(entity_text)
    if len(module_matches) < 2:
        return False, None

    source_text = getattr(source_doc, "text", "") or ""

    has_active_language = bool(_ACTIVE_LANGUAGE.search(source_text))
    if has_active_language:
        return False, None

    has_historical_language = bool(_HISTORICAL_LANGUAGE.search(source_text))
    if not has_historical_language:
        return False, None

    module_list = ", ".join(str(m) for m in module_matches[:5])
    return (
        True,
        (
            f"Stale SAP module breadth: tech stack entity {entity_text!r} references "
            f"multiple SAP modules ({module_list}) extracted from historical or "
            f"past-tense language (consultant CV, legacy implementation context). "
            f"Module breadth from historical sources does not indicate active current "
            f"footprint. For Joule readiness, only currently-maintained, active-production "
            f"modules in the current SAP landscape are relevant. "
            f"Recommend verifying active module footprint directly with the SAP CoE."
        ),
    )
