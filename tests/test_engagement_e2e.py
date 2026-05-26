"""End-to-end regression test for the ai-consulting-firm engagement (EPIC G, Story G1 #27).

Asserts:
  1. schema-forge validate --engagement engagements/ai-consulting-firm exits 0
  2. 04_output/ contains all five artifacts (schema .py, modifiers .yaml,
     policy .py, failure_modes/ dir, gold .jsonl)
  3. The generated schema imports cleanly and extraction_guidance() covers
     every label (i.e., guidance keys == {lbl.value for lbl in GtmLabel})

This test is a committed regression guard: if generate or validate regresses,
this test catches it without requiring a re-run of the full engagement pipeline.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
ENGAGEMENT_DIR = REPO_ROOT / "engagements" / "ai-consulting-firm"
OUTPUT_DIR = ENGAGEMENT_DIR / "04_output"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_module(path: Path, module_name: str):
    """Dynamically load a Python file as a module."""
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
    """Return the gtm_*_v1.py schema file in 04_output/."""
    candidates = sorted(OUTPUT_DIR.glob("gtm_*_v1.py"))
    assert candidates, f"No gtm_*_v1.py found in {OUTPUT_DIR}"
    return candidates[0]


def _find_gold_file() -> Path:
    """Return the *_gold.jsonl file in 04_output/."""
    candidates = sorted(OUTPUT_DIR.glob("*_gold.jsonl"))
    assert candidates, f"No *_gold.jsonl found in {OUTPUT_DIR}"
    return candidates[0]


def _find_failure_modes_dir() -> Path:
    """Return the *_failure_modes/ directory in 04_output/."""
    candidates = [p for p in OUTPUT_DIR.iterdir() if p.is_dir() and p.name.endswith("_failure_modes")]
    assert candidates, f"No *_failure_modes/ directory found in {OUTPUT_DIR}"
    return candidates[0]


def _find_modifiers_file() -> Path:
    """Return the *_modifiers.yaml file in 04_output/."""
    candidates = sorted(OUTPUT_DIR.glob("*_modifiers.yaml"))
    assert candidates, f"No *_modifiers.yaml found in {OUTPUT_DIR}"
    return candidates[0]


def _find_policy_file() -> Path:
    """Return the *_policy.py file in 04_output/."""
    candidates = sorted(OUTPUT_DIR.glob("*_policy.py"))
    assert candidates, f"No *_policy.py found in {OUTPUT_DIR}"
    return candidates[0]


# ---------------------------------------------------------------------------
# Test 1 — schema-forge validate exits 0 on the committed engagement
# ---------------------------------------------------------------------------


class TestValidateExitsZero:
    """schema-forge validate --engagement engagements/ai-consulting-firm must exit 0."""

    def test_validate_exits_zero(self):
        """The committed engagement must pass all four validation checks."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "forge.cli",
                "validate",
                "--engagement",
                str(ENGAGEMENT_DIR),
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"schema-forge validate exited {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_validate_via_cli_entry_point(self):
        """Confirm via the schema-forge CLI entry point (not just module invocation)."""
        from forge.cli import main

        rc = main(["validate", "--engagement", str(ENGAGEMENT_DIR)])
        assert rc == 0, f"schema-forge validate returned {rc} for committed engagement"


# ---------------------------------------------------------------------------
# Test 2 — 04_output/ contains all five artifacts
# ---------------------------------------------------------------------------


class TestAllFiveArtifactsPresent:
    """04_output/ must contain all five required artifacts."""

    def test_schema_module_exists(self):
        schema = _find_schema_module()
        assert schema.is_file(), f"Schema module not found: {schema}"
        assert schema.suffix == ".py"

    def test_modifiers_yaml_exists(self):
        modifiers = _find_modifiers_file()
        assert modifiers.is_file(), f"Modifiers YAML not found: {modifiers}"
        assert modifiers.suffix == ".yaml"

    def test_policy_module_exists(self):
        policy = _find_policy_file()
        assert policy.is_file(), f"Policy module not found: {policy}"
        assert policy.suffix == ".py"

    def test_failure_modes_dir_exists(self):
        fm_dir = _find_failure_modes_dir()
        assert fm_dir.is_dir(), f"Failure modes dir not found: {fm_dir}"

    def test_failure_modes_dir_is_non_empty(self):
        fm_dir = _find_failure_modes_dir()
        py_files = [f for f in fm_dir.iterdir() if f.suffix == ".py" and not f.name.startswith("_")]
        assert len(py_files) > 0, f"No .py files in failure modes dir: {fm_dir}"

    def test_gold_jsonl_exists(self):
        gold = _find_gold_file()
        assert gold.is_file(), f"Gold JSONL not found: {gold}"
        assert gold.suffix == ".jsonl"

    def test_gold_jsonl_is_non_empty(self):
        gold = _find_gold_file()
        content = gold.read_text(encoding="utf-8").strip()
        assert content, f"Gold JSONL is empty: {gold}"

    def test_output_dir_has_exactly_five_artifact_types(self):
        """04_output/ contains the five expected artifact types (schema, modifiers, policy, fm_dir, gold)."""
        assert OUTPUT_DIR.is_dir(), f"04_output/ not found: {OUTPUT_DIR}"
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
# Test 3 — generated schema coverage (guidance covers every label)
# ---------------------------------------------------------------------------


