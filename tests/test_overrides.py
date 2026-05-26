"""Tests for EPIC D — extract-overrides.

Story D1: valid override YAML parses into the models; missing rationale fails;
          bad label refs are detected.

Story D2: with a fake normalizer (no network), extract-overrides writes YAML
          that validates against D1 schemas.

Story D3: proposed files carry the review marker + source snippet;
          command exit/print behaviour is correct.
"""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from forge.overrides import (
    ChannelOverrides,
    CustomSignal,
    DisqualificationRule,
    IcpOverrides,
    LabelFilter,
    ModifierOverrides,
    OverrideBundle,
    PolicyOverrides,
    check_label_refs,
    load_overrides,
)
from forge.normalizer import FakeNormalizer


# ---------------------------------------------------------------------------
# Story D1 — model parsing
# ---------------------------------------------------------------------------


class TestIcpOverrides:
    def test_valid_parses(self):
        raw = {
            "account.employee_range": {
                "include": ["11-50", "51-200"],
                "exclude": ["1-10"],
                "rationale": "5 won deals all 25-180 employees",
            },
            "account.industry": {
                "preferred": ["Professional services"],
                "rationale": "ICP interview Q3",
            },
        }
        overrides = IcpOverrides.model_validate(raw)
        assert "account.employee_range" in overrides.filters
        assert overrides.filters["account.employee_range"].include == ["11-50", "51-200"]

    def test_missing_rationale_fails(self):
        raw = {
            "account.employee_range": {
                "include": ["11-50"],
                # rationale is missing
            }
        }
        with pytest.raises(ValidationError):
            IcpOverrides.model_validate(raw)

    def test_empty_overrides_valid(self):
        overrides = IcpOverrides.model_validate({})
        assert overrides.filters == {}


class TestChannelOverrides:
    def test_valid_signal_weights(self):
        raw = {
            "signal_weights": {
                "signal.pain_point_mention": 0.9,
                "signal.hiring_trigger": 0.3,
            },
            "custom_signals": [
                {
                    "name": "S_LINKEDIN_TL",
                    "definition": "Engaged with LinkedIn content",
                    "rationale": "Channel interview",
                    "add_to_schema": True,
                }
            ],
        }
        overrides = ChannelOverrides.model_validate(raw)
        assert overrides.signal_weights["signal.pain_point_mention"] == 0.9
        assert len(overrides.custom_signals) == 1

    def test_custom_signal_missing_rationale_fails(self):
        raw = {
            "custom_signals": [
                {
                    "name": "S_THING",
                    "definition": "Something",
                    # rationale missing
                }
            ]
        }
        with pytest.raises(ValidationError):
            ChannelOverrides.model_validate(raw)


class TestModifierOverrides:
    def test_valid_parses(self):
        raw = {
            "intent_topics": {
                "add": ["LLM evaluation", "AI governance"],
                "deprioritize": ["data warehouse migration"],
                "rationale": "Client product areas",
            }
        }
        overrides = ModifierOverrides.model_validate(raw)
        assert overrides.intent_topics is not None
        assert "LLM evaluation" in overrides.intent_topics.add

    def test_intent_topics_missing_rationale_fails(self):
        raw = {
            "intent_topics": {
                "add": ["LLM evaluation"],
                # rationale missing
            }
        }
        with pytest.raises(ValidationError):
            ModifierOverrides.model_validate(raw)


class TestPolicyOverrides:
    def test_valid_parses(self):
        raw = {
            "disqualification_rules": [
                {
                    "condition": "A_EMPLOYEE_RANGE in [1-10]",
                    "rationale": "Deal economics require >10 employees",
                }
            ],
            "auto_pass_rules": [
                {
                    "condition": "Q_BUDGET_CONFIRMED AND Q_AUTHORITY_IDENTIFIED",
                    "rationale": "Two of MEDDIC",
                }
            ],
            "hil_rules": [],
        }
        overrides = PolicyOverrides.model_validate(raw)
        assert len(overrides.disqualification_rules) == 1
        assert overrides.disqualification_rules[0].condition == "A_EMPLOYEE_RANGE in [1-10]"

    def test_rule_missing_rationale_fails(self):
        raw = {
            "disqualification_rules": [
                {"condition": "A_EMPLOYEE_RANGE in [1-10]"}  # no rationale
            ]
        }
        with pytest.raises(ValidationError):
            PolicyOverrides.model_validate(raw)


