"""
bdc_soi HIL policy — maps a resolved cross-holder mark divergence to a disposition.

A mark divergence is an *inconsistency to reconcile*, never proof either mark is wrong (carried from
the platform's flag-not-determination stance). The policy decides only whether a divergence is worth
a human's attention. Compose with confidence: in a new vertical, always route (the platform's
always-route-until-calibrated rule) — CONFIDENCE_HIL_THRESHOLD is the seam for when that relaxes.

Override targets (for the merge step):
  - DIVERGENCE_THRESHOLD_PTS: spread (in points) at/above which a divergence routes to a human
  - STRESSED_MARK: a mark below this is a stressed name — route even on a small spread
  - CONFIDENCE_HIL_THRESHOLD: below this confidence, route regardless of spread
"""

from __future__ import annotations

DIVERGENCE_THRESHOLD_PTS: float = 0.5
STRESSED_MARK: float = 90.0
CONFIDENCE_HIL_THRESHOLD: float = 1.01  # >1.0 == always route (new vertical, not yet calibrated)

_ROUTE = "route_to_analyst"
_LOG = "log_consistent"


def disposition(
    mark_spread_pts: float,
    *,
    min_mark: float = 100.0,
    non_accrual_disagreement: bool = False,
) -> str:
    """Route a resolved divergence to a human if the spread clears the threshold, the holders
    disagree on non-accrual, or either side marks the name stressed; otherwise log it as consistent."""
    if mark_spread_pts >= DIVERGENCE_THRESHOLD_PTS:
        return _ROUTE
    if non_accrual_disagreement:
        return _ROUTE
    if min_mark < STRESSED_MARK:
        return _ROUTE
    return _LOG


def compose(
    mark_spread_pts: float,
    confidence: float,
    *,
    min_mark: float = 100.0,
    non_accrual_disagreement: bool = False,
) -> str:
    """Confidence gate over `disposition`: low confidence always routes to a human."""
    if confidence < CONFIDENCE_HIL_THRESHOLD:
        return _ROUTE
    return disposition(
        mark_spread_pts, min_mark=min_mark, non_accrual_disagreement=non_accrual_disagreement
    )
