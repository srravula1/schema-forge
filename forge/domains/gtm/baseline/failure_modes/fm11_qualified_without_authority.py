"""Opportunity marked qualified despite no Q_AUTHORITY_IDENTIFIED evidence — champion risk.

Source: MEDDPICC framework documentation (public); Clari blog on champion vs economic buyer
distinction (clari.com/blog/economic-buyer-meddpicc); Winning by Design SPICED framework
(winningbydesign.com).
"""

from forge.domains.gtm.baseline.failure_modes import SourceDoc

FIXTURE_ENTITY = type("E", (), {"label": type("L", (), {"value": "qualification.disposition"})(), "text": "qualified"})()
FIXTURE_SOURCE = SourceDoc(
    text="Qualified. Budget confirmed, need articulated. No mention of economic buyer or decision process.",
    metadata={"evidence_labels": ["qualification.budget_confirmed", "qualification.need_articulated"]},
)


def detect(entity, source_doc: SourceDoc) -> tuple[bool, str | None]:
    """Flags 'qualified' disposition when Q_AUTHORITY_IDENTIFIED is absent from evidence labels."""
    if entity.label.value != "qualification.disposition":
        return False, None
    if entity.text.strip().lower() != "qualified":
        return False, None
    evidence = set(source_doc.metadata.get("evidence_labels", []))
    if "qualification.authority_identified" not in evidence:
        return True, "disposition='qualified' but Q_AUTHORITY_IDENTIFIED not in evidence; champion risk"
    return False, None
