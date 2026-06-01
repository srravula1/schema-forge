"""
bdc_soi failure-mode library. Each module codifies a real SoI-extraction error caught by hand in the
CalPERS ARCC×OBDC run (2026-06-01) so the spine's ingester can run them as gates and never silently
repeat the bug. Each module exposes:
  - detect(entity, source_doc) -> tuple[bool, str | None]
  - a one-line operator-language docstring + the source (the run/filing it was observed in)
  - FIXTURE_ENTITY + FIXTURE_SOURCE that trigger the mode (asserted in tests/test_bdc_soi.py)

`entity` is a PositionMark (or any object exposing .fair_value_mark / .par / .seniority); `source_doc`
is the SourceDoc below (the raw SoI row text + optional resolution metadata).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SourceDoc:
    """Minimal source shape for SoI failure-mode detection: the raw row text + resolution metadata."""

    text: str = ""
    doc_type: str = "bdc_schedule_of_investments"
    metadata: dict = field(default_factory=dict)
