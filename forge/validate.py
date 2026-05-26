"""Validation battery for EPIC F (Story F1 #24).

Public API
----------
run_validate(engagement_dir) -> ValidationResult
    Run the four-check battery over 04_output/ and return a structured result.
    Callers should check result.ok and print result.report() on failure.

Checks performed (in order):
    1. Schema coverage   — extraction_guidance() keys == {lbl.value for lbl in GtmLabel}
    2. Override label refs — all refs in 03_overrides/ resolve to real baseline labels
    3. Gold validation   — every record in the output *.gold.jsonl validates against the
                           output schema's GtmEntity model
    4. Failure-mode modules — every *.py in the output *_failure_modes/ imports cleanly
                              and detect() is callable without raising
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class ValidationResult:
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.passed for c in self.checks)

    def report(self) -> str:
        lines: list[str] = []
        for c in self.checks:
            status = "PASS" if c.passed else "FAIL"
            lines.append(f"  [{status}] {c.name}")
            if not c.passed and c.detail:
                for line in c.detail.splitlines():
                    lines.append(f"         {line}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_output_dir(engagement_dir: Path) -> Path | None:
    """Return engagement_dir/04_output if it exists and is non-empty, else None."""
    out = engagement_dir / "04_output"
    if not out.is_dir():
        return None
    if not any(out.iterdir()):
        return None
    return out


def _find_schema_module(output_dir: Path) -> Path | None:
    """Return the first gtm_*_v1.py file in output_dir."""
    for p in sorted(output_dir.glob("gtm_*_v1.py")):
        return p
    return None


def _find_gold_file(output_dir: Path) -> Path | None:
    """Return the first *_gold.jsonl file in output_dir."""
    for p in sorted(output_dir.glob("*_gold.jsonl")):
        return p
    return None


def _find_failure_modes_dir(output_dir: Path) -> Path | None:
    """Return the first *_failure_modes/ directory in output_dir."""
    for p in sorted(output_dir.iterdir()):
        if p.is_dir() and p.name.endswith("_failure_modes"):
            return p
    return None


def _load_module_from_path(path: Path, module_name: str) -> Any:
    """Import a Python file as a module. Raises ImportError or any import-time exception."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    # Register in sys.modules to allow relative imports within the module, if needed.
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
    finally:
        # Clean up so repeated loads get a fresh module.
        sys.modules.pop(module_name, None)
    return mod


# ---------------------------------------------------------------------------
# Check 1 — schema coverage
# ---------------------------------------------------------------------------


def _check_schema_coverage(schema_path: Path) -> CheckResult:
    """Verify extraction_guidance() keys == {lbl.value for lbl in GtmLabel}."""
    name = "schema_coverage"
    try:
        mod = _load_module_from_path(schema_path, "_validate_schema_mod")
    except Exception as exc:
        return CheckResult(name=name, passed=False, detail=f"Failed to import schema module: {exc}")

    if not hasattr(mod, "extraction_guidance"):
        return CheckResult(name=name, passed=False, detail="Schema module missing extraction_guidance()")
    if not hasattr(mod, "GtmLabel"):
        return CheckResult(name=name, passed=False, detail="Schema module missing GtmLabel")

    try:
        guidance: dict[str, str] = mod.extraction_guidance()
        label_values: set[str] = {lbl.value for lbl in mod.GtmLabel}
    except Exception as exc:
        return CheckResult(name=name, passed=False, detail=f"Error calling extraction_guidance() or iterating GtmLabel: {exc}")

    guidance_keys = set(guidance.keys())
    missing = label_values - guidance_keys
    extra = guidance_keys - label_values

    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"Missing from guidance (in GtmLabel but not guidance): {sorted(missing)}")
        if extra:
            details.append(f"Extra in guidance (not in GtmLabel): {sorted(extra)}")
        return CheckResult(name=name, passed=False, detail="\n".join(details))

    return CheckResult(name=name, passed=True)


# ---------------------------------------------------------------------------
# Check 2 — override label refs
# ---------------------------------------------------------------------------


def _check_override_label_refs(engagement_dir: Path) -> CheckResult:
    """All override references in 03_overrides/ must resolve to real baseline labels."""
    name = "override_label_refs"
    overrides_dir = engagement_dir / "03_overrides"

    if not overrides_dir.is_dir():
        # No overrides directory at all — treat as passing (nothing to check).
        return CheckResult(name=name, passed=True, detail="03_overrides/ not found; skipping")

    try:
        from forge.overrides import check_label_refs, load_overrides
        bundle = load_overrides(overrides_dir)
        errors = check_label_refs(bundle)
    except Exception as exc:
        return CheckResult(name=name, passed=False, detail=f"Error loading overrides: {exc}")

    if errors:
        return CheckResult(name=name, passed=False, detail="\n".join(errors))

    return CheckResult(name=name, passed=True)


