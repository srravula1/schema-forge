# Template 05 — Failure Modes Interview
## SAP-Joule Engagement — Filled 2026-05-22

---

## Section 1 — False positives

**Describe the most common false-positive patterns — accounts that looked qualified but were not.**

> FM-SAP-01: ECC-only with no roadmap flagged as pilot-ready.
> An account running SAP ECC 6.0 with a large SAP user base (~3,000 users) was scored as high-priority because of the large SAP footprint. Reality: they had no S/4HANA plan, no BTP entitlement, and no Joule access. The SAP landscape was large but frozen in a pre-AI era configuration. Joule requires S/4HANA (or an ECC-to-S/4 migration in progress); ECC alone is not a pilot candidate.
>
> FM-SAP-02: SAP AE excitement without end-customer budget (channel mirage).
> An SAP Account Executive referred an account with high enthusiasm ("this is a perfect Joule account"). The SAP AE had seen a Joule demo with the CIO and the CIO had said "sounds interesting." We treated the referral as a qualified lead. After 45 days in discovery, the end-customer's finance team confirmed there was no IT project budget allocated for Joule that fiscal year. The AE's excitement reflected their own co-sell quota motivations, not the end-customer's buying intent.
>
> FM-SAP-03: Big4 MD relationship without a live program.
> A Managing Director at a Big4 SAP practice approached us as a potential Joule subcontractor. We invested in the relationship (partner dinners, reference calls, joint proposal prep) over 4 months. The prime contract for the SAP transformation program they were pitching was lost to a competing SI. The MD relationship is real; there is no deal.
>
> FM-SAP-04: "Joule interest" from SAP marketing copy, not prospect initiative.
> A prospect downloaded an SAP whitepaper on "Joule for Finance" from SAP's own website, which fed our intent-data provider, which flagged the account as "high intent for Joule." The account was a 200-employee company running SAP Business One (not S/4HANA, not Joule-compatible). The intent signal was from SAP's own marketing campaign reach, not genuine Joule buying intent.
>
> FM-SAP-05: RISE migration mistaken for Joule implementation intent.
> An account was reported as "migrating to RISE with SAP" and scored as a Joule pilot candidate. In reality, RISE migration is an infrastructure/commercial contract change — it is not inherently an AI or Joule project. The account's RISE migration was being run by an incumbent SI; they had no AI workstream and no Joule project plan.
>
> FM-SAP-06: "SAP VP" title inflation at a small reseller.
> A contact with title "VP of SAP Consulting" at a 12-person SAP boutique reseller was flagged as a sap_field co-sell contact. In reality, this was a senior individual contributor at a small shop with no co-sell relationship with SAP SE. The "SAP VP" title referred to their practice area, not to an SAP SE employment relationship. They could not refer us into end-customer accounts via any official SAP co-sell program.
>
> FM-SAP-07: Clean core initiative interpreted as AI readiness.
> An account was publicly discussing their "clean core SAP strategy" — removing customizations to prepare for cloud migration. This was treated as a signal that they were Joule-ready. In reality, clean core work is a prerequisite to S/4HANA migration, not a signal of AI readiness. The account was 18-24 months from being Joule-implementable.
>
> FM-SAP-08: Multiple SAP module mentions creating false breadth signal.
> An account had FI, CO, MM, SD, PP, QM, and HR all mentioned in their job postings and LinkedIn content. This was interpreted as a "rich SAP footprint" and scored highly. In reality, many of these modules were in a legacy ECC implementation that had not been upgraded in years; only FI/CO was actively maintained. The breadth of module mentions was historical documentation, not current active deployment.

---

## Section 2 — False negatives (accounts we missed)

**Describe accounts that should have been qualified earlier but were not.**

> FM-SAP-09: Clean core initiative that DID signal readiness (missed).
> An account that was implementing clean core and explicitly describing it as "the first step in our RISE with SAP migration, which we plan to complete by Q1 2027" was in our nurture sequence for 6 months before we realized they were an active S/4 migration candidate. The clean core framing obscured the S/4 migration intent.
>
> FM-SAP-10: BTP entitlement in the tech stack, not connected to Joule intent.
> Two accounts had SAP BTP listed as a tech stack item (visible from job postings for BTP developers). We did not connect BTP entitlement to Joule readiness. In both cases, the accounts had active BTP usage and were independently evaluating Joule. We missed 60-90 day windows before they signed with a competitor.

---

## Section 3 — Extraction and data failure modes

**Where does data quality cause bad scoring?**

> - SAP landscape data is often in job postings and LinkedIn content, not in standard firmographic databases. An account running S/4HANA on-prem may not have that in any CRM enrichment field — it shows up in job titles ("SAP S/4HANA Functional Consultant") and job requirements. Extraction needs to pull SAP stack from hiring content, not just from tech stack databases.
> - ECC vs. S/4 confusion is common. Some prospects say "we run SAP" without specifying version. The version distinction is critical for qualification (ECC with roadmap = medium priority; S/4HANA = high priority; ECC without roadmap = nurture). Extraction must probe for version specificity.
> - RISE vs. GROW confusion. RISE with SAP and GROW with SAP are different program tiers with different implications for Joule readiness. RISE includes more BTP entitlements; GROW is simpler. Both are high-priority signals but for different reasons.
