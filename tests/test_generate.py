"""Tests for EPIC E — generate (deterministic merge + manifest).

Story E1: run_generate merges 02_baseline/ + 03_overrides/ into 04_output/
          with no LLM call.
Story E2: per-type merge semantics verified.
Story E3: manifest.yaml audit trail (generated_at, sha256s, changes_from_baseline).

Byte-determinism: run generate twice with a fixed clock → identical bytes for all
five artifacts and the manifest.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from forge.scaffold import init_engagement


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXED_NOW = datetime(2026, 5, 25, 16, 42, 0, tzinfo=timezone.utc)

CLIENT = "ai-consulting-firm"
SLUG = "aiconsultingfirm"  # _slugify strips hyphens


def _make_engagement(tmp_path: Path) -> Path:
    """Initialize a full engagement using scaffold, then write sample overrides."""
    eng = tmp_path / "acme"
    init_engagement("gtm", CLIENT, eng)
    return eng


def _write_override_yamls(eng: Path) -> None:
    overrides_dir = eng / "03_overrides"

    # Keys use enum MEMBER names (A_EMPLOYEE_RANGE), matching the §5 plan
    # example. The merge must resolve these to label VALUES
    # (account.employee_range) when appending guidance — never introduce a
    # guidance key equal to the member name.
    (overrides_dir / "icp_overrides.yaml").write_text(
        textwrap.dedent("""\
            A_EMPLOYEE_RANGE:
              include:
                - "11-50"
                - "51-200"
              exclude:
                - "1-10"
              rationale: "5 won deals all between 25-180 employees"
            A_INDUSTRY:
              preferred:
                - "Professional services"
                - "AI/ML services"
              rationale: "ICP interview Q3 — closed-won deals in services verticals"
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
                - "AI governance"
                - "RAG implementation"
              deprioritize:
                - "data warehouse migration"
              rationale: "Client product areas from channel interview"
        """),
        encoding="utf-8",
    )

    (overrides_dir / "policy_overrides.yaml").write_text(
        textwrap.dedent("""\
            disqualification_rules:
              - condition: "A_EMPLOYEE_RANGE in [1-10]"
                rationale: "Deal economics require >10 employees"
            auto_pass_rules:
              - condition: "Q_BUDGET_CONFIRMED AND Q_AUTHORITY_IDENTIFIED AND confidence > 0.7"
                rationale: "Two of MEDDIC's four = auto-route to AE"
            hil_rules:
              - condition: "S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT AND confidence > 0.5"
                rationale: "Always human-verify warm-channel signals"
        """),
        encoding="utf-8",
    )

    # One failure mode addition
    fm_dir = overrides_dir / "failure_mode_additions"
    fm_dir.mkdir(exist_ok=True)
    (fm_dir / "fake_yes_ai_curiosity.py").write_text(
        textwrap.dedent('''\
            """Failure mode: prospect is just exploring AI, not a buyer."""


            def detect(entity, source_doc) -> tuple[bool, str | None]:
                return False, None
        '''),
        encoding="utf-8",
    )


def _run_generate(eng: Path, now: datetime = FIXED_NOW) -> int:
    from forge.cli import cmd_generate

    ns = argparse.Namespace(engagement=eng)
    return cmd_generate(ns, _now=now)


# ---------------------------------------------------------------------------
# Story E1 — run_generate writes all five artifacts + manifest.yaml
# ---------------------------------------------------------------------------


class TestAllArtifactsExist:
    def test_five_artifacts_and_manifest_written(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        rc = _run_generate(eng)

        assert rc == 0, "generate must exit zero"

        out = eng / "04_output"
        assert (out / f"gtm_{SLUG}_v1.py").exists(), "schema not written"
        assert (out / f"gtm_{SLUG}_modifiers.yaml").exists(), "modifiers not written"
        assert (out / f"gtm_{SLUG}_policy.py").exists(), "policy not written"
        assert (out / f"gtm_{SLUG}_failure_modes").is_dir(), "failure_modes dir not written"
        assert (out / f"gtm_{SLUG}_gold.jsonl").exists(), "gold not written"
        assert (eng / "manifest.yaml").exists(), "manifest.yaml not written"

    def test_failure_modes_dir_contains_baseline_modes(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        fm_dir = eng / "04_output" / f"gtm_{SLUG}_failure_modes"
        fm_files = {f.name for f in fm_dir.iterdir() if f.suffix == ".py"}
        assert "fm01_own_product_as_intent.py" in fm_files
        assert "fm25_timeline_from_fiscal_year_language.py" in fm_files

    def test_failure_modes_dir_contains_client_addition(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        fm_dir = eng / "04_output" / f"gtm_{SLUG}_failure_modes"
        assert (fm_dir / "fake_yes_ai_curiosity.py").exists()

    def test_gold_carried_unchanged(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        baseline_gold = (eng / "02_baseline" / "synthetic_gold.jsonl").read_bytes()
        output_gold = (eng / "04_output" / f"gtm_{SLUG}_gold.jsonl").read_bytes()
        assert baseline_gold == output_gold, "gold must be carried byte-for-byte from baseline"


# ---------------------------------------------------------------------------
# Story E1 — byte-determinism
# ---------------------------------------------------------------------------


class TestByteDeterminism:
    def test_two_runs_produce_identical_output(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)

        _run_generate(eng, now=FIXED_NOW)
        out1: dict[str, bytes] = {}
        out_dir = eng / "04_output"
        for p in sorted(out_dir.rglob("*")):
            if p.is_file():
                out1[str(p.relative_to(eng))] = p.read_bytes()
        out1["manifest.yaml"] = (eng / "manifest.yaml").read_bytes()

        _run_generate(eng, now=FIXED_NOW)
        out2: dict[str, bytes] = {}
        for p in sorted(out_dir.rglob("*")):
            if p.is_file():
                out2[str(p.relative_to(eng))] = p.read_bytes()
        out2["manifest.yaml"] = (eng / "manifest.yaml").read_bytes()

        assert out1.keys() == out2.keys(), "file sets differ between runs"
        for key in out1:
            assert out1[key] == out2[key], f"{key} is not byte-identical across runs"


# ---------------------------------------------------------------------------
# Story E2 — per-type merge semantics
# ---------------------------------------------------------------------------


class TestSchemaMerge:
    def test_schema_module_imports_cleanly(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_path = eng / "04_output" / f"gtm_{SLUG}_v1.py"
        spec = importlib.util.spec_from_file_location(f"gtm_{SLUG}_v1", schema_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "GtmLabel")
        assert hasattr(mod, "GtmEntity")
        assert hasattr(mod, "extraction_guidance")
        assert hasattr(mod, "valid_links")

    def test_extraction_guidance_covers_all_base_labels(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_path = eng / "04_output" / f"gtm_{SLUG}_v1.py"
        spec = importlib.util.spec_from_file_location(f"gtm_{SLUG}_v1", schema_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        guidance = mod.extraction_guidance()
        for lbl in mod.GtmLabel:
            assert lbl.value in guidance, f"extraction_guidance missing label: {lbl.value}"

    def test_extraction_guidance_covers_custom_signal(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_path = eng / "04_output" / f"gtm_{SLUG}_v1.py"
        spec = importlib.util.spec_from_file_location(f"gtm_{SLUG}_v1", schema_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        guidance = mod.extraction_guidance()
        custom_key = "custom.s_linkedin_thought_leadership_engagement"
        assert custom_key in guidance, (
            f"extraction_guidance must include custom signal key {custom_key!r}"
        )
        assert "LinkedIn" in guidance[custom_key] or "linkedin" in guidance[custom_key].lower()

    def test_guidance_keys_exactly_equal_label_values(self, tmp_path):
        """Contract: guidance keys are EXACTLY the set of label values.

        The fixture narrows A_EMPLOYEE_RANGE (icp override, keyed by member
        name) AND adds a custom signal (channel override). A regression where
        the icp append uses the enum member name introduces a stray
        'A_EMPLOYEE_RANGE' guidance key — this asserts no missing AND no extra.
        """
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_path = eng / "04_output" / f"gtm_{SLUG}_v1.py"
        spec = importlib.util.spec_from_file_location(f"gtm_{SLUG}_v1", schema_path)
        generated = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generated)

        assert set(generated.extraction_guidance().keys()) == {
            l.value for l in generated.GtmLabel
        }

    def test_icp_append_keyed_by_label_value_not_member_name(self, tmp_path):
        """The §5 preferred/restrict sentence must land on the label VALUE entry."""
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_path = eng / "04_output" / f"gtm_{SLUG}_v1.py"
        spec = importlib.util.spec_from_file_location(f"gtm_{SLUG}_v1", schema_path)
        generated = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generated)

        guidance = generated.extraction_guidance()
        # No guidance key may equal an enum member name.
        member_names = {l.name for l in generated.GtmLabel}
        assert member_names.isdisjoint(guidance.keys())
        # The appended sentence modifies the existing employee_range definition.
        assert "11-50" in guidance["account.employee_range"]

    def test_schema_has_custom_label_enum_member(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_path = eng / "04_output" / f"gtm_{SLUG}_v1.py"
        spec = importlib.util.spec_from_file_location(f"gtm_{SLUG}_v1", schema_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        label_values = {lbl.value for lbl in mod.GtmLabel}
        assert "custom.s_linkedin_thought_leadership_engagement" in label_values

    def test_schema_has_no_spine_or_forge_import(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_text = (eng / "04_output" / f"gtm_{SLUG}_v1.py").read_text()
        assert "from forge" not in schema_text, "schema must not import from forge"
        assert "import forge" not in schema_text, "schema must not import forge"
        assert "from spine" not in schema_text, "schema must not import from spine"
        assert "import spine" not in schema_text, "schema must not import spine"

    def test_icp_guidance_appended(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_text = (eng / "04_output" / f"gtm_{SLUG}_v1.py").read_text()
        # Should contain ICP override text
        assert "Professional services" in schema_text

    def test_signal_weights_in_schema(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        schema_text = (eng / "04_output" / f"gtm_{SLUG}_v1.py").read_text()
        assert "SIGNAL_WEIGHTS" in schema_text
        assert "signal.pain_point_mention" in schema_text


class TestModifiersMerge:
    def test_modifiers_yaml_contains_client_topics(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        modifiers_text = (eng / "04_output" / f"gtm_{SLUG}_modifiers.yaml").read_text()
        data = yaml.safe_load(modifiers_text)
        client_topics = data["signal"]["intent_topics"]["topics"]["client_specific"]
        assert "LLM evaluation" in client_topics
        assert "AI governance" in client_topics
        assert "RAG implementation" in client_topics

    def test_modifiers_yaml_contains_deprioritized(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        modifiers_text = (eng / "04_output" / f"gtm_{SLUG}_modifiers.yaml").read_text()
        data = yaml.safe_load(modifiers_text)
        deprioritized = data["signal"]["intent_topics"]["deprioritized"]
        assert "data warehouse migration" in deprioritized


class TestPolicyMerge:
    def test_policy_contains_disqualification_rule(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        policy_text = (eng / "04_output" / f"gtm_{SLUG}_policy.py").read_text()
        assert "A_EMPLOYEE_RANGE in [1-10]" in policy_text
        assert "Deal economics require >10 employees" in policy_text

    def test_policy_contains_auto_pass_rule(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        policy_text = (eng / "04_output" / f"gtm_{SLUG}_policy.py").read_text()
        assert "Q_BUDGET_CONFIRMED AND Q_AUTHORITY_IDENTIFIED" in policy_text

    def test_policy_contains_hil_rule(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        policy_text = (eng / "04_output" / f"gtm_{SLUG}_policy.py").read_text()
        assert "S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT AND confidence > 0.5" in policy_text

    def test_policy_preserves_baseline_logic(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        policy_text = (eng / "04_output" / f"gtm_{SLUG}_policy.py").read_text()
        # Baseline function must still be present
        assert "def disposition(" in policy_text
        assert "REQUIRED_FOR_QUALIFIED" in policy_text


# ---------------------------------------------------------------------------
# Story E3 — manifest.yaml audit trail
# ---------------------------------------------------------------------------


class TestManifest:
    def test_manifest_has_generated_at(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng, now=FIXED_NOW)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        assert data["generated_at"] == "2026-05-25T16:42:00Z"

    def test_manifest_has_baseline_version(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        assert data["baseline_version"] == "gtm_v1.0"

    def test_manifest_has_override_sha256s(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        overrides = data["overrides"]
        assert "icp_overrides.yaml" in overrides
        assert overrides["icp_overrides.yaml"].startswith("sha256:")
        assert "channel_overrides.yaml" in overrides
        assert overrides["channel_overrides.yaml"].startswith("sha256:")

    def test_manifest_sha256_matches_file(self, tmp_path):
        import hashlib

        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        for fname, sha_entry in data["overrides"].items():
            expected_sha = hashlib.sha256(
                (eng / "03_overrides" / fname).read_bytes()
            ).hexdigest()
            assert sha_entry == f"sha256:{expected_sha}", (
                f"{fname}: manifest sha256 does not match file content"
            )

    def test_manifest_changes_from_baseline_not_empty(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        changes = data["output"]["changes_from_baseline"]
        assert len(changes) > 0, "changes_from_baseline must not be empty"

    def test_manifest_changes_carry_rationale(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        changes = data["output"]["changes_from_baseline"]
        # Each change for ICP/channel/policy/modifier should mention the rationale
        all_text = " ".join(changes)
        assert "5 won deals all between 25-180 employees" in all_text
        assert "Channel interview" in all_text
        assert "Deal economics require >10 employees" in all_text

    def test_manifest_changes_carry_source_file_reference(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        changes = data["output"]["changes_from_baseline"]
        all_text = " ".join(changes)
        assert "icp_overrides.yaml" in all_text
        assert "channel_overrides.yaml" in all_text
        assert "policy_overrides.yaml" in all_text

    def test_manifest_lists_failure_mode_addition(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        changes = data["output"]["changes_from_baseline"]
        all_text = " ".join(changes)
        assert "fake_yes_ai_curiosity.py" in all_text

    def test_manifest_output_schema_filename(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        _run_generate(eng)

        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        assert data["output"]["schema"] == f"gtm_{SLUG}_v1.py"

    def test_manifest_injectable_clock(self, tmp_path):
        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)

        custom_now = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        _run_generate(eng, now=custom_now)
        data = yaml.safe_load((eng / "manifest.yaml").read_text())
        assert data["generated_at"] == "2025-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


class TestCliGenerate:
    def test_generate_via_cli_returns_zero(self, tmp_path):
        from forge.cli import main

        eng = _make_engagement(tmp_path)
        _write_override_yamls(eng)
        rc = main(["generate", "--engagement", str(eng)])
        assert rc == 0

    def test_generate_nonexistent_dir_returns_nonzero(self):
        from forge.cli import main

        rc = main(["generate", "--engagement", "/tmp/__no_such_dir_generate_test__"])
        assert rc != 0

    def test_generate_no_manifest_returns_nonzero(self, tmp_path):
        """A dir that exists but has no manifest.yaml should fail."""
        from forge.cli import main

        bare = tmp_path / "bare"
        bare.mkdir()
        rc = main(["generate", "--engagement", str(bare)])
        assert rc != 0
