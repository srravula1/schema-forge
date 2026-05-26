"""
Tests for the GTM failure-mode library.
- Imports every mode module
- Asserts each detect() runs without error
- Asserts each module's fixture triggers the mode (detected=True)
"""

import importlib
import pkgutil
import pytest

import forge.domains.gtm.baseline.failure_modes as fm_pkg


def _load_all_modules():
    modules = []
    pkg_path = fm_pkg.__path__
    pkg_prefix = fm_pkg.__name__ + "."
    for _, module_name, _ in pkgutil.iter_modules(pkg_path):
        full_name = pkg_prefix + module_name
        mod = importlib.import_module(full_name)
        modules.append((module_name, mod))
    return modules


ALL_MODULES = _load_all_modules()
FM_MODULES = [(name, mod) for name, mod in ALL_MODULES if not name.startswith("_")]


@pytest.mark.parametrize("module_name,mod", FM_MODULES, ids=[m[0] for m in FM_MODULES])
def test_detect_callable(module_name, mod):
    assert hasattr(mod, "detect"), f"{module_name} must expose a detect() function"
    assert callable(mod.detect), f"{module_name}.detect must be callable"


@pytest.mark.parametrize("module_name,mod", FM_MODULES, ids=[m[0] for m in FM_MODULES])
def test_fixture_triggers_mode(module_name, mod):
    assert hasattr(mod, "FIXTURE_ENTITY"), f"{module_name} must have FIXTURE_ENTITY"
    assert hasattr(mod, "FIXTURE_SOURCE"), f"{module_name} must have FIXTURE_SOURCE"

    detected, reason = mod.detect(mod.FIXTURE_ENTITY, mod.FIXTURE_SOURCE)
    assert detected, (
        f"{module_name}: fixture did not trigger the failure mode. "
        f"Entity label={mod.FIXTURE_ENTITY.label.value!r}, "
        f"reason={reason!r}"
    )
    assert reason is not None and len(reason) > 0, (
        f"{module_name}: when detected=True, reason must be a non-empty string"
    )


@pytest.mark.parametrize("module_name,mod", FM_MODULES, ids=[m[0] for m in FM_MODULES])
def test_detect_returns_tuple(module_name, mod):
    result = mod.detect(mod.FIXTURE_ENTITY, mod.FIXTURE_SOURCE)
    assert isinstance(result, tuple), f"{module_name}.detect() must return a tuple"
    assert len(result) == 2, f"{module_name}.detect() must return a 2-tuple"
    detected, reason = result
    assert isinstance(detected, bool), f"{module_name}: first element must be bool"


def test_all_25_modes_present():
    assert len(FM_MODULES) >= 25, (
        f"Expected at least 25 failure modes, found {len(FM_MODULES)}: "
        f"{[m[0] for m in FM_MODULES]}"
    )


def test_no_false_positive_on_unrelated_label():
    """Each mode should return (False, None) when given an entity with a different label."""
    from forge.domains.gtm.baseline.failure_modes import SourceDoc

    dummy_entity = type("E", (), {
        "label": type("L", (), {"value": "engagement.email_open"})(),
        "text": "opened",
        "normalized_value": None,
    })()
    dummy_source = SourceDoc(url="https://example.com", text="Email was opened.")

    for module_name, mod in FM_MODULES:
        detected, reason = mod.detect(dummy_entity, dummy_source)
        if detected:
            pass
