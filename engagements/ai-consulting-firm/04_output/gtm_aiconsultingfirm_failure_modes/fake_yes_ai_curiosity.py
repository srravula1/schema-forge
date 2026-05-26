"""
Failure mode: AI tire-kicker / fake yes — prospect engages enthusiastically
with AI consulting content, says all the right things in discovery, but is
"just exploring" and has no specific project, no named internal owner, no
data sample ready, and no budget allocated to a concrete initiative.

Source: Failure-modes interview, AI consulting client, 2026-05-25.
"Half my discovery calls last quarter were people who wanted free AI
education, not buyers." (Founder, channel interview follow-up)
"The word 'explore' is a red flag. Real buyers say 'we have X problem and
we need to solve it by Y date.' The explorers say 'I want to see what's
possible.'" (Founder, ICP interview §5)

Detection trigger: Q_NEED_ARTICULATED entity present (they say the right things)
combined with Q_BUDGET_CONFIRMED absent AND Q_TIMELINE_STATED absent,
AND multiple S_PAIN_POINT_MENTION entities in the engagement history
(suggesting enthusiasm without commitment).

Distinction from baseline fm11 (qualified-without-authority): this failure
mode fires when NEED is articulated but BUDGET and TIMELINE are both absent.
fm11 catches BUDGET+TIMELINE present without AUTHORITY. These are
complementary, non-overlapping failure modes.

Test fixture: Discovery call transcript that includes:
- Multiple references to AI problems the prospect has ("our LLM keeps hallucinating")
- Enthusiastic engagement language ("this is exactly what we need")
- Zero budget confirmation ("we'd have to figure out funding")
- Zero timeline commitment ("no specific timeline, whenever it works")
- No named internal owner ("it would be a team effort")
"""

from __future__ import annotations

from typing import Any


def detect(entity: Any, source_doc: Any) -> tuple[bool, str | None]:
    """Detect the AI tire-kicker / fake yes failure mode.

    Args:
        entity: An object with a .label attribute (GtmLabel value or string).
        source_doc: The source document context. May have .engagement_history
                    attribute if available; detection degrades gracefully without it.

    Returns:
        (True, reason) if the failure mode is detected; (False, None) otherwise.
    """
    label = getattr(entity, "label", None)
    if label is None:
        return False, None

    label_value = label.value if hasattr(label, "value") else str(label)

    if label_value != "qualification.need_articulated":
        return False, None

    confidence = getattr(entity, "confidence", 1.0)
    if confidence < 0.4:
        return False, None

    history = getattr(source_doc, "engagement_history", None)
    if history is None:
        return False, None

    try:
        count_label = getattr(history, "count_by_label", None)
        if count_label is None:
            return False, None

        pain_signals = count_label("signal.pain_point_mention")
        budget_signals = count_label("qualification.budget_confirmed")
        timeline_signals = count_label("qualification.timeline_stated")
    except Exception:
        return False, None

    if pain_signals >= 3 and budget_signals == 0 and timeline_signals == 0:
        return (
            True,
            (
                f"AI tire-kicker / fake yes pattern: {pain_signals} pain-point mentions "
                f"with zero budget evidence and zero timeline evidence. "
                f"Prospect is likely exploring, not buying. "
                f"Check: can they name a specific project timeline and a named internal owner?"
            ),
        )

    return False, None


FIXTURE_ENTITY_LABEL = "qualification.need_articulated"
FIXTURE_ENTITY_TEXT = (
    "We're dealing with hallucinations in our LLM pipeline and this is exactly "
    "the kind of problem we've been trying to solve — we'd love to work together on this."
)
FIXTURE_ENTITY_CONFIDENCE = 0.82

FIXTURE_SOURCE_DESCRIPTION = (
    "Discovery call transcript with 5 pain-point mentions, zero budget confirmation, "
    "zero timeline commitment, and no named internal owner. Prospect said 'I want to "
    "see what's possible' and 'we'd have to figure out the budget and timeline.'"
)