class TestSchemaGuidanceCoverage:
    """The generated schema must export extraction_guidance() covering every label."""

    def test_schema_imports_cleanly(self):
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_e2e_schema_import_test")
        assert hasattr(mod, "GtmLabel"), "Schema module must expose GtmLabel"
        assert hasattr(mod, "GtmEntity"), "Schema module must expose GtmEntity"
        assert hasattr(mod, "extraction_guidance"), "Schema module must expose extraction_guidance()"

    def test_extraction_guidance_covers_all_labels(self):
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_e2e_schema_coverage_test")

        guidance: dict = mod.extraction_guidance()
        label_values: set = {lbl.value for lbl in mod.GtmLabel}
        guidance_keys: set = set(guidance.keys())

        missing = label_values - guidance_keys
        extra = guidance_keys - label_values

        assert not missing, (
            f"extraction_guidance() is missing entries for: {sorted(missing)}"
        )
        assert not extra, (
            f"extraction_guidance() has extra keys not in GtmLabel: {sorted(extra)}"
        )

    def test_schema_has_custom_signal_label(self):
        """The ai-consulting-firm schema must include the custom LinkedIn engagement signal."""
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_e2e_schema_custom_signal_test")

        label_values = {lbl.value for lbl in mod.GtmLabel}
        custom_val = "custom.s_linkedin_thought_leadership_engagement"
        assert custom_val in label_values, (
            f"Custom signal {custom_val!r} not found in GtmLabel. "
            f"Check channel_overrides.yaml custom_signals."
        )

    def test_schema_guidance_non_empty_strings(self):
        """Every guidance entry must be a non-empty string."""
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_e2e_schema_guidance_strings_test")

        guidance: dict = mod.extraction_guidance()
        for label_val, definition in guidance.items():
            assert isinstance(definition, str) and definition.strip(), (
                f"Guidance for {label_val!r} is empty or not a string: {definition!r}"
            )

    def test_schema_valid_links_non_empty(self):
        """valid_links() must return at least the baseline link types."""
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_e2e_schema_links_test")

        links = mod.valid_links()
        assert len(links) >= 13, (
            f"Expected at least 13 link types (baseline), got {len(links)}"
        )

    def test_gtm_entity_model_validates(self):
        """GtmEntity must accept a valid entity dict."""
        schema_path = _find_schema_module()
        mod = _load_module(schema_path, "_e2e_entity_model_test")

        entity = mod.GtmEntity.model_validate({
            "label": "account.company_name",
            "text": "Acme Corp",
            "confidence": 0.95,
        })
        assert entity.label.value == "account.company_name"
        assert entity.text == "Acme Corp"
        assert entity.confidence == 0.95


# ---------------------------------------------------------------------------
# Test 4 — custom failure mode (fake_yes_ai_curiosity) is present and callable
# ---------------------------------------------------------------------------


class TestCustomFailureModePresent:
    """The fake_yes_ai_curiosity failure mode must be present in the output."""

    def test_fake_yes_failure_mode_in_output(self):
        fm_dir = _find_failure_modes_dir()
        fm_file = fm_dir / "fake_yes_ai_curiosity.py"
        assert fm_file.is_file(), (
            f"fake_yes_ai_curiosity.py not found in {fm_dir}. "
            f"Files present: {[f.name for f in fm_dir.iterdir()]}"
        )

    def test_fake_yes_failure_mode_detect_is_callable(self):
        fm_dir = _find_failure_modes_dir()
        fm_file = fm_dir / "fake_yes_ai_curiosity.py"
        mod = _load_module(fm_file, "_e2e_fake_yes_fm_test")
        assert hasattr(mod, "detect"), "fake_yes_ai_curiosity must expose detect()"
        assert callable(mod.detect), "detect must be callable"
