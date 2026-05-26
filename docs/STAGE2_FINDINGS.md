# Stage-2 Generalization Findings

**Status:** Formal harvest after engagement 2 (sap-joule). Feeds tracking issue #29.
**Decision date:** 2026-05-26
**Engagements compared:** `ai-consulting-firm` (engagement 1) · `sap-joule` (engagement 2)

---

## 1. Side-by-side comparison

| Dimension | ai-consulting-firm | sap-joule |
|---|---|---|
| **ICP overrides** | `A_EMPLOYEE_RANGE` 11–200; `A_FUNDING_STAGE` exclude pre_seed/seed; `A_INDUSTRY` preferred technical-services verticals | `A_EMPLOYEE_RANGE` 1001+; `A_FUNDING_STAGE` preferred public/acquired; `A_INDUSTRY` preferred SAP IS-industry verticals; `A_REVENUE_RANGE` 250M+; `C_DEPARTMENT` engineering/finance/ops; `C_SENIORITY` c_suite/vp/director |
| **Channel overrides** | 1 custom signal (`S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT`); signal weights tuned for founder-led LinkedIn inbound | 6 custom signals (`S_CLEAN_CORE_INITIATIVE`, `S_JOULE_INTEREST`, `S_RISE_ADOPTION`, `S_S4_MIGRATION_TIMELINE`, `S_SAP_FIELD_CO_SELL`, `S_SI_PARTNER_INVOLVED`); signal weights tuned for three-channel co-sell motion (SAP field + Big4 SI + direct) |
| **Modifier overrides** | 15 intent topics added; 6 deprioritized | 22 intent topics added; 7 deprioritized |
| **Policy overrides** | 3 disqualify rules; 1 auto_pass rule; 3 HIL rules | 3 disqualify rules; 2 auto_pass rules; 5 HIL rules |
| **Failure mode additions** | 1 engagement-specific failure mode (`fake_yes_ai_curiosity`) | 8 engagement-specific failure modes (ecc_only_no_roadmap, channel_mirage, partner_mirage, joule_interest_from_marketing, rise_migration_as_joule_intent, vp_title_inflation_reseller, clean_core_false_positive, stale_sap_module_breadth) |
| **`gtm@v1` source modified?** | No | No |
| **`forge/` source modified?** | No | No |

### What was duplicated (reusable pattern, used by both engagements)

1. **Modifier scaffolding** — both engagements followed the same four-file override structure (`icp_overrides.yaml`, `channel_overrides.yaml`, `modifier_overrides.yaml`, `policy_overrides.yaml`) with no deviations. The scaffolding is proven.

2. **Custom-signal → derived-schema pattern** — both engagements needed engagement-specific signals that could not be expressed as weights on base labels. The pattern (define signal in `channel_overrides.yaml` with `add_to_schema: true`; emit as `custom.*` enum value in the output `.py`) was used independently by both with no modifications to the pattern itself.

3. **Per-segment policy rules** — both engagements produced disqualify/auto_pass/HIL rules that follow the same predicate structure (`label condition AND label condition → routing outcome`). Neither engagement required changes to the policy rule syntax; both expressed materially different business logic within the same structure.

4. **Contact org-affiliation need** — both engagements encountered contacts that belong to a different org than the end-customer account:
   - `ai-consulting-firm`: LinkedIn-channel contacts (followers, commenters) who are not the prospect but interact via the founder's content. The `S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT` signal implicitly encodes "this contact has a relationship to our content, not directly to their own company's buying process."
   - `sap-joule`: Three explicit contact affiliations — `end_customer`, `sap_field`, `si_partner` — with the current `works_at` link pointing all three at the end-customer account (the unit of analysis). Encoded by convention in `C_TITLE` `normalized_value`.

   In both cases, `gtm@v1`'s single-account `works_at` link from contact to account did not express the contact's org-affiliation relationship. The DESIGN.md for `sap-joule` formally documented this as a `gtm@v2` candidate. **This is the one point where two engagements independently needed the same structural fix.**

### What strained the model

- **`sap-joule`:** The `works_at` link convention (all channel contacts point to the end-customer) caused `C_SENIORITY` and `C_DEPARTMENT` overrides to carry a dual burden: they had to encode buying-contact guidance AND distinguish SAP-field / SI-partner contacts by convention in `normalized_value`. The spine's F1 evaluator cannot query on `normalized_value` subfields — it evaluates labels, not conventions embedded in values.

- **`sap-joule`:** The SAP user-base bucket (licensed SAP user count by size tier) has no base label and could not be expressed as a scoreable entity; it lived as modifier-layer extraction guidance only.