# ---------------------------------------------------------------------------
# Story D1 — label reference checker
# ---------------------------------------------------------------------------


class TestCheckLabelRefs:
    def test_valid_label_passes(self):
        bundle = OverrideBundle(
            icp=IcpOverrides.model_validate(
                {
                    "account.employee_range": {
                        "include": ["11-50"],
                        "rationale": "ok",
                    }
                }
            )
        )
        errors = check_label_refs(bundle)
        assert errors == []

    def test_invalid_label_detected(self):
        """A label that is not in GtmLabel should be caught."""
        # Construct the bundle manually with an invalid key bypassing validation.
        bundle = OverrideBundle()
        bundle.icp.filters["not.a.real.label"] = LabelFilter(
            include=["x"], rationale="test"
        )
        errors = check_label_refs(bundle)
        assert any("not.a.real.label" in e for e in errors)

    def test_invalid_signal_weight_label_detected(self):
        bundle = OverrideBundle()
        # Bypass model validator by constructing channel manually.
        ch = ChannelOverrides(signal_weights={}, custom_signals=[])
        ch.signal_weights["signal.does_not_exist"] = 0.5
        bundle.channel = ch
        errors = check_label_refs(bundle)
        assert any("signal.does_not_exist" in e for e in errors)


# ---------------------------------------------------------------------------
# D1 — loader tests
# ---------------------------------------------------------------------------


class TestLoadOverrides:
    def test_load_valid_icp_yaml(self, tmp_path):
        overrides_dir = tmp_path / "03_overrides"
        overrides_dir.mkdir()
        icp_yaml = textwrap.dedent("""\
            account.employee_range:
              include:
                - "11-50"
                - "51-200"
              exclude:
                - "1-10"
              rationale: "5 won deals 25-180 employees"
            account.industry:
              preferred:
                - "Professional services"
              rationale: "ICP interview Q3"
        """)
        (overrides_dir / "icp_overrides.yaml").write_text(icp_yaml)
        bundle = load_overrides(overrides_dir)
        assert "account.employee_range" in bundle.icp.filters
        assert bundle.icp.filters["account.employee_range"].include == ["11-50", "51-200"]

    def test_missing_files_use_defaults(self, tmp_path):
        overrides_dir = tmp_path / "03_overrides"
        overrides_dir.mkdir()
        bundle = load_overrides(overrides_dir)
        assert bundle.icp.filters == {}
        assert bundle.channel.signal_weights == {}


# ---------------------------------------------------------------------------
# Story D2 — extract-overrides with fake normalizer
# ---------------------------------------------------------------------------


def _make_engagement(tmp_path: Path) -> Path:
    """Create a minimal engagement directory with filled interview inputs."""
    eng = tmp_path / "acme"
    interviews = eng / "01_interview_inputs"
    interviews.mkdir(parents=True)

    (interviews / "02_icp_interview.md").write_text(
        "We sell to AI consulting firms with 20-200 employees. "
        "Our 5 won deals were all professional services companies."
    )
    (interviews / "03_channel_interview.md").write_text(
        "Pain point mentions are our biggest signal. "
        "LinkedIn thought leadership drives 70% of inbound."
    )
    (interviews / "04_qualification_interview.md").write_text(
        "Companies under 10 employees never have budget for us."
    )
    (interviews / "05_failure_modes_interview.md").write_text(
        "LLM evaluation and AI governance are our main intent topics."
    )
    return eng


def _run_extract(engagement: Path, normalizer=None) -> int:
    """Run cmd_extract_overrides with an injectable normalizer."""
    from forge.cli import cmd_extract_overrides

    ns = argparse.Namespace(engagement=engagement)
    return cmd_extract_overrides(ns, _normalizer=normalizer or FakeNormalizer())


