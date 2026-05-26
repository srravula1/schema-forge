# sap_gold.jsonl — SAP-Joule Engagement v0 Gold Corpus

## What this is

200 synthetic-but-grounded gold records for the `gtm_sapjoule@v1` schema (37 labels:
31 base including `contact.affiliation`, + 6 custom SAP signals). This is the **v0 fit**:
calibration numbers derived from this corpus are indicative, not buyer-validated.
**The buyer-CRM pilot win/loss re-fit is the benchmark-call deliverable** and supersedes
this corpus. This file is distinct from the baseline gold carried into `04_output/`.

## Record shape

Each line is a JSON object matching the baseline shape exactly:

```json
{
  "source_doc_id": "sap_0001",
  "source_type": "linkedin_post | website_page | crm_note | call_transcript | email",
  "grounding_sources": ["<citation>", ...],
  "entities": [
    {
      "label": "<GtmLabel value>",
      "text": "<raw extracted span>",
      "normalized_value": "<canonical form or null>",
      "confidence": 0.87
    },
    ...
  ]
}
```

All `label` values validate against `GtmLabel` in `engagements/sap-joule/04_output/gtm_sapjoule_v1.py`.
All `confidence` values are in [0.0, 1.0].

## Real grounding data (cited verbatim)

### Firmographic distribution — Vibe Prospecting / Explorium

Source: Vibe Prospecting / Explorium query on large SAP-ERP install base,
**n=30,316 companies**, credit_usage=0, queried 2026-05.

Synthetic account firmographics are sampled to match these real proportions:

**Geography (top countries, raw counts):**

| Country | Count |
|---|---|
| United States | 6,762 |
| India | 1,950 |
| Germany | 1,936 |
| United Kingdom | 1,246 |
| Brazil | 990 |
| France | 978 |
| Canada | 745 |
| Australia | 694 |
| Netherlands | 626 |
| Switzerland | 572 |
| Spain | 562 |
| China | 516 |
| Mexico | 513 |
| Italy | 489 |
| (long tail beyond) | |

**Revenue (USD) distribution:**

| Revenue Bucket | Count |
|---|---|
| 1B–10B | 11,156 |
| 200M–500M | 8,933 |
| 500M–1B | 6,968 |
| 75M–200M | 1,598 |
| 10B–100B | 1,323 |
| 25M–75M | 283 |
| 100B–1T | 49 |

**Employee distribution:**

| Employee Bucket | Count |
|---|---|
| 1,001–5,000 | 16,211 |
| 10,001+ | 9,103 |
| 5,001–10,000 | 5,002 |

### Real named anchor records — Indeed job postings

Three records use real named organizations, cited with their Indeed job ID and URL:

| Job ID | Company | Title | Location | Salary | Date | URL | Role in corpus |
|---|---|---|---|---|---|---|---|
| JOB_3 | **Ferrero** | SAP S/4HANA Finance Functional Lead | Parsippany-Troy Hills, NJ | $122,854–$163,806 | 2026-03-13 | https://to.indeed.com/aakjwr4djq2h | Real end-customer S/4HANA Finance signal |
| JOB_1 | **w3global** | SAP BTP Consultant / Lead | California | $80k–$105k | 2026-05-22 | https://to.indeed.com/aat98cl8kckk | SI/staffing channel + BTP signal |
| JOB_2 | **Quintile Advisory** | Enterprise Scheduling Specialist (Kinaxis) | Remote | — | — | https://to.indeed.com/aabb6d88zpjp | Consultancy / channel |

## Synthetic-vs-real split

| Record type | Count | Notes |
|---|---|---|
| Real named anchor (Indeed-cited) | 3 | Ferrero, w3global, Quintile Advisory |
| Synthetic-but-realistic accounts | 197 | Firmographics from Vibe n=30,316 |

**All other end-customer account names are synthetic-but-realistic.** They are tagged
in `grounding_sources` as:
> "synthetic identity; firmographics sampled from Vibe SAP-ERP distribution n=30,316"

