"""LLM normalization step for EPIC D (Story D2).

``Normalizer`` is the injectable abstraction that ``cmd_extract_overrides`` uses
to turn free-text interview answers into structured override YAML.  The real
implementation calls the Anthropic API; tests inject a fake via the constructor.

Interface::

    class Normalizer:
        def propose(self, interview_text: str, target: str) -> dict:
            ...

``target`` is one of: ``"icp"``, ``"channel"``, ``"modifier"``, ``"policy"``.
The returned dict must be a valid payload for the corresponding Pydantic model.
"""

from __future__ import annotations

import json
import re
from typing import Any, Protocol


_SYSTEM_PROMPT = """\
You are a schema normalization assistant for a sales schema generator.
Your job is to read free-text interview answers and convert them into a
structured JSON object that fits a specific override type.

Rules:
- Output ONLY a JSON object — no markdown, no explanation, no code fences.
- Every key that maps to an object with per-entry data must include a "rationale"
  string field with the direct interview snippet that motivated the entry.
- Only include keys where the interview contains evidence. Omit keys with no evidence.
- Do not make strategic decisions. Only normalize what the human said.
"""

_TARGET_PROMPTS: dict[str, str] = {
    "icp": """\
Convert the interview text into an ICP overrides JSON object.
Top-level keys are GtmLabel string values (e.g. "account.employee_range",
"account.industry", "account.funding_stage").
Each entry has: include (list), exclude (list), preferred (list), rationale (string).
Omit include/exclude/preferred if empty. Always include rationale.
Example:
{
  "account.employee_range": {
    "include": ["11-50", "51-200"],
    "exclude": ["1-10"],
    "rationale": "5 won deals all between 25-180 employees"
  }
}
""",
    "channel": """\
Convert the interview text into a channel overrides JSON object.
Keys: "signal_weights" (map of GtmLabel string -> float 0-1),
      "custom_signals" (list of {name, definition, rationale, add_to_schema}).
Example:
{
  "signal_weights": {
    "signal.pain_point_mention": 0.9,
    "signal.hiring_trigger": 0.3
  },
  "custom_signals": [
    {
      "name": "S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT",
      "definition": "Prospect engaged with founder LinkedIn content in last 14 days",
      "rationale": "Channel interview: 70% of inbound starts here",
      "add_to_schema": true
    }
  ]
}
""",
    "modifier": """\
Convert the interview text into a modifier overrides JSON object.
Key: "intent_topics" with sub-keys "add" (list), "deprioritize" (list), "rationale" (string).
Example:
{
  "intent_topics": {
    "add": ["LLM evaluation", "AI governance"],
    "deprioritize": ["data warehouse migration"],
    "rationale": "Client product areas from modifier interview"
  }
}
""",
    "policy": """\
Convert the interview text into a policy overrides JSON object.
Keys: "disqualification_rules", "auto_pass_rules", "hil_rules".
Each is a list of {condition (string), rationale (string)}.
Example:
{
  "disqualification_rules": [
    {"condition": "A_EMPLOYEE_RANGE in [1-10]", "rationale": "Deal economics require >10 employees"}
  ],
  "auto_pass_rules": [],
  "hil_rules": []
}
""",
}


class NormalizerProtocol(Protocol):
    def propose(self, interview_text: str, target: str) -> dict[str, Any]:
        ...


class AnthropicNormalizer:
    """Real normalizer backed by the Anthropic API.

    Uses model ``claude-sonnet-4-6``.  The LLM only normalizes free-text
    into structured edits — it makes no strategic decisions.
    """

    MODEL = "claude-sonnet-4-6"

    def __init__(self) -> None:
        import anthropic  # deferred import keeps tests import-clean

        self._client = anthropic.Anthropic()

    def propose(self, interview_text: str, target: str) -> dict[str, Any]:
        target_prompt = _TARGET_PROMPTS.get(target, "")
        user_content = f"{target_prompt}\n\nINTERVIEW TEXT:\n{interview_text}"
        message = self._client.messages.create(
            model=self.MODEL,
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = message.content[0].text.strip()
        # Strip any accidental markdown fences
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        return json.loads(raw)


class FakeNormalizer:
    """Deterministic stub for tests — returns minimal valid structures."""

    _RESPONSES: dict[str, dict[str, Any]] = {
        "icp": {
            "account.employee_range": {
                "include": ["11-50", "51-200"],
                "exclude": ["1-10"],
                "rationale": "Stub: 5 won deals all between 25-180 employees",
            }
        },
        "channel": {
            "signal_weights": {"signal.pain_point_mention": 0.9},
            "custom_signals": [
                {
                    "name": "S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT",
                    "definition": "Prospect engaged with founder LinkedIn content",
                    "rationale": "Stub: channel interview evidence",
                    "add_to_schema": True,
                }
            ],
        },
        "modifier": {
            "intent_topics": {
                "add": ["LLM evaluation", "AI governance"],
                "deprioritize": ["data warehouse migration"],
                "rationale": "Stub: client product areas",
            }
        },
        "policy": {
            "disqualification_rules": [
                {
                    "condition": "A_EMPLOYEE_RANGE in [1-10]",
                    "rationale": "Stub: deal economics require >10 employees",
                }
            ],
            "auto_pass_rules": [],
            "hil_rules": [],
        },
    }

    def propose(self, interview_text: str, target: str) -> dict[str, Any]:
        return self._RESPONSES.get(target, {})
