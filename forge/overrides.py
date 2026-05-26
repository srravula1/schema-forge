"""Override file schemas and loader for EPIC D.

Four override types, matching the §5 YAML examples in docs/schema_forge_plan.md:

    IcpOverrides        — narrows valid value space for account-family labels
    ChannelOverrides    — adds signal weights and custom signal definitions
    ModifierOverrides   — adds / restricts modifier-ontology entries
    PolicyOverrides     — buyer-specific qualification rules

Every override entry requires a ``rationale`` field so the audit trail in
``manifest.yaml`` can trace every change back to an interview answer.

Loader usage::

    from forge.overrides import load_overrides, check_label_refs

    bundle = load_overrides(Path("engagements/acme/03_overrides/"))
    errors = check_label_refs(bundle)

``failure_mode_additions/`` shape
----------------------------------
Each Python module in an engagement's ``03_overrides/failure_mode_additions/``
must expose:

    detect(entity, source_doc) -> tuple[bool, str | None]

where ``entity`` has at minimum a ``.label`` attribute (``GtmLabel`` value) and
``source_doc`` is any object the caller passes.  When detected is ``True``,
reason must be a non-empty string.  The modules may also expose ``FIXTURE_ENTITY``
and ``FIXTURE_SOURCE`` following the same convention as the baseline failure modes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

from forge.domains.gtm.baseline.gtm_schema import GtmLabel

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_LABEL_VALUES: frozenset[str] = frozenset(lbl.value for lbl in GtmLabel)
# Also accept enum member names (e.g. "A_EMPLOYEE_RANGE") as valid ICP override keys.
# The merge engine (forge/merge/__init__.py) resolves both forms via _LABEL_VALUE_BY_KEY.
_VALID_LABEL_KEYS: frozenset[str] = _VALID_LABEL_VALUES | frozenset(lbl.name for lbl in GtmLabel)


def _validate_label(value: str) -> str:
    """Raise ValueError if value is not a known GtmLabel."""
    if value not in _VALID_LABEL_VALUES:
        raise ValueError(
            f"{value!r} is not a valid GtmLabel. "
            f"Valid values: {sorted(_VALID_LABEL_VALUES)}"
        )
    return value


# ---------------------------------------------------------------------------
# Story D1 — Pydantic v2 models
# ---------------------------------------------------------------------------


class LabelFilter(BaseModel):
    """Include/exclude/preferred constraints for a single label's value space."""

    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    preferred: list[str] = Field(default_factory=list)
    rationale: str = Field(..., description="Why this constraint was applied (required).")


class IcpOverrides(BaseModel):
    """
    Narrows the valid value space for account-family labels.

    Keys are GtmLabel string values (e.g. ``"account.employee_range"``).
    Each entry is a :class:`LabelFilter`.
    """

    filters: dict[str, LabelFilter] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _promote_flat(cls, data: Any) -> Any:
        """Allow the top-level YAML keys to act as the filters dict."""
        if isinstance(data, dict) and "filters" not in data:
            return {"filters": data}
        return data


class CustomSignal(BaseModel):
    """A buyer-specific signal definition to add to the schema."""

    name: str = Field(..., description="Signal identifier, e.g. S_LINKEDIN_ENGAGEMENT.")
    definition: str = Field(..., description="Human-readable definition for extraction prompt.")
    rationale: str = Field(..., description="Source interview evidence that motivated this signal.")
    add_to_schema: bool = Field(default=True)


class ChannelOverrides(BaseModel):
    """
    Adds signal weights and new signal definitions.

    ``signal_weights`` maps GtmLabel string values to floats [0, 1].
    ``custom_signals`` lists new buyer-specific signal definitions.
    """

    signal_weights: dict[str, float] = Field(default_factory=dict)
    custom_signals: list[CustomSignal] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_signal_weight_labels(self) -> "ChannelOverrides":
        for label_val in self.signal_weights:
            _validate_label(label_val)
        return self


class IntentTopicOverrides(BaseModel):
    """Add / deprioritize intent topics in the modifier ontology."""

    add: list[str] = Field(default_factory=list)
    deprioritize: list[str] = Field(default_factory=list)
    rationale: str = Field(..., description="Source interview evidence.")


class ModifierOverrides(BaseModel):
    """Adds or restricts modifier-ontology entries."""

    intent_topics: IntentTopicOverrides | None = None


class DisqualificationRule(BaseModel):
    condition: str = Field(..., description="Condition expression that triggers disqualification.")
    rationale: str = Field(..., description="Source interview evidence.")


class AutoPassRule(BaseModel):
    condition: str = Field(..., description="Condition expression that triggers auto-pass.")
    rationale: str = Field(..., description="Source interview evidence.")


class HilRule(BaseModel):
    condition: str = Field(..., description="Condition expression that routes to HIL.")
    rationale: str = Field(..., description="Source interview evidence.")


class PolicyOverrides(BaseModel):
    """Buyer-specific qualification rules layered on top of the baseline policy."""

    disqualification_rules: list[DisqualificationRule] = Field(default_factory=list)
    auto_pass_rules: list[AutoPassRule] = Field(default_factory=list)
    hil_rules: list[HilRule] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Bundle — holds all four override files for one engagement
# ---------------------------------------------------------------------------


class OverrideBundle(BaseModel):
    """All overrides for one engagement, loaded from ``03_overrides/``."""

    icp: IcpOverrides = Field(default_factory=IcpOverrides)
    channel: ChannelOverrides = Field(default_factory=ChannelOverrides)
    modifier: ModifierOverrides = Field(default_factory=ModifierOverrides)
    policy: PolicyOverrides = Field(default_factory=PolicyOverrides)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

_FILE_MAP = {
    "icp_overrides.yaml": "icp",
    "channel_overrides.yaml": "channel",
    "modifier_overrides.yaml": "modifier",
    "policy_overrides.yaml": "policy",
}

_MODEL_MAP = {
    "icp": IcpOverrides,
    "channel": ChannelOverrides,
    "modifier": ModifierOverrides,
    "policy": PolicyOverrides,
}


def load_overrides(overrides_dir: Path) -> OverrideBundle:
    """Parse YAML files from ``03_overrides/`` into an :class:`OverrideBundle`.

    Missing files are silently skipped (empty defaults are used).  Malformed
    YAML or schema violations raise ``ValueError`` / ``pydantic.ValidationError``.
    """
    kwargs: dict[str, Any] = {}
    for filename, key in _FILE_MAP.items():
        path = overrides_dir / filename
        if not path.exists():
            continue
        raw = yaml.safe_load(path.read_text()) or {}
        model_cls = _MODEL_MAP[key]
        kwargs[key] = model_cls.model_validate(raw)
    return OverrideBundle(**kwargs)


# ---------------------------------------------------------------------------
# Label-reference checker
# ---------------------------------------------------------------------------


def check_label_refs(bundle: OverrideBundle) -> list[str]:
    """Return a list of error strings for any label reference that is not a real GtmLabel.

    Accepts both label values (e.g. ``"account.employee_range"``) and enum member
    names (e.g. ``"A_EMPLOYEE_RANGE"``), matching the merge engine's behaviour.

    An empty list means all references are valid.
    """
    errors: list[str] = []

    for label_key in bundle.icp.filters:
        if label_key not in _VALID_LABEL_KEYS:
            errors.append(
                f"icp_overrides: {label_key!r} is not a valid GtmLabel"
            )

    for label_val in bundle.channel.signal_weights:
        if label_val not in _VALID_LABEL_VALUES:
            errors.append(
                f"channel_overrides.signal_weights: {label_val!r} is not a valid GtmLabel"
            )

    return errors