class TestExtractOverrides:
    def test_writes_override_files(self, tmp_path):
        eng = _make_engagement(tmp_path)
        rc = _run_extract(eng)
        assert rc == 0
        overrides_dir = eng / "03_overrides"
        for fname in [
            "icp_overrides.yaml",
            "channel_overrides.yaml",
            "modifier_overrides.yaml",
            "policy_overrides.yaml",
        ]:
            assert (overrides_dir / fname).exists(), f"{fname} was not written"

    def test_written_yaml_validates_against_d1_schemas(self, tmp_path):
        eng = _make_engagement(tmp_path)
        rc = _run_extract(eng)
        assert rc == 0
        bundle = load_overrides(eng / "03_overrides")
        # ICP: should have the employee_range filter from FakeNormalizer
        assert "account.employee_range" in bundle.icp.filters
        # Channel: should have signal_weights
        assert "signal.pain_point_mention" in bundle.channel.signal_weights
        # Modifier: should have intent_topics
        assert bundle.modifier.intent_topics is not None
        # Policy: should have disqualification_rules
        assert len(bundle.policy.disqualification_rules) > 0

    def test_no_network_call(self, tmp_path, monkeypatch):
        """FakeNormalizer must not make any network call."""
        import anthropic as _anthropic

        def _no_call(*a, **kw):
            raise AssertionError("Should not call Anthropic API in tests")

        monkeypatch.setattr(_anthropic, "Anthropic", _no_call)
        eng = _make_engagement(tmp_path)
        rc = _run_extract(eng, normalizer=FakeNormalizer())
        assert rc == 0

    def test_missing_engagement_dir_returns_error(self, tmp_path):
        ns = argparse.Namespace(engagement=tmp_path / "nonexistent")
        from forge.cli import cmd_extract_overrides

        rc = cmd_extract_overrides(ns, _normalizer=FakeNormalizer())
        assert rc != 0

    def test_missing_interviews_dir_returns_error(self, tmp_path):
        eng = tmp_path / "acme"
        eng.mkdir()
        # No 01_interview_inputs/
        ns = argparse.Namespace(engagement=eng)
        from forge.cli import cmd_extract_overrides

        rc = cmd_extract_overrides(ns, _normalizer=FakeNormalizer())
        assert rc != 0


# ---------------------------------------------------------------------------
# Story D3 — review marker + source snippet
# ---------------------------------------------------------------------------


class TestProposedMarkers:
    def test_proposed_header_in_files(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _run_extract(eng)
        for fname in ["icp_overrides.yaml", "channel_overrides.yaml"]:
            content = (eng / "03_overrides" / fname).read_text()
            assert "PROPOSED" in content, f"{fname} must contain PROPOSED marker"
            assert "review before generate" in content.lower(), (
                f"{fname} must contain review instruction"
            )

    def test_source_snippet_in_files(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _run_extract(eng)
        icp_content = (eng / "03_overrides" / "icp_overrides.yaml").read_text()
        # Strip comment lines (lines starting with #) before parsing YAML
        yaml_body = "\n".join(
            line for line in icp_content.splitlines() if not line.startswith("#")
        )
        parsed = yaml.safe_load(yaml_body)
        assert "_source_snippet" in parsed, "icp_overrides.yaml must contain _source_snippet"
        assert len(parsed["_source_snippet"]) > 0

    def test_reviewed_field_is_false(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _run_extract(eng)
        icp_content = (eng / "03_overrides" / "icp_overrides.yaml").read_text()
        parsed = yaml.safe_load(icp_content.replace("# PROPOSED — review before generate\n", ""))
        assert parsed.get("reviewed") is False

    def test_command_prints_review_instruction(self, tmp_path, capsys):
        eng = _make_engagement(tmp_path)
        _run_extract(eng)
        captured = capsys.readouterr()
        assert "Review" in captured.out or "review" in captured.out.lower()
        assert "generate" in captured.out.lower()

    def test_command_exit_zero_on_success(self, tmp_path):
        eng = _make_engagement(tmp_path)
        rc = _run_extract(eng)
        assert rc == 0
