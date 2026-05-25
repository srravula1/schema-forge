# spine/schema/registry.py — minimal edit, mirrors how cord@v1 was added (Story C-1)
# Only the two lines marked NEW are the change.

from spine.schema.funsd import FunsdEntity as _FunsdV1
from spine.schema.funsd_v2 import FunsdEntity as _FunsdV2
from spine.schema.cord import CordEntity as _CordV1
from spine.schema.gtm import GtmEntity as _GtmV1  # NEW

_REGISTRY = {
    "funsd@v1": _FunsdV1,
    "funsd@v2": _FunsdV2,
    "cord@v1":  _CordV1,
    "gtm@v1":   _GtmV1,   # NEW
}


def load_schema(name: str):
    if name not in _REGISTRY:
        raise KeyError(f"unknown schema {name!r}; known: {sorted(_REGISTRY)}")
    return _REGISTRY[name]
