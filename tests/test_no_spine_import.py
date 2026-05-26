"""Enforce the files-only contract: forge/ must never import the spine."""

import pathlib
import re

FORGE = pathlib.Path(__file__).resolve().parent.parent / "forge"
_SPINE_IMPORT = re.compile(r"^\s*(?:import\s+spine|from\s+spine[.\s])", re.MULTILINE)


def test_forge_never_imports_spine():
    offenders = [
        str(py.relative_to(FORGE.parent))
        for py in FORGE.rglob("*.py")
        if _SPINE_IMPORT.search(py.read_text(encoding="utf-8"))
    ]
    assert not offenders, f"forge/ must not import the spine; offenders: {offenders}"
