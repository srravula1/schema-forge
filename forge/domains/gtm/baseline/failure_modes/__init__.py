"""
GTM failure-mode library. ~25 named modes, each with:
  - detect(entity, source_doc) -> tuple[bool, str | None]
  - one-line operator-language docstring
  - public source citation
  - at least one test fixture (in tests/test_failure_modes.py)

SourceDoc is the shared minimal shape passed to every detect() function.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SourceDoc:
    """Minimal source document shape for failure-mode detection."""

    url: str = ""
    text: str = ""
    doc_type: str = ""
    metadata: dict = field(default_factory=dict)
