# Story — Private-credit `bdc_soi` domain (Schedule-of-Investments → position marks)

> Status: **proposed** (story only; not built). Stage-3 candidate (first non-GTM domain).
> Trigger engagement: **CalPERS / ARCC × OBDC mark-divergence run, 2026-06-01.**

## Why now

The CalPERS run (`PrivateCredit/TASK_CalPERS_MarkDivergence_Run.md`, outputs in
`PrivateCredit/outputs/`) found a real, defensible cross-manager mark divergence — PetVet Care
Centers' first-lien term loan marked **86.01 (Ares) vs 90.00 (Blue Owl)** as of the same quarter —
by parsing two BDC 10-Q Schedules of Investments **by hand** (a throwaway lxml/regex script), then
feeding clean `position_mark` rows to the platform's deterministic `mark_consistency` engine.

That hand-run *was* the Stage-0 sanity check the plan (`schema_forge_plan.md` §Roadmap) prescribes:
"hand-write the artifacts in a scratch directory… you'll feel where the actual pain is." The pain is
now known and catalogued (see Failure modes below), and the run produced **verified gold**. That is
the evidence threshold for promoting a domain from speculation to build.

## The boundary (read this first)

This story builds **artifacts**, not an ingester. Per schema-forge's hard scope cut — *"Does not
generate the ingest adapter… Does not run extraction or eval"* — the runtime that pulls EDGAR,
parses the SoI table, segments periods, and emits `position_mark` rows lives in the **spine/platform**
(companion story below). schema-forge generates the **schema + guidance + modifier ontology +
failure-mode library + HIL policy + gold corpus** that the spine's ingester *consumes* via the
files-only interface (`INTERFACE.md`). The CalPERS run proved the engine works; what's missing is the
**repeatable, audited contract** for reading any BDC's SoI — that contract is the schema-forge half.

```
  schema-forge (this story)                         spine / platform (companion story)
  ─────────────────────────                         ──────────────────────────────────
  bdc_soi domain →  position_mark schema            SoI ingester (table-aware EDGAR pull,
                    extraction guidance        ──▶   period-segment, FX-exclude, tranche-
                    modifier ontology (per BDC)      select, entity-resolve) → position_mark
                    failure-mode library       ──▶   runs the failure-mode detectors as gates
                    HIL policy                 ──▶   routes divergences to a human
                    gold corpus (CalPERS)      ──▶   eval / calibration
```

## What gets built — the `bdc_soi` domain (the five artifacts)

`schema-forge init --domain bdc_soi --client <fund>` scaffolds an engagement; baseline + per-fund
overrides → `generate` (deterministic, no LLM) → the five outputs. Per-fund overrides exist because
**every BDC formats its SoI differently** — the modifier layer is where that heterogeneity lives,
not the schema.

### 1. Schema — `position_mark`
The domain entity is one **loan-level SoI row**: `holder, borrower, instrument_id, seniority,
maturity, par, fair_value_mark, coupon_spread, pik_flag, non_accrual_flag, as_of_date, provenance`.
This already exists as `position_mark@v1` in the platform; schema-forge adopts it as the baseline and
the generated schema must stay validation-compatible with it (see Open decision D1 — this is the one
place the "flat entity / nested-row" shape question bites).

### 2. Extraction guidance
How to read an SoI row into the schema: which columns are par/principal vs amortized cost vs fair
value; that the comparable **mark is `fair_value / par × 100`**, computed **per tranche**; copy
issuer names and section/footnote markers verbatim; never infer a mark for a row without a funded par.

### 3. Modifier ontology (per-BDC, the heterogeneity layer)
Citation-backed, one group per convention, e.g.:
- **Units**: ARCC reports `Principal`/`Fair Value` in **$millions**; OBDC reports `Par`/`Fair Value`
  in **$thousands**. (The mark is unit-free; face/NAV is not — the ingester must normalize.)
- **Currency**: USD tranches reference `SOFR`/`S+`; **FX** tranches reference `E+`/`Euribor`/`SONIA`/
  `SA+` and carry par in `€`/`£` while cost/FV are USD — these must be excluded from FV/par.
- **Tranche taxonomy**: `first lien senior secured loan` (term, comparable) vs `revolving` /
  `delayed draw` (often unfunded) vs `preferred/common/warrant/units` (no par-based mark).
- **Entity aliases**: `AI Titan Parent, Inc.` ≡ `AI Titan Parent, Inc. (dba Prometheus Group)`;
  footnote markers `(3)(4)(9)` and `(dba …)` are stripped for resolution.

