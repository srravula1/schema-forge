# Template 04 — Qualification Interview
## SAP-Joule Engagement — Filled 2026-05-22

---

## Section 1 — Evidence gates and disqualification

**What evidence must be present before you create an active opportunity in your CRM?**

> Three gates must pass before we create an active opportunity:
> 1. SAP Platform gate: prospect must be running SAP S/4HANA, or running ECC with a funded and named S/4HANA migration program (not just "planning to migrate someday"). Non-SAP ERP is a hard DQ.
> 2. Budget gate: direct confirmation from the end-customer CIO or CFO that a pilot budget of >= $150k is allocated or in active procurement. SAP AE assertion of budget is not sufficient — we require end-customer voice.
> 3. Use-case gate: at least one named, specific Joule or BTP AI use case articulated by the end-customer (not suggested by us and accepted passively). "AI in FI/CO period-close" is a named use case. "We want to explore AI" is not.

**What evidence triggers immediate disqualification?**

> - Running non-SAP ERP: hard DQ, no exceptions.
> - ECC 6.0 with no funded S/4 roadmap and no stated migration plan: nurture; do not activate in pipeline.
> - Budget stated below $150k pilot floor: DQ; below our economics floor.
> - No named AI use case after two discovery conversations: tire-kicker; move to 6-month nurture.
> - SAP AE is the only contact engaged (no direct end-customer contact): channel mirage risk; hold in co-sell staging until end-customer is directly engaged.

**What evidence triggers automatic qualification (auto-pass)?**

> - Executive sponsor confirmed (CIO or CFO has met with us directly and expressed intent to proceed).
> - Viable S/4HANA landscape: either running S/4HANA (any variant), or a funded ECC-to-S/4 migration program with a named project start within 12 months.
> - Named Joule use case articulated by the end-customer.
> - Budget $150k–$500k confirmed or in active procurement.
> When all four are present, route to AE for proposal scoping immediately.

---

## Section 2 — MEDDIC evidence requirements

**Budget (Q_BUDGET_CONFIRMED): what counts as evidence?**

> Direct statement from CIO or CFO: "We have $X allocated for a Joule pilot this fiscal year" or "We have a PO/project code for AI in SAP." Budget confirmed by the SAP AE on behalf of the end-customer does NOT count. Big4 prime contract scope that includes our SOW counts.

**Authority (Q_AUTHORITY_IDENTIFIED): what counts as evidence?**

> We have had a direct meeting or call with the end-customer's CIO, CFO, or VP IT — the person with P&L authority for a $150k+ commitment. Confirmation that they are aware of and supportive of the pilot is required. An email from a director saying "the CIO is interested" does not count as authority identification.

**Need (Q_NEED_ARTICULATED): what counts as evidence?**

> A specific problem statement articulated by the end-customer in their own words: e.g., "Our FI period-close takes 8 days and 3 FTEs; we need to get it to 4 days" or "Our purchase-order matching error rate is 12% and it costs us $X per year." A use case suggested by us and acknowledged by the prospect is NOT sufficient — it must come from the prospect.

**Timeline (Q_TIMELINE_STATED): what counts as evidence?**

> A specific start or completion date tied to a business event: "We want to go live before our fiscal year Q4 close," "The S/4 migration project starts in September; we need Joule configured before then," or "The board has asked for an AI demo at the Q2 business review." "Someday" or "when we have the budget" is not a timeline.

---

## Section 3 — Routing rules

**How should different inbound types be routed to the right team member?**

> SAP-field co-sell leads (S_SAP_FIELD_CO_SELL signal present): route to Alliances Owner for co-sell protocol management before AE engagement. Alliances Owner verifies end-customer budget with the AE and confirms direct end-customer meeting before activating.
> SI-partner pull-through leads (S_SI_PARTNER_INVOLVED signal present): route to SI-Partner Lead. SI-Partner Lead confirms prime contract status and SOW slot before activating.
> Direct inbound (no co-sell or SI signal): route to AE for standard discovery.
>
> Critical guard: SAP-field co-sell WITHOUT end-customer budget confirmation is NOT qualified, even if the SAP AE is enthusiastic. Do not route to AE until end-customer budget is confirmed. Route to Alliances Owner instead.

---

## Section 4 — Failure modes in qualification

**What are the qualification failure modes that have cost you the most time/money?**

> 1. SAP AE excitement treated as budget confirmation. Spent 60 days on L1 (energy company) because the SAP AE said "they have budget." They did not. Rule: we now require a direct end-customer statement on budget, not AE assertion.
> 2. Big4 relationship without a live prime contract. Invested in two SI partner relationships for months before realizing the prime contracts were not won. Rule: no delivery capacity investment until prime contract is signed.
> 3. "Joule interest" from SAP's own marketing campaign reach, not the prospect's own initiative. A prospect who downloaded an SAP whitepaper on Joule and got into our nurture is not the same as a prospect who called us because their CIO asked them to evaluate Joule. The source of intent matters.
> 4. RISE migration interpreted as Joule intent. A company migrating to RISE with SAP is an SAP implementation project; it does NOT automatically mean they are buying a Joule implementation. RISE migration is a necessary but not sufficient condition.
> 5. "SAP VP" title at a small SAP reseller or boutique SI. We have had contacts with "VP of SAP Consulting" at 10-person reseller shops who cannot make a buying decision for themselves, let alone introduce us to their end customers. Title inflation in the SAP ecosystem is significant.
