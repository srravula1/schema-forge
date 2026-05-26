"""
GTM qualification policy — MEDDPICC-derived.

Maps Q_* evidence labels → disposition (qualified / nurture / disqualified).

Framework: MEDDPICC (Metrics, Economic Buyer, Decision Criteria, Decision Process,
Identify Pain, Champion, Competition, Paper Process). Public framework; multiple
structured versions at github.com/meddic/meddpicc and notion.so community templates.

Compose with a confidence threshold: low confidence → HIL regardless of policy
verdict. The compose() function implements this gate.

Override targets (for merge step):
  - REQUIRED_FOR_QUALIFIED: set of Q_* label values that must all be present
  - DISQUALIFY_IF: set of conditions that immediately disqualify
  - CONFIDENCE_HIL_THRESHOLD: float, below which route to HIL
"""

from __future__ import annotations

# Evidence labels from gtm_schema.GtmLabel — listed by value string so this
# module stays import-free from the schema (pure policy logic, no model deps).
_BUDGET = "qualification.budget_confirmed"
_AUTHORITY = "qualification.authority_identified"
_NEED = "qualification.need_articulated"
_TIMELINE = "qualification.timeline_stated"

REQUIRED_FOR_QUALIFIED: frozenset[str] = frozenset({_NEED, _AUTHORITY})
STRONG_QUALIFIED: frozenset[str] = frozenset({_BUDGET, _AUTHORITY, _NEED, _TIMELINE})

CONFIDENCE_HIL_THRESHOLD: float = 0.70

_QUALIFIED = "qualified"
_NURTURE = "nurture"
_DISQUALIFIED = "disqualified"
_HIL = "hil"


def disposition(evidence_labels: set[str], confidence: float) -> str:
    """
    Map extracted Q_* evidence labels and confidence to a disposition string.

    Returns one of: 'qualified', 'nurture', 'disqualified', 'hil'.

    Policy (MEDDPICC-derived, generic baseline):
    - Low confidence (<= CONFIDENCE_HIL_THRESHOLD) → 'hil' regardless of evidence.
    - All four MEDDPICC evidence labels present → 'qualified'.
    - REQUIRED_FOR_QUALIFIED (need + authority) present → 'qualified'.
    - Need articulated but missing authority → 'nurture'.
    - Nothing relevant present → 'nurture' (keep in pipeline, do not discard).

    Note: 'disqualified' is reserved for explicit negative signals (no budget
    category, wrong segment, explicit rejection) — the base policy does not
    auto-disqualify from absence of evidence alone. Buyer-specific disqualify
    rules go in 03_overrides/policy_overrides.yaml.

    Source: MEDDPICC framework (public); Clari published qualification rubrics
    (clari.com/blog/meddpicc-sales-methodology).
    """
    if confidence <= CONFIDENCE_HIL_THRESHOLD:
        return _HIL

    has_need = _NEED in evidence_labels
    has_authority = _AUTHORITY in evidence_labels
    has_budget = _BUDGET in evidence_labels
    has_timeline = _TIMELINE in evidence_labels

    if STRONG_QUALIFIED.issubset(evidence_labels):
        return _QUALIFIED

    if REQUIRED_FOR_QUALIFIED.issubset(evidence_labels):
        return _QUALIFIED

    if has_need and has_budget:
        return _QUALIFIED

    if has_need or has_authority:
        return _NURTURE

    return _NURTURE


def compose(
    evidence_labels: set[str],
    confidence: float,
    policy_verdict: str | None = None,
) -> str:
    """
    Compose the policy verdict with the confidence gate.

    If policy_verdict is provided, applies the confidence gate on top:
    low confidence routes to 'hil' regardless of verdict.

    If policy_verdict is None, calls disposition() internally.
    """
    if confidence <= CONFIDENCE_HIL_THRESHOLD:
        return _HIL
    if policy_verdict is not None:
        return policy_verdict
    return disposition(evidence_labels, confidence)