### 4. Failure-mode library — the star artifact (codifies the CalPERS bugs)
Each is a `detect(entity, source_doc) -> (bool, reason)` module + fixture, exactly the bugs the
hand-run hit and that **must never silently recur**:
- `fm_fx_par_inflates_mark` — FV(USD)/par(EUR) faked marks of 104.99 (Bamboo) and 102.36 (Flexera).
- `fm_cross_period_blend` — each 10-Q embeds the current **and** prior-year SoI; blending them
  corrupts par. (Detector: a borrower's par changing within one parse → period leak.)
- `fm_unfunded_revolver_as_funded` — revolver/DDTL rows with `—` funded par must not yield a mark.
- `fm_column_misattribution` — sanity bounds: a first-lien senior secured term-loan mark outside
  ~[60,103] is almost always a column/row attribution error, not a real mark.
- `fm_entity_overmerge` — distinct issuers collapsing to one normalized key (e.g. `Bamboo Purchaser`
  vs `Bamboo US BidCo`).

```python
# failure_modes/fm_fx_par_inflates_mark.py  (sketch, schema-forge format)
"""Mark computed from a foreign-currency par against a USD fair value — inflates the mark above par.
Source: CalPERS ARCC×OBDC run, 2026-06-01 (OBDC Bamboo EUR term loan, €4,650 par vs $5,358 FV → 115)."""
def detect(entity, source_doc) -> tuple[bool, str | None]:
    row = source_doc.text
    if any(t in row for t in ("€", "£", "E+", "Euribor", "SONIA", "SA+")) and entity.fair_value_mark > 100.5:
        return True, "FX tranche: par is non-USD but fair value is USD — FV/par is not a valid mark"
    return False, None
```

### 5. HIL policy + gold corpus
- **Policy**: when a resolved divergence routes to a human — spread ≥ threshold, either side on
  non-accrual, or a stressed mark (<90). (Mirrors the platform's always-route-in-new-vertical stance.)
- **Gold**: the CalPERS verified marks as labeled JSONL — PetVet `86.01/90.00`, GI Ranger
  `94.95/97.00`, Cambrex `100.00` — each tracing to CIK + accession + SoI as-of date. This is the
  eval set that proves a future ingester reproduces the hand-verified numbers.

## Companion story (spine, NOT this repo) — the SoI ingester
Separate platform story: a table-aware `position_mark` ingester (extends `fetch_filing_tables`) that
(a) pulls a BDC 10-Q, (b) segments to the current period, (c) excludes FX/unfunded rows, (d) selects
the comparable tranche, (e) entity-resolves, (f) emits `position_mark` rows — and **runs the
failure-mode detectors as hard gates + checks against the gold corpus** before the marks reach
`mark_consistency`. Optionally LLM-reads ambiguous rows with a human-confirm step (the existing
upload→confirm pattern). This is the piece that lets a non-Claude user reproduce the CalPERS outcome
from filings.

## Acceptance criteria (this story)
- `schema-forge generate --domain bdc_soi` emits all five artifacts; `validate` passes (guidance
  covers the schema; gold validates; every failure-mode module compiles + its fixture triggers).
- The failure-mode library catches every CalPERS bug on its fixture (FX, cross-period, unfunded,
  misattribution, over-merge).
- The gold corpus reproduces the hand-verified marks (PetVet/GI Ranger/Cambrex) and each row cites
  CIK + accession + as-of date.
- `manifest.yaml` traces every per-fund modifier to its source (filing or operator note).
- No spine import; files-only handoff (`test_no_spine_import` stays green).

## Scope cuts (what this story does NOT do)
- **No ingester / no EDGAR pull / no extraction run** — spine's job (companion story).
- **No new generate-time LLM** — `generate` stays deterministic; any LLM is in `extract-overrides`
  (operator-reviewed) only.
- **Not all BDCs** — baseline + ARCC/OBDC overrides only; more funds are added as engagements need
  them, not speculatively.
- **Not the `forge_core/` refactor** — `bdc_soi` is a copied/adapted domain module (Stage 3); core
  extraction waits for ≥3 domains (Stage 4).

## Open decisions
- **D1 — schema shape.** Adopt the platform's structured `position_mark@v1` as the domain entity
  (recommended; it's a flat typed row, close enough to schema-forge's entity model), vs. generate
  only the 4 supporting artifacts and leave the schema platform-authored. D1 is the one spot where
  schema-forge's "flat label/text entity" canonical shape meets a structured row.
- **D2 — domain name.** `bdc_soi` (document-type-scoped, precise) vs `private_credit` (vertical-scoped,
  room for credit-agreement/compliance-certificate doc types later). Recommend `bdc_soi` now; let a
  `private_credit` umbrella emerge if a 2nd doc type lands.
