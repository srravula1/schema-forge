# INTERFACE — the files-only contract with the spine

schema-forge produces files; the spine consumes them. There are **no shared
imports, no shared database, and no shared package**. The interface is this set
of file formats. Either repo can evolve independently as long as these hold.

## The five output artifacts

`generate` writes these into an engagement's `04_output/` directory. Each maps
to a destination inside the spine repo (handoff is manual — see `docs/HANDOFF.md`).

| # | Artifact | Output file | Lands in (spine) | Format |
|---|----------|-------------|------------------|--------|
| 1 | Schema | `<domain>_<client>_v1.py` | `spine/schema/` | Python module: Pydantic v2 entity model + `extraction_guidance()` + `valid_links()` |
| 2 | Modifier ontology | `<domain>_<client>_modifiers.yaml` | extraction prompt + eval normalization | YAML, grouped by entity family, each group carries a `source:` citation |
| 3 | Policy library | `<domain>_<client>_policy.py` | `spine/hil/policies/` | Python module mapping evidence labels → disposition |
| 4 | Failure-mode library | `<domain>_<client>_failure_modes/` | `spine/eval/failure_modes/` | Directory of Python modules, each exposing `detect(entity, source_doc) -> tuple[bool, str | None]` + a fixture |
| 5 | Ground-truth corpus | `<domain>_<client>_gold.jsonl` | calibration fit + `spine/eval/` | JSONL, one record per line, each validating against artifact #1 |

### Schema module contract (artifact #1)
A schema module must expose:
- a Pydantic v2 entity model with `label`, `text`, optional `normalized_value`, and a bounded `confidence` field (`extra="forbid"`);
- `extraction_guidance() -> dict[str, str]` covering **every** label;
- `valid_links() -> list[...]` whose endpoints are all real labels.

This mirrors the spine's existing FUNSD/CORD entity shape, so `pipeline.py`,
`calibration/`, `provenance/`, `hil/`, and `eval/f1.py` do not change.

## `manifest.yaml`
Written next to `04_output/` on every `generate`. It is the audit trail — every
change traces back to an interview answer.

```yaml
generated_at: <ISO-8601 UTC>
baseline_version: <e.g. gtm_v1.0>
overrides:
  icp_overrides.yaml: sha256:<hex>
  channel_overrides.yaml: sha256:<hex>
  # ... one entry per override file consumed
output:
  schema: <domain>_<client>_v1.py
  changes_from_baseline:
    - "<human-readable change> (<override file> L<line>)"
    # one line per applied change, each carrying the override's rationale
```

## Non-goals of the interface
- No Python import across the repo boundary in either direction.
- No shared DB or message bus.
- No automated cross-repo push — the handoff is a deliberate, human-supervised copy.
