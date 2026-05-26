"""End-to-end regression test for the sap-joule engagement (stories #43–#56).

Asserts:
  1. schema-forge validate --engagement engagements/sap-joule exits 0
  2. 04_output/ contains all five artifacts (schema .py, modifiers .yaml,
     policy .py, failure_modes/ dir, gold .jsonl)
  3. The generated schema imports cleanly and extraction_guidance() covers
     every label including all 6 custom signals
  4. All 6 custom signals are present as GtmLabel members with 'custom.' prefix
  5. All 8 SAP-specific failure mode modules are present and detect() is callable
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
ENGAGEMENT_DIR = REPO_ROOT / "engagements" / "sap-joule"
OUTPUT_DIR = ENGAGEMENT_DIR / "04_output"

EXPECTED_CUSTOM_SIGNALS = [
    "custom.s_s4_migration_timeline",
    "custom.s_joule_interest",
    "custom.s_clean_core_initiative",
    "custom.s_rise_adoption",
    "custom.s_sap_field_co_sell",
    "custom.s_si_partner_involved",
]

EXPECTED_FAILURE_MODE_FILES = [
    "sap_fm01_ecc_only_no_roadmap.py",
    "sap_fm02_channel_mirage_ae_excitement.py",
    "sap_fm03_partner_mirage_no_live_program.py",
    "sap_fm04_joule_interest_from_sap_marketing.py",
    "sap_fm05_rise_migration_as_joule_intent.py",
    "sap_fm06_sap_vp_title_inflation_reseller.py",
    "sap_fm07_clean_core_false_positive.py",
    "sap_fm08_stale_sap_module_breadth.py",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None, f"Cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.modules.pop(module_name, None)
    return mod


def _find_schema_module() -> Path:
    candidates = sorted(OUTPUT_DIR.glob("gtm_*_v1.py"))
    assert candidates, f"No gtm_*_v1.py found in {OUTPUT_DIR}"
    return candidates[0]


def _find_failure_modes_dir() -> Path:
    candidates = [p for p in OUTPUT_DIR.iterdir() if p.is_dir() and p.name.endswith("_failure_modes")]
    assert candidates, f"No *_failure_modes/ dir found in {OUTPUT_DIR}"
    return candidates[0]


# ---------------------------------------------------------------------------
# Test 1 — validate exits 0
# ---------------------------------------------------------------------------


class TestValidateExitsZero:
    """schema-forge validate --engagement engagements/sap-joule must exit 0."""

    def test_validate_exits_zero(self):
        result = subprocess.run(
            [sys.executable, "-m", "forge.cli", "validate", "--engagement", str(ENGAGEMENT_DIR)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"schema-forge validate exited {result.returncode}.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_validate_via_cli_entry_point(self):
        from forge.cli import main
        rc = main(["validate", "--engagement", str(ENGAGEMENT_DIR)])
        assert rc == 0, f"schema-forge validate returned {rc} for sap-joule engagement"


# ---------------------------------------------------------------------------
# Test 2 — 04_output/ contains all five artifact types
# ---------------------------------------------------------------------------


class TestAllFiveArtifactsPresent:
    """04_output/ must contain all five required artifacts."""

    def test_schema_module_exists(self):
        schema = _find_schema_module()
        assert schema.is_file()
        assert schema.suffix == ".py"

    def test_modifiers_yaml_exists(self):
        candidates = sorted(OUTPUT_DIR.glob("*_modifiers.yaml"))
        assert candidates, f"No *_modifiers.yaml found in {OUTPUT_DIR}"
        assert candidates[0].suffix == ".yaml"

    def test_policy_module_exists(self):
        candidates = sorted(OUTPUT_DIR.glob("*_policy.py"))
        assert candidates, f"No *_policy.py found in {OUTPUT_DIR}"
        assert candidates[0].suffix == ".py"

    def test_failure_modes_dir_exists(self):
        fm_dir = _find_failure_modes_dir()
        assert fm_dir.is_dir()

    def test_failure_modes_dir_is_non_empty(self):
        fm_dir = _find_failure_modes_dir()
        py_files = [f for f in fm_dir.iterdir() if f.suffix == ".py" and not f.name.startswith("_")]
        assert len(py_files) > 0

    def test_gold_jsonl_exists(self):
        candidates = sorted(OUTPUT_DIR.glob("*_gold.jsonl"))
        assert candidates, f"No *_gold.jsonl found in {OUTPUT_DIR}"
        assert candidates[0].suffix == ".jsonl"

    def test_gold_jsonl_is_non_empty(self):
        candidates = sorted(OUTPUT_DIR.glob("*_gold.jsonl"))
        assert candidates
        content = candidates[0].read_text(encoding="utf-8").strip()
        assert content

    def test_output_dir_has_exactly_five_artifact_types(self):
        schemas = sorted(OUTPUT_DIR.glob("gtm_*_v1.py"))
        modifiers = sorted(OUTPUT_DIR.glob("*_modifiers.yaml"))
        policies = sorted(OUTPUT_DIR.glob("*_policy.py"))
        golds = sorted(OUTPUT_DIR.glob("*_gold.jsonl"))
        fm_dirs = [p for p in OUTPUT_DIR.iterdir() if p.is_dir() and p.name.endswith("_failure_modes")]
        assert len(schemas) == 1, f"Expected 1 schema module, got: {schemas}"
        assert len(modifiers) == 1, f"Expected 1 modifiers YAML, got: {modifiers}"
        assert len(policies) == 1, f"Expected 1 policy module, got: {policies}"
        assert len(golds) == 1, f"Expected 1 gold JSONL, got: {golds}"
        assert len(fm_dirs) == 1, f"Expected 1 failure_modes/ dir, got: {fm_dirs}"


# ---------------------------------------------------------------------------
# Test 3 — schema guidance coverage including custom signals
# ---------------------------------------------------------------------------


class TestSchemaGuidanceCoverage:
    """The generated schema must export extraction_guidance() covering every label."""

    def test_schema_imports_cleanly(self):
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_sj_e2e_schema_import")
        assert hasattr(mod, "GtmLabel")
        assert hasattr(mod, "GtmEntity")
        assert hasattr(mod, "extraction_guidance")

    def test_extraction_guidance_covers_all_labels(self):
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_sj_e2e_schema_coverage")
        guidance: dict = mod.extraction_guidance()
        label_values: set = {lbl.value for lbl in mod.GtmLabel}
        guidance_keys: set = set(guidance.keys())
        missing = label_values - guidance_keys
        extra = guidance_keys - label_values
        assert not missing, f"extraction_guidance() is missing: {sorted(missing)}"
        assert not extra, f"extraction_guidance() has extra keys: {sorted(extra)}"

    def test_all_six_custom_signals_in_schema(self):
        """The sap-joule schema must include all 6 declared custom signals."""
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_sj_e2e_custom_signals")
        label_values = {lbl.value for lbl in mod.GtmLabel}
        for custom_val in EXPECTED_CUSTOM_SIGNALS:
            assert custom_val in label_values, (
                f"Custom signal {custom_val!r} not found in GtmLabel. "
                f"Check channel_overrides.yaml custom_signals."
            )

    def test_schema_has_36_labels(self):
        """30 baseline + 6 custom = 36 labels total."""
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_sj_e2e_label_count")
        label_values = {lbl.value for lbl in mod.GtmLabel}
        assert len(label_values) == 36, (
            f"Expected 36 labels (30 baseline + 6 custom), got {len(label_values)}: "
            f"{sorted(label_values)}"
        )

    def test_guidance_non_empty_strings(self):
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_sj_e2e_guidance_strings")
        guidance: dict = mod.extraction_guidance()
        for label_val, definition in guidance.items():
            assert isinstance(definition, str) and definition.strip(), (
                f"Guidance for {label_val!r} is empty or not a string: {definition!r}"
            )

    def test_valid_links_non_empty(self):
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_sj_e2e_links")
        links = mod.valid_links()
        assert len(links) >= 13, f"Expected >= 13 link types, got {len(links)}"

    def test_gtm_entity_model_validates(self):
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_sj_e2e_entity_model")
        entity = mod.GtmEntity.model_validate({
            "label": "account.company_name",
            "text": "BASF SE",
            "confidence": 0.97,
        })
        assert entity.label.value == "account.company_name"

    def test_custom_signal_entity_validates(self):
        """Custom signal labels must be valid in GtmEntity."""
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_sj_e2e_custom_entity")
        entity = mod.GtmEntity.model_validate({
            "label": "custom.s_joule_interest",
            "text": "We want to activate Joule for our FI period-close by Q4",
            "confidence": 0.91,
        })
        assert entity.label.value == "custom.s_joule_interest"


# ---------------------------------------------------------------------------
# Test 4 — all 8 SAP failure mode modules present and callable
# ---------------------------------------------------------------------------


class TestSapFailureModulesPresent:
    """All 8 SAP-specific failure mode modules must be in 04_output/ and callable."""

    def test_all_sap_failure_mode_files_present(self):
        fm_dir = _find_failure_modes_dir()
        present = {f.name for f in fm_dir.iterdir() if f.suffix == ".py" and not f.name.startswith("_")}
        for expected_file in EXPECTED_FAILURE_MODE_FILES:
            assert expected_file in present, (
                f"{expected_file} not found in {fm_dir}. Present: {sorted(present)}"
            )

    @pytest.mark.parametrize("fm_filename", EXPECTED_FAILURE_MODE_FILES)
    def test_failure_mode_detect_callable(self, fm_filename: str):
        fm_dir = _find_failure_modes_dir()
        fm_file = fm_dir / fm_filename
        assert fm_file.is_file(), f"{fm_filename} not found in {fm_dir}"
        mod = _load_module(fm_file, f"_sj_e2e_fm_{fm_file.stem}")
        assert hasattr(mod, "detect"), f"{fm_filename}: missing detect()"
        assert callable(mod.detect), f"{fm_filename}: detect is not callable"

    @pytest.mark.parametrize("fm_filename", EXPECTED_FAILURE_MODE_FILES)
    def test_failure_mode_has_fixture(self, fm_filename: str):
        fm_dir = _find_failure_modes_dir()
        fm_file = fm_dir / fm_filename
        mod = _load_module(fm_file, f"_sj_e2e_fm_fixture_{fm_file.stem}")
        has_fixture = (
            hasattr(mod, "FIXTURE_ENTITY") or hasattr(mod, "FIXTURE_SOURCE")
        )
        assert has_fixture, (
            f"{fm_filename}: no FIXTURE_ENTITY or FIXTURE_SOURCE defined. "
            f"Add a fixture entity and/or source for test documentation."
        )

    def test_ecc_only_detect_returns_true_on_fixture(self):
        """Smoke-test: ECC-only failure mode fires on its own fixture."""
        fm_dir = _find_failure_modes_dir()
        fm_file = fm_dir / "sap_fm01_ecc_only_no_roadmap.py"
        mod = _load_module(fm_file, "_sj_e2e_fm_ecc_smoke")
        detected, reason = mod.detect(mod.FIXTURE_ENTITY, mod.FIXTURE_SOURCE)
        assert detected is True, f"Expected True, got {detected}; reason: {reason}"
        assert reason and len(reason) > 0

    def test_channel_mirage_detect_returns_true_on_fixture(self):
        """Smoke-test: channel mirage failure mode fires on its own fixture."""
        fm_dir = _find_failure_modes_dir()
        fm_file = fm_dir / "sap_fm02_channel_mirage_ae_excitement.py"
        mod = _load_module(fm_file, "_sj_e2e_fm_mirage_smoke")
        detected, reason = mod.detect(mod.FIXTURE_ENTITY, mod.FIXTURE_SOURCE)
        assert detected is True, f"Expected True, got {detected}; reason: {reason}"
        assert reason and len(reason) > 0


# ---------------------------------------------------------------------------
# Test 5 — override label refs are clean
# ---------------------------------------------------------------------------


class TestOverrideLabelRefs:
    """All label references in 03_overrides/ must resolve to valid GtmLabel or custom signals."""

    def test_override_label_refs_clean(self):
        from forge.overrides import check_label_refs, load_overrides
        overrides_dir = ENGAGEMENT_DIR / "03_overrides"
        bundle = load_overrides(overrides_dir)
        errors = check_label_refs(bundle)
        assert not errors, (
            f"Override label reference errors in sap-joule engagement:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
