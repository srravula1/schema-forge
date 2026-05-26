# DESIGN.md — SAP-Joule Engagement
## schema-forge v0, Stage 1 | engagement 2

---

## D1 — Unit of Analysis

The **end-customer account** (a company running SAP ECC or S/4HANA) is the unit of
analysis for all qualification scoring, disposition decisions, and pipeline metrics.

**SAP-field** contacts (Regional VPs, VPs of Sales, Account Executives employed by SAP
SE) and **SI-partner** contacts (Managing Directors and Partners at Big4 or large IT
consulting firms) are modeled as **co-sell signals and channel-affiliated contacts**, not
as separate entity families. They are captured as:
- `S_SAP_FIELD_CO_SELL` — a custom signal on the end-customer account indicating active
  SAP-field co-sell engagement (SAP AE has introduced the firm, requested joint pursuit,
  or is listed as co-sell partner in CRM).
- `S_SI_PARTNER_INVOLVED` — a custom signal indicating an SI transformation program
  pull-through (Big4 or large IT consulting partner is running an SAP transformation
  engagement that surfaces this firm's Joule/AI-impl work).
- Contact records use `normalized_value` on `C_TITLE` or `C_DEPARTMENT` to encode
  org-affiliation convention (see D3 below).

Budget authorization and contract signature always sit with the end-customer. A
SAP-field or SI-partner contact in the CRM does NOT qualify the account — only
end-customer authority evidence does.

---

## D2 — SAP Landscape as Dominant Firmographic

For this engagement, the SAP landscape replaces the standard technology firmographic
as the dominant account-level signal:

- **ERP core** (ECC 6.0 / S/4HANA on-premises / S/4HANA Cloud private edition /
  S/4HANA Cloud public edition / RISE with SAP / GROW with SAP) — captured via
  `A_TECH_STACK_ITEM` with `normalized_value` encoding the SAP variant.
- **Deployment model** (on-premises / cloud / hybrid) — encoded in `normalized_value`
  on the SAP stack item or in modifier modifiers.yaml.
- **Module footprint** (FI/CO, MM, SD, PP, QM, HR/HCM, EWM, etc.) — captured as
  additional `A_TECH_STACK_ITEM` entities.
- **SAP user-base bucket** (< 500 / 500–2000 / 2000–10000 / 10000+) — modifier-layer
  dimension (cannot be expressed as a base label bucket without a gtm@v2 label).
- **SAP IS-industry** (Retail, Manufacturing, Energy & Utilities, Financial Services,
  Public Sector, Life Sciences) — modifier-layer dimension.

The migration timeline to S/4HANA is the single highest-value signal for qualification:
an ECC customer without a funded, named S/4HANA program is a **nurture** account; one
with a board-funded migration active in 2025–2027 is the target ICP.

---

## D3 — Contact Org-Affiliation: The gtm@v1 Strain Point

`gtm@v1`'s single-account `works_at` link from `C_FULL_NAME → A_COMPANY_NAME` assumes
every contact belongs to one account family. This engagement surfaces three contact
org-affiliations:

| Affiliation | Who | Typical CRM association |
|---|---|---|
| `end_customer` | CIO, CFO, IT VP, SAP Program Director at the buying company | Account = prospect |
| `sap_field` | SAP SE Regional VP / VP Sales / AE who co-sells | Linked to prospect account via co-sell field |
| `si_partner` | Big4 MD / Partner running the transformation program | Linked to prospect account via partner opportunity |

**Convention applied in this engagement (without modifying gtm@v1):**
- `C_TITLE` `normalized_value` includes the org-affiliation tag when known:
  e.g. `normalized_value = "vp_sales|sap_field"` or `"managing_director|si_partner"`.
- The presence of `S_SAP_FIELD_CO_SELL` or `S_SI_PARTNER_INVOLVED` signals at the
  account level is the primary indicator; contact `normalized_value` is secondary
  documentation.
- The `works_at` link continues to point SAP-field and SI-partner contacts to the
  end-customer account they are associated with (not to SAP SE or the Big4 firm),
  because the end-customer is the unit of analysis.

**gtm@v2 candidate:** A proper fix would add a `C_ORG_AFFILIATION` label
(values: `end_customer`, `sap_field`, `si_partner`) and extend `valid_links()` with
`C_ORG_AFFILIATION → A_COMPANY_NAME`. This is documented as a Stage-2 finding —
see Stage-2 Findings section below.

---

## No Base gtm@v1 Edits

No files under `forge/` were modified. The `gtm@v1` baseline is frozen at 30 labels.
All SAP-specific extensions are expressed through the four override files in `03_overrides/`
and the failure mode additions in `03_overrides/failure_mode_additions/`.

---

## Stage-2 Findings (things the override mechanism cannot fully express)

These are real limitations found during this engagement — valuable engineering inputs
for the gtm@v2 design:

1. **Contact org-affiliation can't be a first-class label.** `gtm@v1` has no
   `C_ORG_AFFILIATION` label. The convention of embedding affiliation in `normalized_value`
   is workable but not queryable by the spine's F1 evaluator. Candidate: `gtm@v2` adds
   `C_ORG_AFFILIATION` with values `end_customer` / `sap_field` / `si_partner`.

2. **SAP user-base bucket has no natural home.** There is no base label that maps to
   "number of SAP licensed users." It is expressed via modifier-layer guidance but not
   as a scoreable entity. Candidate: `gtm@v2` adds `A_PLATFORM_USER_RANGE` for
   platform-scale dimensions beyond headcount.

3. **SAP module footprint produces M entities per account.** Extracting FI/CO, MM, SD,
   PP, QM, HR, EWM etc. as individual `A_TECH_STACK_ITEM` entities is correct but
   creates a wide, unordered set. The spine's eval treats each entity independently —
   there is no "module footprint profile" aggregate label. Candidate: `gtm@v2` adds
   `A_PLATFORM_PROFILE` as a structured multi-value label.

4. **Co-sell routing is binary in HIL rules.** The `S_SAP_FIELD_CO_SELL` HIL rule
   routes to "alliances owner" but cannot express priority ordering when both co-sell
   signals are present simultaneously (SAP AE + Big4 MD on the same deal). The override
   mechanism supports independent HIL rules; compound routing logic requires the spine's
   HIL orchestrator to implement priority ordering. Documented as a spine-layer concern,
   not a schema-forge concern.

5. **SAP IS-industry and RISE/GROW program tier are modifier-layer only.** These
   dimensions are expressed as `intent_topics` and extraction guidance additions, not as
   queryable labels. Any analytics that segments pipeline by SAP industry or deployment
   program tier requires a downstream enrichment step, not schema-forge output.
