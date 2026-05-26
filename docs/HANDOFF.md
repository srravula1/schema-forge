# Spine Handoff Runbook

This document describes how to hand off the five generated artifacts from a
schema-forge engagement into the spine repo so extraction can run.

**The handoff is deliberately manual and human-supervised.** Automating it
across repo boundaries is a Stage 5+ feature. At this stage, a human reviews
the generated schema before it enters the spine.

---

## Prerequisites

- `schema-forge generate` has run successfully and `04_output/` is populated.
- `schema-forge validate` exits 0 (all four checks pass).
- You have a local clone of the spine repo checked out to a clean branch.

---

## Step 1 — Copy the schema module

```bash
cp engagements/<client>/04_output/gtm_<client>_v1.py \
   ../spine/spine/schema/gtm_<client>_v1.py
```

Example for `ai-consulting-firm`:

```bash
cp engagements/ai-consulting-firm/04_output/gtm_aiconsultingfirm_v1.py \
   ../spine/spine/schema/gtm_aiconsultingfirm_v1.py
```

The generated module is self-contained: it has no imports from `forge` or
`spine`, and it drops directly into `spine/schema/` with no modification.

---

## Step 2 — Register the schema (2-line registry edit)

Open `spine/spine/schema/registry.py` and add two lines:

```python
# Before (example — your registry may differ slightly):
from spine.schema.gtm_schema import GtmLabel, GtmEntity, extraction_guidance

SCHEMA_REGISTRY = {
    "gtm@v1": {
        "label_enum": GtmLabel,
        "entity_model": GtmEntity,
        "extraction_guidance": extraction_guidance,
    },
    # ... other schemas ...
}

# After — add the client-specific schema entry:
from spine.schema.gtm_aiconsultingfirm_v1 import (   # line 1: import
    GtmLabel as GtmLabelAiConsulting,
    GtmEntity as GtmEntityAiConsulting,
    extraction_guidance as extraction_guidance_ai_consulting,
)

SCHEMA_REGISTRY = {
    "gtm@v1": { ... },
    "gtm_aiconsultingfirm@v1": {                       # line 2: register
        "label_enum": GtmLabelAiConsulting,
        "entity_model": GtmEntityAiConsulting,
        "extraction_guidance": extraction_guidance_ai_consulting,
    },
}
```

That is the complete registry change: one import line and one dict entry.

---

## Step 3 — Run the spine's extract pipeline against the client URLs

```bash
cd ../spine
python -m spine.pipeline extract \
    --schema gtm_aiconsultingfirm@v1 \
    --urls path/to/client_urls.txt \
    --out out/aiconsulting/
```

Adjust the command to match the spine's actual CLI surface. The schema key
(`gtm_aiconsultingfirm@v1`) must match what you registered in Step 2.

---

## Expected `git diff --stat` in the spine

After Steps 1 and 2, and before running extraction, the spine diff should show
**only two changed locations**:

```
 spine/schema/gtm_aiconsultingfirm_v1.py  | <N> insertions(+)   ← new file
 spine/schema/registry.py                  |   2 insertions(+)   ← 2-line edit
 2 files changed, <N+2> insertions(+)
```

No other spine files should change. If `git diff --stat` shows additional
files touched, stop and investigate before proceeding. The spine's existing
extraction, calibration, HIL, and eval pipeline remain untouched.

---

## Other artifacts (optional)

The remaining four artifacts in `04_output/` can be integrated independently:

| Artifact | Destination in spine |
|----------|----------------------|
| `gtm_<client>_modifiers.yaml` | Attach to the extraction prompt config |
| `gtm_<client>_policy.py` | `spine/hil/policies/` |
| `gtm_<client>_failure_modes/` | `spine/eval/failure_modes/` |
| `gtm_<client>_gold.jsonl` | `spine/eval/` calibration corpus |

These integrations follow the same pattern — copy the file, register it in the
relevant registry or config — and are similarly human-supervised.