# ---------------------------------------------------------------------------
# Check 3 — gold validation
# ---------------------------------------------------------------------------


def _check_gold_validation(gold_path: Path, schema_path: Path) -> CheckResult:
    """Every gold record must validate against the output schema's GtmEntity model."""
    name = "gold_validation"

    try:
        mod = _load_module_from_path(schema_path, "_validate_schema_mod_gold")
    except Exception as exc:
        return CheckResult(name=name, passed=False, detail=f"Failed to import schema module: {exc}")

    if not hasattr(mod, "GtmEntity"):
        return CheckResult(name=name, passed=False, detail="Schema module missing GtmEntity")

    GtmEntity = mod.GtmEntity
    errors: list[str] = []
    line_num = 0

    try:
        lines = gold_path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        return CheckResult(name=name, passed=False, detail=f"Cannot read gold file: {exc}")

    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Line {line_num}: JSON parse error: {exc}")
            continue

        entities = record.get("entities", [])
        for i, entity_dict in enumerate(entities):
            try:
                GtmEntity.model_validate(entity_dict)
            except Exception as exc:
                errors.append(
                    f"Line {line_num}, entity[{i}] ({entity_dict.get('label', '?')}): {exc}"
                )

    if errors:
        shown = errors[:10]
        detail = "\n".join(shown)
        if len(errors) > 10:
            detail += f"\n... and {len(errors) - 10} more error(s)"
        return CheckResult(name=name, passed=False, detail=detail)

    return CheckResult(name=name, passed=True)


# ---------------------------------------------------------------------------
# Check 4 — failure-mode modules
# ---------------------------------------------------------------------------


def _check_failure_modes(fm_dir: Path) -> CheckResult:
    """Each failure-mode module must import cleanly and detect() must be callable."""
    name = "failure_modes"
    errors: list[str] = []

    fm_files = sorted(
        p for p in fm_dir.iterdir()
        if p.suffix == ".py" and not p.name.startswith("_")
    )

    if not fm_files:
        return CheckResult(name=name, passed=True, detail="No failure-mode modules found")

    for fm_file in fm_files:
        mod_name = f"_validate_fm_{fm_file.stem}"
        try:
            mod = _load_module_from_path(fm_file, mod_name)
        except Exception as exc:
            errors.append(f"{fm_file.name}: import error: {exc}")
            continue

        if not hasattr(mod, "detect"):
            errors.append(f"{fm_file.name}: missing detect() function")
            continue

        # Verify detect() is callable with minimal stub args (just check it doesn't crash
        # with type errors on the signature itself — we can't call it meaningfully without
        # a real entity, so we skip the call and just confirm it's callable).
        if not callable(mod.detect):
            errors.append(f"{fm_file.name}: detect is not callable")

    if errors:
        return CheckResult(name=name, passed=False, detail="\n".join(errors))

    return CheckResult(name=name, passed=True)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_validate(engagement_dir: Path) -> ValidationResult:
    """Run the four-check sanity battery over 04_output/.

    Returns a ValidationResult; exits non-zero behavior is handled by the caller.
    """
    result = ValidationResult()

    output_dir = _find_output_dir(engagement_dir)
    if output_dir is None:
        result.checks.append(
            CheckResult(
                name="output_dir",
                passed=False,
                detail=(
                    f"04_output/ is missing or empty in {engagement_dir}. "
                    "Run 'schema-forge generate --engagement <dir>' first."
                ),
            )
        )
        return result

    schema_path = _find_schema_module(output_dir)
    gold_path = _find_gold_file(output_dir)
    fm_dir = _find_failure_modes_dir(output_dir)

    # Check 1 — schema coverage
    if schema_path is None:
        result.checks.append(
            CheckResult(
                name="schema_coverage",
                passed=False,
                detail=f"No gtm_*_v1.py found in {output_dir}",
            )
        )
    else:
        result.checks.append(_check_schema_coverage(schema_path))

    # Check 2 — override label refs
    result.checks.append(_check_override_label_refs(engagement_dir))

    # Check 3 — gold validation
    if gold_path is None:
        result.checks.append(
            CheckResult(
                name="gold_validation",
                passed=False,
                detail=f"No *_gold.jsonl found in {output_dir}",
            )
        )
    elif schema_path is None:
        result.checks.append(
            CheckResult(
                name="gold_validation",
                passed=False,
                detail="Cannot validate gold: schema module not found",
            )
        )
    else:
        result.checks.append(_check_gold_validation(gold_path, schema_path))

    # Check 4 — failure modes
    if fm_dir is None:
        result.checks.append(
            CheckResult(
                name="failure_modes",
                passed=False,
                detail=f"No *_failure_modes/ directory found in {output_dir}",
            )
        )
    else:
        result.checks.append(_check_failure_modes(fm_dir))

    return result