- **`sap-joule`:** The SAP module footprint (FI/CO, MM, SD, PP, QM, HR, EWM, etc.) produces M `A_TECH_STACK_ITEM` entities per account with no aggregate profile label. The spine evaluates each entity independently.

- **`sap-joule`:** When both `S_SAP_FIELD_CO_SELL` and `S_SI_PARTNER_INVOLVED` fire simultaneously, the two independent HIL rules have no priority ordering. Compound routing logic is a spine-layer concern that overrides cannot express.

- **`ai-consulting-firm`:** No structural strain. The single-channel model (founder LinkedIn) fit cleanly within the existing contact-family labels. The engagement-specific strain was signal-weight tuning, not schema structure.

---

## 2. Generalization decision: `gtm@v2`

### What `gtm@v2` adds

**One new generic label:**

```
C_AFFILIATION = "contact.affiliation"
```

Coarse buckets: `end_customer` / `channel_partner` / `vendor` / `internal` / `unknown`

**Rationale:** Both engagements needed to express which org a contact belongs to relative to the deal:
- `ai-consulting-firm`: LinkedIn channel contacts are not the prospect's internal buyers; the label would have allowed the spine to distinguish inbound-channel contacts from direct-prospect contacts.
- `sap-joule`: Three explicit contact orgs (end-customer buyers, SAP-field co-sell reps, Big4/SI transformation partners) could not be expressed as first-class queryable labels.

The `end_customer` / `channel_partner` / `vendor` / `internal` / `unknown` buckets are coarse enough to generalize across both cases. Engagement-specific granularity (`sap_field` vs. `si_partner` distinction within `channel_partner`) stays in overrides via `normalized_value` or a future engagement-specific sub-label — not in the generic label definition.

**What `gtm@v2` does NOT add** (all four items below are deferred with one-engagement evidence only):

| Deferred item | Source | Reason for deferral |
|---|---|---|
| `A_PLATFORM_USER_RANGE` | sap-joule only | N=1. Only one engagement needed licensed-user-count bucketing. Adding a generic label for platform scale after one SAP-specific engagement is premature; a non-SAP engagement using platform user count would validate the pattern. |
| `A_PLATFORM_PROFILE` (module footprint aggregate) | sap-joule only | N=1. The multi-entity module footprint problem is specific to ERP landscapes with M modules. A second engagement with a similarly structured platform (e.g., Salesforce org with many installed packages) would validate whether this is a general pattern. |
| Compound HIL routing priority | sap-joule only | N=1, and it is a spine-layer concern, not a schema-forge concern. The HIL orchestrator, not the schema, must implement priority ordering when multiple routing rules fire. This is tracked as a spine concern, not a `gtm@v2` item. |
| `A_IS_INDUSTRY` / program-tier labels (RISE/GROW) | sap-joule only | N=1. SAP IS-industry and RISE/GROW program tiers are SAP-specific taxonomy. A second enterprise-ERP engagement (Oracle Fusion, Workday) might surface a parallel need for platform-program-tier labeling, but that has not occurred. |

---

## 3. No speculative generalization

**We are NOT building `forge_core/` yet.**

Per `docs/schema_forge_plan.md` §2 (Stage 4): the reusable framework (`forge_core/`) is extracted after engagement 3–4, when three engagements of pattern data exist. At N=2, the patterns are not yet stable enough to factor out safely. Building `forge_core/` now would be building a framework for patterns we've seen twice — exactly the class of over-engineering the roadmap was designed to prevent.

**We are NOT adding single-engagement labels to the generic baseline.** The four deferred items above are deferred specifically because they were flagged by exactly one engagement. The N=1 discipline is the primary guard against speculative generalization.

---

## 4. What a third engagement would need to promote a deferred item

**To promote `A_PLATFORM_USER_RANGE`:** A third engagement that needs to score prospects on licensed-user count for a non-SAP platform (e.g., Salesforce org size, Workday seat count, Snowflake credit consumption tier). If two different platform-implementation firms need a "users on the platform" bucket, the label generalizes.

**To promote `A_PLATFORM_PROFILE`:** A third engagement where the account's footprint on a platform is expressed as M installed modules/packages/apps that the spine needs to evaluate as a profile rather than as independent entities. A Salesforce implementation firm with ISV/AppExchange product mix would be a clear example.

**To promote compound HIL routing:** A third engagement that independently defines two co-present routing signals that require priority ordering. If a second engagement hits this, it becomes a spine API requirement (a `priority` field on HIL rules), not a schema change.

**To promote IS-industry / program-tier labels:** A second enterprise-ERP engagement (Oracle, SAP on a different product line, Workday) that needs platform-program-tier as a queryable label. The pattern needs to appear outside the SAP taxonomy before it generalizes.

---

*This document closes GitHub issue #58. See issue #29 for the ongoing Stage-2 tracking thread.*
