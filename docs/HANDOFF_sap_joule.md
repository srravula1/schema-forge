# Spine Handoff Note — sap-joule (`gtm_sapjoule@v1`)

**Engagement:** sap-joule (engagement 2)
**Schema key:** `gtm_sapjoule@v1`
**Output file:** `engagements/sap-joule/04_output/gtm_sapjoule_v1.py`

This is an engagement-specific companion to `docs/HANDOFF.md`. Read that document first
for the generic runbook structure. This note records the sap-joule-specific details:
source-doc types, custom signals, and the exact commands and diff expectation for this
engagement.

---

## Prerequisites

Same as `docs/HANDOFF.md`:

- `schema-forge generate` has run and `engagements/sap-joule/04_output/` is populated.
- `schema-forge validate --engagement engagements/sap-joule/` exits 0.
- You have a local clone of the spine repo checked out to a clean branch.

---

## Step 1 — Copy the schema module

```bash
cp engagements/sap-joule/04_output/gtm_sapjoule_v1.py \
   ../spine/spine/schema/gtm_sapjoule_v1.py
```

`gtm_sapjoule_v1.py` is self-contained. It has no imports from `forge/` or from the
spine, and it drops directly into `spine/schema/` with no modification.

---

## Step 2 — Register the schema (2-line registry edit)

Open `spine/spine/schema/registry.py` and add two lines:

```python
# line 1 — import
from spine.schema.gtm_sapjoule_v1 import (
    GtmLabel as GtmLabelSapJoule,
    GtmEntity as GtmEntitySapJoule,
    extraction_guidance as extraction_guidance_sap_joule,
)

# line 2 — register
SCHEMA_REGISTRY = {
    # ... existing entries ...
    "gtm_sapjoule@v1": {
        "label_enum": GtmLabelSapJoule,
        "entity_model": GtmEntitySapJoule,
        "extraction_guidance": extraction_guidance_sap_joule,
    },
}
```

That is the complete registry change: one import line and one dict entry.

---

## Step 3 — Run the spine's extract pipeline

Point the extraction pipeline at sap-joule source documents. The relevant document
types and what to extract from each are listed below.

```bash
cd ../spine
python -m spine.pipeline extract \
    --schema gtm_sapjoule@v1 \
    --urls path/to/sapjoule_urls.txt \
    --out out/sapjoule/
```

The schema key (`gtm_sapjoule@v1`) must match what you registered in Step 2.

---

## Source-document types for extraction

Point the extraction pipeline at the following source-document categories. These are
the document types the engagement was designed around; extraction guidance in
`gtm_sapjoule_v1.py` is calibrated to these sources.

| Document type | What to extract | Priority labels |
|---|---|---|
| SAP-field contact LinkedIn profiles (SAP SE Regional VPs, AEs, VPs of Sales) | Contact seniority, title, department; presence of SAP field role = routing signal | `C_TITLE`, `C_SENIORITY`, `C_DEPARTMENT`, `S_SAP_FIELD_CO_SELL` |
| Big4 / large IT consulting contact LinkedIn profiles (MDs, Partners running SAP transformation programs) | SI-partner contact identity; confirmation of live SAP transformation program | `C_TITLE`, `C_SENIORITY`, `S_SI_PARTNER_INVOLVED` |
| End-customer SAP landscape pages and IT/infrastructure pages | ERP stack (ECC vs S/4HANA), deployment model, RISE/GROW adoption, module footprint | `A_TECH_STACK_ITEM`, `S_RISE_ADOPTION`, `S_S4_MIGRATION_TIMELINE` |
| Pilot RFPs and procurement documents | Named use case, budget evidence, authority (CIO/CFO sponsor), timeline | `Q_NEED_ARTICULATED`, `Q_BUDGET_CONFIRMED`, `Q_AUTHORITY_IDENTIFIED`, `Q_TIMELINE_STATED` |
| SAP partner-directory listings | Confirmation that end-customer is a named SAP partner or RISE/GROW customer; listed SI-partner programs | `S_RISE_ADOPTION`, `A_TECH_STACK_ITEM`, `S_SI_PARTNER_INVOLVED` |
| End-customer press releases, executive announcements, and job postings | S/4HANA migration timeline confirmation, clean core program, Joule interest, SAP hiring signals | `S_S4_MIGRATION_TIMELINE`, `S_CLEAN_CORE_INITIATIVE`, `S_JOULE_INTEREST`, `S_HIRING_TRIGGER` |

---

## Custom signals in `gtm_sapjoule@v1`

The schema contains 6 custom signals beyond the 30-label `gtm@v1` baseline. All six
are defined in `engagements/sap-joule/03_overrides/channel_overrides.yaml` and emitted
as `custom.*` enum values in `gtm_sapjoule_v1.py`. The spine consumes them as first-class
labels — no special handling is required.

| Signal | Enum value | Description |
|---|---|---|
| `S_CLEAN_CORE_INITIATIVE` | `custom.s_clean_core_initiative` | Account implementing SAP clean core strategy (medium-priority nurture signal; combine with `S_S4_MIGRATION_TIMELINE` for higher confidence) |
| `S_JOULE_INTEREST` | `custom.s_joule_interest` | Prospect-originated evidence of Joule evaluation or planning (must be prospect-initiated, not SAP marketing attribution) |
| `S_RISE_ADOPTION` | `custom.s_rise_adoption` | Account has adopted or contracted for RISE with SAP (strong signal — Joule entitlement included in RISE license) |
| `S_S4_MIGRATION_TIMELINE` | `custom.s_s4_migration_timeline` | Confirmed, funded S/4HANA migration program with named start date or completion target within 24 months |
| `S_SAP_FIELD_CO_SELL` | `custom.s_sap_field_co_sell` | Active co-sell engagement from an SAP SE employee with a specific account referral (routing signal, NOT a qualification signal) |
| `S_SI_PARTNER_INVOLVED` | `custom.s_si_partner_involved` | Big4 or large IT consulting partner running a live SAP transformation program and engaging this firm as a Joule specialist subcontractor |

The spine consumes `gtm_sapjoule_v1.py` as a **single self-contained file**. All 36
labels (30 base + 6 custom), the `GtmEntity` model, and `extraction_guidance()` are
defined in that one file. No additional imports are needed.

---

## Expected `git diff --stat` in the spine

After Steps 1 and 2, before running extraction, the spine diff must show **only two
changed locations**:

```
 spine/schema/gtm_sapjoule_v1.py  | <N> insertions(+)   ← new file
 spine/schema/registry.py          |   2 insertions(+)   ← 2-line edit
 2 files changed, <N+2> insertions(+)
```

No other spine files should change. The spine's extraction, calibration, HIL, and eval
pipeline remain untouched. If `git diff --stat` shows additional files, stop and
investigate before proceeding.

---

## Other artifacts (optional, same pattern as generic runbook)

The remaining four artifacts in `engagements/sap-joule/04_output/` can be integrated
independently after the schema is live:

| Artifact | Destination in spine |
|---|---|
| `gtm_sapjoule_modifiers.yaml` | Attach to the extraction prompt config |
| `gtm_sapjoule_policy.py` | `spine/hil/policies/` |
| `gtm_sapjoule_gold.jsonl` | `spine/eval/` calibration corpus |
| `engagements/sap-joule/04_output/gtm_sapjoule_failure_modes/` (see `manifest.yaml` for the 8 failure modes) | `spine/eval/failure_modes/` |

---

*For the generic spine handoff runbook (prerequisites, copy semantics, registry pattern),
see `docs/HANDOFF.md`.*

*This document closes GitHub issue #59.*