No specific claim is made that any non-cited company runs SAP. Big4/SI firm names
(Deloitte, Accenture, PwC, EY, KPMG, IBM Global Services, Capgemini) are used as
`channel_partner` org names — they are public entities and their SAP practice existence
is public knowledge.

**No real named individuals are invented.** All persona names are synthetic combinations
from cross-cultural first/last name pools.

## Channel-affiliation mix and disposition distribution

Generated with `SEED=42`, `NUM_RECORDS=200`.

**Channel affiliation (per spec: ~50% end_customer, 30% sap-field, 20% SI):**

| Affiliation | Count | % |
|---|---|---|
| `end_customer` (direct) | ~99 | ~50% |
| `channel_partner` (sap-field + SI combined) | ~101 | ~50% |

- SAP-field co-sell records are paired with `custom.s_sap_field_co_sell`.
- SI/Big4 records are paired with `custom.s_si_partner_involved`.

**Disposition spread:**

| Disposition | Count | % |
|---|---|---|
| `nurture` | 122 | 61% |
| `disqualified` | 40 | 20% |
| `qualified` | 38 | 19% |

The nurture majority reflects the SAP pipeline reality: most ECC accounts without a
funded S/4 roadmap land in nurture (FM-SAP-01), and SAP-field co-sell referrals without
end-customer budget confirmation are not auto-qualified (FM-SAP-02).

## Failure mode patterns deliberately included

The corpus includes records that trigger the SAP-specific qualification failure modes
documented in `03_overrides/failure_mode_additions/`:

| Failure Mode | Pattern in corpus |
|---|---|
| FM-SAP-01: ECC-only, no S/4 roadmap | ECC tech stack + no S4 migration timeline → `disqualified` / `nurture` |
| FM-SAP-02: Channel mirage (AE excitement) | `s_sap_field_co_sell` without `budget_confirmed` → `nurture` (not auto-qualified) |
| FM-SAP-03: Partner mirage (no live SI program) | `s_si_partner_involved` without `budget_confirmed` → `nurture` |
| FM-SAP-04: Joule interest from SAP marketing | Low-confidence `s_joule_interest` with disqualifying text → `nurture` |
| FM-SAP-07: Clean core false positive | `s_clean_core_initiative` without `need_articulated` → `nurture` |

## SAP landscape coverage

Every account has at least one `account.tech_stack_item` from the SAP landscape.
Coverage includes:

- **ERP core variants**: SAP ECC 6.0, SAP S/4HANA, SAP S/4HANA Cloud, RISE with SAP
- **Module items**: SAP FI, SAP CO, SAP MM, SAP SD, SAP PP, SAP QM, SAP PM,
  SAP EWM, SAP HR, SAP IS-U, SAP BTP, SAP SuccessFactors
- **Deployment programs**: RISE with SAP, GROW with SAP

## Generation

Records were generated by `_gen_sap_gold.py` with `SEED=42`. The committed `.jsonl`
is the deterministic output. Re-running the script with the same seed produces
byte-identical output. This is verified by `tests/test_sap_gold.py::test_generator_is_deterministic`.

## Limitations

- **No operator validation.** No human reviewed these records against real deal data.
  Labels reflect the generator's logic, not operator judgment.
- **Confidence scores are synthetic.** Drawn from uniform distributions within ranges,
  not from a calibrated model.
- **SAP landscape is illustrative.** While grounded in the Vibe distribution, specific
  module assignments to synthetic accounts are probabilistic, not researched.

## v1 upgrade path (benchmark-call deliverable)

This corpus is explicitly the **v0 fit**. The upgrade path:

1. Buyer exports 50–100 CRM records (qualified / nurture / disqualified labeled) from
   their actual SAP-Joule pipeline
2. Schema-forge maps fields to `GtmEntity` shape under `gtm_sapjoule_v1.py`
3. The re-fit corpus replaces or augments this file in `gold/`
4. Calibration is re-run on the buyer corpus; ECE and F1 numbers are reported
5. The signal weight table in `gtm_sapjoule_v1.py::SIGNAL_WEIGHTS` is updated to
   reflect empirical win/loss data
