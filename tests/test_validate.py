"""Tests for EPIC F — validate (Story F1 #24).

Story F1: run_validate runs the four-check sanity battery over 04_output/.

Happy path: scaffold + valid overrides + generate → validate passes (exit 0).

Corrupt cases (each must exit non-zero):
  (a) an override referencing a non-existent label
  (b) a gold record that violates the schema
  (c) a failure-mode module that raises on import
  (d) missing 04_output/
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import pytest

from forge.scaffold import init_engagement


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

CLIENT = "ai-consulting-firm"
SLUG = "aiconsultingfirm"


def _make_engagement(tmp_path: Path) -> Path:
    eng = tmp_path / "eng"
    init_engagement("gtm", CLIENT, eng)
    return eng


def _write_valid_overrides(eng: Path) -> None:
    overrides_dir = eng / "03_overrides"
    (overrides_dir / "icp_overrides.yaml").write_text(
        textwrap.dedent("""\
            A_EMPLOYEE_RANGE:
              include:
                - "11-50"
                - "51-200"
              exclude:
                - "1-10"
              rationale: "5 won deals all between 25-180 employees"
        """),
        encoding="utf-8",
    )
    (overrides_dir / "channel_overrides.yaml").write_text(
        textwrap.dedent("""\
            signal_weights:
              signal.hiring_trigger: 0.3
              signal.pain_point_mention: 0.9
            custom_signals:
              - name: S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT
                definition: "Prospect engaged with founder's LinkedIn content in last 14 days"
                rationale: "Channel interview — 70% of inbound starts here"
                add_to_schema: true
        """),
        encoding="utf-8",
    )
    (overrides_dir / "modifier_overrides.yaml").write_text(
        textwrap.dedent("""\
            intent_topics:
              add:
                - "LLM evaluation"
              deprioritize:
                - "data warehouse migration"
              rationale: "Client product areas"
        """),
        encoding="utf-8",
    )
    (overrides_dir / "policy_overrides.yaml").write_text(
        textwrap.dedent("""\
            disqualification_rules:
              - condition: "A_EMPLOYEE_RANGE in [1-10]"
                rationale: "Deal economics require >10 employees"
        """),
        encoding="utf-8",
    )
    fm_dir = overrides_dir / "failure_mode_additions"
    fm_dir.mkdir(exist_ok=True)
    (fm_dir / "fake_yes.py").write_text(
        textwrap.dedent('''\
            """Failure mode: prospect is just exploring AI, not a buyer."""


            def detect(entity, source_doc) -> tuple[bool, str | None]:
                return False, None
        '''),
        encoding="utf-8",
    )


def _run_generate(eng: Path) -> int:
    from forge.cli import cmd_generate
    ns = argparse.Namespace(engagement=eng)
    return cmd_generate(ns)


def _run_validate(eng: Path) -> int:
    from forge.cli import main
    return main(["validate", "--engagement", str(eng)])


# ---------------------------------------------------------------------------
# Happy path — all checks pass
# ---------------------------------------------------------------------------


class TestValidateHappyPath:
    def test_validate_passes_after_generate(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        rc_gen = _run_generate(eng)
        assert rc_gen == 0, "generate must succeed first"

        rc_val = _run_validate(eng)
        assert rc_val == 0, "validate must exit 0 on a clean engagement"

    def test_validate_result_ok_flag(self, tmp_path):
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        result = run_validate(eng)
        assert result.ok, f"Validation failed:\n{result.report()}"

    def test_validate_all_four_checks_present(self, tmp_path):
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        result = run_validate(eng)
        check_names = {c.name for c in result.checks}
        assert "schema_coverage" in check_names
        assert "override_label_refs" in check_names
        assert "gold_validation" in check_names
        assert "failure_modes" in check_names


# ---------------------------------------------------------------------------
# Corrupt case (d) — missing 04_output/
# ---------------------------------------------------------------------------


class TestMissingOutputDir:
    def test_missing_output_dir_exits_nonzero(self, tmp_path):
        eng = _make_engagement(tmp_path)
        # Do NOT run generate — 04_output/ is empty (scaffold creates it but empty).
        rc = _run_validate(eng)
        assert rc != 0

    def test_missing_output_dir_check_fails(self, tmp_path):
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        # scaffold creates 04_output/ but leaves it empty.
        result = run_validate(eng)
        assert not result.ok

    def test_entirely_absent_output_dir_exits_nonzero(self, tmp_path):
        eng = _make_engagement(tmp_path)
        import shutil
        shutil.rmtree(eng / "04_output")
        rc = _run_validate(eng)
        assert rc != 0


# ---------------------------------------------------------------------------
# Corrupt case (a) — override referencing a non-existent label
# ---------------------------------------------------------------------------


class TestBadOverrideLabel:
    def _write_bad_icp_override(self, overrides_dir: Path) -> None:
        """Write an icp_overrides.yaml that references a non-existent label."""
        (overrides_dir / "icp_overrides.yaml").write_text(
            textwrap.dedent("""\
                account.nonexistent_label_xyz:
                  include:
                    - "some value"
                  rationale: "This label does not exist in GtmLabel"
            """),
            encoding="utf-8",
        )

    def test_bad_override_label_exits_nonzero(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)  # generate with valid overrides first

        # Now corrupt the override AFTER generate (re-validate picks it up)
        self._write_bad_icp_override(eng / "03_overrides")
        rc = _run_validate(eng)
        assert rc != 0

    def test_bad_override_label_check_fails(self, tmp_path):
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        self._write_bad_icp_override(eng / "03_overrides")
        result = run_validate(eng)
        assert not result.ok
        failed = [c for c in result.checks if not c.passed]
        assert any(c.name == "override_label_refs" for c in failed), (
            f"Expected override_label_refs to fail, got: {[c.name for c in failed]}"
        )


# ---------------------------------------------------------------------------
# Corrupt case (b) — gold record that violates the schema
# ---------------------------------------------------------------------------


class TestBadGoldRecord:
    def _corrupt_gold(self, output_dir: Path) -> None:
        """Overwrite the gold file with one record that has an invalid confidence value."""
        gold_files = list(output_dir.glob("*_gold.jsonl"))
        assert gold_files, "No gold file found to corrupt"
        gold_path = gold_files[0]

        bad_record = {
            "source_doc_id": "test_bad_000",
            "source_type": "email",
            "entities": [
                {
                    "label": "account.company_name",
                    "text": "ACME Corp",
                    "confidence": 9.99,  # invalid: must be <= 1.0
                }
            ],
        }
        gold_path.write_text(json.dumps(bad_record) + "\n", encoding="utf-8")

    def test_bad_gold_record_exits_nonzero(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        self._corrupt_gold(eng / "04_output")
        rc = _run_validate(eng)
        assert rc != 0

    def test_bad_gold_record_check_fails(self, tmp_path):
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        self._corrupt_gold(eng / "04_output")
        result = run_validate(eng)
        assert not result.ok
        failed = [c for c in result.checks if not c.passed]
        assert any(c.name == "gold_validation" for c in failed), (
            f"Expected gold_validation to fail, got: {[c.name for c in failed]}"
        )

    def test_bad_label_in_gold_record_exits_nonzero(self, tmp_path):
        """Gold record with an unrecognized label should fail schema validation."""
        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        output_dir = eng / "04_output"
        gold_files = list(output_dir.glob("*_gold.jsonl"))
        bad_record = {
            "source_doc_id": "test_bad_001",
            "source_type": "email",
            "entities": [
                {
                    "label": "account.nonexistent_field",
                    "text": "ACME Corp",
                    "confidence": 0.9,
                }
            ],
        }
        gold_files[0].write_text(json.dumps(bad_record) + "\n", encoding="utf-8")
        rc = _run_validate(eng)
        assert rc != 0


# ---------------------------------------------------------------------------
# Corrupt case (c) — failure-mode module raises on import
# ---------------------------------------------------------------------------


class TestBadFailureModeModule:
    def _inject_bad_fm(self, fm_dir: Path) -> None:
        """Write a failure-mode module that raises on import."""
        (fm_dir / "fm_bad_import.py").write_text(
            textwrap.dedent('''\
                """Failure mode that raises on import."""
                raise RuntimeError("This module is intentionally broken")


                def detect(entity, source_doc) -> tuple[bool, str | None]:
                    return False, None
            '''),
            encoding="utf-8",
        )

    def _find_fm_dir(self, output_dir: Path) -> Path:
        for p in output_dir.iterdir():
            if p.is_dir() and p.name.endswith("_failure_modes"):
                return p
        raise FileNotFoundError(f"No failure_modes dir in {output_dir}")

    def test_bad_fm_module_exits_nonzero(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        fm_dir = self._find_fm_dir(eng / "04_output")
        self._inject_bad_fm(fm_dir)
        rc = _run_validate(eng)
        assert rc != 0

    def test_bad_fm_module_check_fails(self, tmp_path):
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        fm_dir = self._find_fm_dir(eng / "04_output")
        self._inject_bad_fm(fm_dir)
        result = run_validate(eng)
        assert not result.ok
        failed = [c for c in result.checks if not c.passed]
        assert any(c.name == "failure_modes" for c in failed), (
            f"Expected failure_modes to fail, got: {[c.name for c in failed]}"
        )

    def _find_fm_dir(self, output_dir: Path) -> Path:  # noqa: F811
        for p in output_dir.iterdir():
            if p.is_dir() and p.name.endswith("_failure_modes"):
                return p
        raise FileNotFoundError(f"No failure_modes dir in {output_dir}")


# ---------------------------------------------------------------------------
# "Renamed label" class of bug — label in policy/overrides not in schema
# ---------------------------------------------------------------------------


class TestRenamedLabelBug:
    """
    Validates the spec requirement: 'must catch the renamed-label-in-overrides-
    but-forgot-to-update-the-policy class of bug.'
    """

    def test_renamed_label_in_icp_override_fails(self, tmp_path):
        """If we reference account.old_name (not in GtmLabel), check 2 fails."""
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        # Post-generate, corrupt 03_overrides to reference a label that doesn't exist.
        (eng / "03_overrides" / "icp_overrides.yaml").write_text(
            textwrap.dedent("""\
                account.renamed_old_label:
                  include:
                    - "some value"
                  rationale: "This label was renamed but the override was not updated"
            """),
            encoding="utf-8",
        )
        result = run_validate(eng)
        assert not result.ok
        check_map = {c.name: c for c in result.checks}
        assert not check_map["override_label_refs"].passed

    def test_bad_label_in_policy_condition_fails(self, tmp_path):
        """A label referenced inside a policy condition that doesn't exist must fail."""
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        # Post-generate, corrupt the policy condition to reference a non-existent label.
        (eng / "03_overrides" / "policy_overrides.yaml").write_text(
            textwrap.dedent("""\
                disqualification_rules:
                  - condition: "Q_NOT_A_REAL_LABEL is null"
                    rationale: "bad"
            """),
            encoding="utf-8",
        )
        rc = _run_validate(eng)
        assert rc != 0, "validate must reject an unknown label in a policy condition"

        result = run_validate(eng)
        assert not result.ok
        check_map = {c.name: c for c in result.checks}
        assert not check_map["override_label_refs"].passed
        assert "Q_NOT_A_REAL_LABEL" in check_map["override_label_refs"].detail

    def test_valid_labels_in_policy_condition_pass(self, tmp_path):
        """A condition referencing real labels (and AND/OR keywords) must NOT be flagged."""
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        (eng / "03_overrides" / "policy_overrides.yaml").write_text(
            textwrap.dedent("""\
                disqualification_rules:
                  - condition: "Q_BUDGET_CONFIRMED AND Q_AUTHORITY_IDENTIFIED"
                    rationale: "Both qualification signals required"
            """),
            encoding="utf-8",
        )
        result = run_validate(eng)
        check_map = {c.name: c for c in result.checks}
        assert check_map["override_label_refs"].passed, (
            f"valid labels must not be flagged: {check_map['override_label_refs'].detail}"
        )

    def test_declared_custom_signal_in_policy_condition_passes(self, tmp_path):
        """A custom signal declared in channel_overrides is a valid policy-condition reference (plan §5)."""
        from forge.validate import run_validate

        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)  # declares S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT
        _run_generate(eng)

        (eng / "03_overrides" / "policy_overrides.yaml").write_text(
            textwrap.dedent("""\
                hil_rules:
                  - condition: "S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT AND confidence > 0.5"
                    rationale: "Always human-verify warm-channel signals"
            """),
            encoding="utf-8",
        )
        result = run_validate(eng)
        check_map = {c.name: c for c in result.checks}
        assert check_map["override_label_refs"].passed, (
            f"declared custom signal must not be flagged: {check_map['override_label_refs'].detail}"
        )

    def test_undeclared_custom_signal_in_policy_condition_fails(self, tmp_path):
        """An S_-shaped token that is neither a baseline label nor a declared custom signal still fails."""
        eng = _make_engagement(tmp_path)
        _write_valid_overrides(eng)
        _run_generate(eng)

        (eng / "03_overrides" / "policy_overrides.yaml").write_text(
            textwrap.dedent("""\
                hil_rules:
                  - condition: "S_UNDECLARED_SIGNAL AND confidence > 0.5"
                    rationale: "typo'd / never declared"
            """),
            encoding="utf-8",
        )
        assert _run_validate(eng) != 0, "undeclared S_-token must still be rejected"
