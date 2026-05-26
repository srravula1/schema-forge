"""
gtm_sapjoule@v1 — client-specific GTM schema derived from gtm@v1 baseline.

This module is self-contained. No spine or schema-forge imports are needed.
Drop this file into spine/schema/ to integrate.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GtmLabel(str, Enum):
    """GTM label union. Base labels + client-specific custom signals."""

    # --- Account family ---
    A_COMPANY_NAME = "account.company_name"
    A_DOMAIN = "account.domain"
    A_INDUSTRY = "account.industry"
    A_EMPLOYEE_RANGE = "account.employee_range"
    A_REVENUE_RANGE = "account.revenue_range"
    A_HQ_LOCATION = "account.hq_location"
    A_TECH_STACK_ITEM = "account.tech_stack_item"
    A_FUNDING_STAGE = "account.funding_stage"

    # --- Contact family ---
    C_FULL_NAME = "contact.full_name"
    C_TITLE = "contact.title"
    C_SENIORITY = "contact.seniority"
    C_DEPARTMENT = "contact.department"
    C_EMAIL = "contact.email"
    C_LINKEDIN_URL = "contact.linkedin_url"

    # --- Signal family ---
    S_HIRING_TRIGGER = "signal.hiring_trigger"
    S_FUNDING_TRIGGER = "signal.funding_trigger"
    S_TECH_ADOPTION = "signal.tech_adoption"
    S_PAIN_POINT_MENTION = "signal.pain_point_mention"
    S_COMPETITOR_MENTION = "signal.competitor_mention"
    S_INTENT_TOPIC = "signal.intent_topic"

    # --- Engagement family ---
    E_EMAIL_OPEN = "engagement.email_open"
    E_EMAIL_REPLY = "engagement.email_reply"
    E_MEETING_BOOKED = "engagement.meeting_booked"
    E_CALL_TRANSCRIPT_REF = "engagement.call_transcript_ref"
    E_FORM_SUBMIT = "engagement.form_submit"

    # --- Qualification family ---
    Q_BUDGET_CONFIRMED = "qualification.budget_confirmed"
    Q_AUTHORITY_IDENTIFIED = "qualification.authority_identified"
    Q_NEED_ARTICULATED = "qualification.need_articulated"
    Q_TIMELINE_STATED = "qualification.timeline_stated"
    Q_DISPOSITION = "qualification.disposition"

    # --- Custom signals (from channel_overrides) ---
    S_CLEAN_CORE_INITIATIVE = 'custom.s_clean_core_initiative'
    S_JOULE_INTEREST = 'custom.s_joule_interest'
    S_RISE_ADOPTION = 'custom.s_rise_adoption'
    S_S4_MIGRATION_TIMELINE = 'custom.s_s4_migration_timeline'
    S_SAP_FIELD_CO_SELL = 'custom.s_sap_field_co_sell'
    S_SI_PARTNER_INVOLVED = 'custom.s_si_partner_involved'


class GtmEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: GtmLabel
    text: str = Field(..., description="The raw extracted span from the source.")
    normalized_value: Optional[str] = Field(default=None)
    confidence: float = Field(..., ge=0.0, le=1.0)


class GtmEntityLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_label: GtmLabel
    to_label: GtmLabel
    relation: str


def extraction_guidance() -> dict[str, str]:
    """Return {label_value: human_definition} for every label including custom signals."""
    _guidance: dict[str, str] = {
        "account.company_name": "The legal or commonly-used name of a company being discussed.",
        "account.domain": "The primary web domain of a company (e.g. \'acme.com\').",
        "account.industry": "The industry the company operates in. Use the most specific form stated.",
        "account.employee_range": (
            "Employee count as a bucket. Use one of: \'1-10\', \'11-50\', \'51-200\', "
            "\'201-1000\', \'1001-5000\', \'5000+\'. Map exact counts to the right bucket."
        ),
        "account.revenue_range": (
            "Annual revenue bucket. Use one of: \'<1M\', \'1-10M\', \'10-50M\', "
            "\'50-250M\', \'250M-1B\', \'1B+\'."
        ),
        "account.hq_location": "Headquarters city/region/country, as stated.",
        "account.tech_stack_item": (
            "A specific technology, tool, or vendor the company uses. Extract one entity per technology."
        ),
        "account.funding_stage": (
            "Funding stage. Use one of: \'bootstrapped\', \'pre_seed\', \'seed\', \'series_a\', "
            "\'series_b\', \'series_c\', \'series_d_plus\', \'public\', \'acquired\'."
        ),
        "contact.full_name": "A person\'s full name when referenced as a professional contact.",
        "contact.title": "The exact job title as stated.",
        "contact.seniority": (
            "Seniority bucket. Use one of: \'ic\', \'manager\', \'director\', \'vp\', \'c_suite\', \'founder\'."
        ),
        "contact.department": (
            "Department bucket. Use one of: \'engineering\', \'product\', \'sales\', \'marketing\', "
            "\'revops\', \'cs\', \'finance\', \'hr\', \'legal\', \'operations\', \'other\'."
        ),
        "contact.email": "A professional email address for the contact.",
        "contact.linkedin_url": "A LinkedIn profile URL for the contact.",
        "signal.hiring_trigger": (
            "A mention that the company is hiring for a specific role or team in a way "
            "that signals buying intent."
        ),
        "signal.funding_trigger": "A funding event with timing or amount.",
        "signal.tech_adoption": "A statement that the company has adopted or deployed a specific technology recently.",
        "signal.pain_point_mention": "A stated problem, frustration, or gap. Extract the pain phrase as-stated.",
        "signal.competitor_mention": "A named competitor product or vendor.",
        "signal.intent_topic": "A topic the account is actively researching.",
        "engagement.email_open": "A recorded email open event.",
        "engagement.email_reply": "A recorded email reply event.",
        "engagement.meeting_booked": "A booked or scheduled meeting reference.",
        "engagement.call_transcript_ref": "A reference to or excerpt from a sales call transcript.",
        "engagement.form_submit": "A form submission (demo request, content download, etc.).",
        "qualification.budget_confirmed": "Explicit evidence that budget exists or has been allocated. Quote the evidence.",
        "qualification.authority_identified": "Explicit evidence that the decision-maker has been identified. Quote the evidence.",
        "qualification.need_articulated": "Explicit evidence that a need or use case has been articulated. Quote the evidence.",
        "qualification.timeline_stated": "Explicit evidence of a buying timeline or compelling event. Quote the evidence.",
        "qualification.disposition": (
            "The overall qualification verdict. Use one of: \'qualified\', \'nurture\', \'disqualified\'."
        ),
        # Custom signals
        'custom.s_clean_core_initiative': 'Evidence that the account is implementing SAP\'s clean core strategy — removing custom code and side-by-side extensions in preparation for S/4HANA cloud migration. Qualifying evidence: job postings for "clean core architect" or "SAP clean core consultant," explicit statements about a clean core program, references to SAP Clean Core certification or SAP\'s clean core assessment tools. Clean core is a necessary but NOT sufficient signal for Joule readiness — it indicates the account is on the S/4 migration path but may still be 12-24 months from Joule readiness. Use as a medium-priority nurture signal; combine with S_S4_MIGRATION_TIMELINE for higher confidence.\n',
        'custom.s_joule_interest': 'Direct, prospect-initiated evidence that the account is evaluating or planning to implement SAP Joule — the SAP AI copilot embedded in S/4HANA and BTP. Qualifying evidence: the prospect names Joule specifically in a call, email, or document; a job posting explicitly lists SAP Joule as a required skill; the CIO or IT VP asks "how do we activate Joule?" during discovery. Does NOT qualify: SAP AE assertion that the account "should be interested in Joule" without end-customer confirmation; generic "AI" interest without naming Joule; intent-data topic hits from SAP marketing campaigns about Joule (SAP\'s own content, not the prospect\'s search behavior).\n',
        'custom.s_rise_adoption': "Evidence that the account has adopted or contracted for RISE with SAP — SAP's cloud ERP subscription bundle that includes S/4HANA Cloud and BTP entitlements. Qualifying evidence: the account is publicly listed as a RISE with SAP customer, a job posting requires RISE with SAP experience, an executive announcement references RISE, or a partner (SI or SAP AE) confirms a RISE contract is in place. RISE adoption is a strong signal because (1) it means S/4HANA is either live or being deployed, (2) BTP entitlements are included, and (3) Joule is available as part of the RISE license — meaning there is no additional infrastructure cost barrier to a Joule pilot.\n",
        'custom.s_s4_migration_timeline': 'Explicit evidence that the account has a confirmed, funded S/4HANA migration program with a named start date or completion target within the next 24 months. Qualifying evidence includes: an announced S/4 go-live target, a project team posting for S/4HANA roles, a press release or executive statement committing to S/4 migration, or a Big4 / SI partner reference to a live S/4 program at the account. Does NOT qualify: vague statements like "we plan to migrate eventually" or "we\'re evaluating S/4HANA" without a named timeline. The ECC-to-S/4 migration is the single most important precondition for a Joule pilot on an ECC account.\n',
        'custom.s_sap_field_co_sell': 'Active co-sell engagement from an SAP SE employee — specifically an SAP Account Executive, Area Sales Manager, Regional VP, or VP of Sales — who has introduced or referred this firm into an end-customer account via the SAP co-sell program or direct referral. Qualifying evidence: an SAP AE has sent an introduction email, set up a three-way meeting, or listed the firm as a co-sell partner in the SAP co-sell portal for a specific account. Does NOT qualify: informal LinkedIn connection with an SAP employee who has not made a specific referral; past SAP event attendance; general partner relationship with SAP SE without a named account-specific co-sell nomination. CRITICAL: this signal indicates channel engagement, NOT end-customer qualification. An account with S_SAP_FIELD_CO_SELL is not qualified until S_JOULE_INTEREST or Q_BUDGET_CONFIRMED is also present from the end-customer directly.\n',
        'custom.s_si_partner_involved': 'Evidence that a Systems Integrator (Big4 consulting firm or large IT consulting partner) is running or bidding on an SAP transformation program at the account, and has engaged or is evaluating this firm as a Joule/AI specialist subcontractor. Qualifying evidence: a Big4 MD or Partner has reached out about subcontracting; the firm is named in a Big4 proposal or SOW as a Joule specialist; a signed prime contract exists with a named SOW slot for Joule work. Does NOT qualify: a Big4 relationship at the account level without a live program; an SI firm that lost the prime contract; an SI exploring subcontractors for a proposal they have not yet won. CRITICAL: this signal indicates partner pipeline, not direct end-customer qualification. The end-customer budget is confirmed by the prime contract, not by direct end-customer conversation in SI-partner cases.\n',
    }

    # ICP overrides — narrow value space
    _guidance['account.employee_range'] = _guidance.get('account.employee_range', '') + ' ' + 'For this engagement, preferred values are: 5000+. Restrict to: 1001-5000, 5000+.'
    _guidance['account.funding_stage'] = _guidance.get('account.funding_stage', '') + ' ' + 'For this engagement, preferred values are: public, acquired.'
    _guidance['account.industry'] = _guidance.get('account.industry', '') + ' ' + 'For this engagement, preferred values are: Manufacturing, Chemicals, Retail, Life Sciences, Energy & Utilities, Consumer Products.'
    _guidance['account.revenue_range'] = _guidance.get('account.revenue_range', '') + ' ' + 'For this engagement, preferred values are: 1B+. Restrict to: 250M-1B, 1B+.'
    _guidance['contact.department'] = _guidance.get('contact.department', '') + ' ' + 'For this engagement, preferred values are: engineering, finance, operations.'
    _guidance['contact.seniority'] = _guidance.get('contact.seniority', '') + ' ' + 'For this engagement, preferred values are: c_suite, vp, director.'
    return _guidance


def valid_links() -> list[GtmEntityLink]:
    return [
        GtmEntityLink(from_label=GtmLabel.C_FULL_NAME, to_label=GtmLabel.A_COMPANY_NAME, relation="works_at"),
        GtmEntityLink(from_label=GtmLabel.C_TITLE, to_label=GtmLabel.C_FULL_NAME, relation="title_of"),
        GtmEntityLink(from_label=GtmLabel.S_HIRING_TRIGGER, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.S_FUNDING_TRIGGER, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.S_TECH_ADOPTION, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.S_PAIN_POINT_MENTION, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.E_EMAIL_REPLY, to_label=GtmLabel.C_FULL_NAME, relation="from_contact"),
        GtmEntityLink(from_label=GtmLabel.E_MEETING_BOOKED, to_label=GtmLabel.C_FULL_NAME, relation="with_contact"),
        GtmEntityLink(from_label=GtmLabel.Q_BUDGET_CONFIRMED, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.Q_AUTHORITY_IDENTIFIED, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.Q_NEED_ARTICULATED, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.Q_TIMELINE_STATED, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
        GtmEntityLink(from_label=GtmLabel.Q_DISPOSITION, to_label=GtmLabel.A_COMPANY_NAME, relation="concerns"),
    ]


SIGNAL_WEIGHTS: dict[str, float] = {
    'signal.funding_trigger': 0.15,
    'signal.hiring_trigger': 0.45,
    'signal.intent_topic': 0.75,
    'signal.pain_point_mention': 0.82,
    'signal.tech_adoption': 0.9,
}

def client_policy_rules() -> None:
    """Buyer-specific policy rules (from policy_overrides)."""
    pass
    # --- Disqualification rules ---
    # DISQUALIFY: A_TECH_STACK_ITEM not contains 'SAP'
    # Rationale: Non-SAP ERP accounts are a hard disqualification. The firm's entire service offering (Joule implementation, BTP AI Core, S/4HANA migration + AI uplift) is SAP-specific. Oracle Fusion, Workday, Dynamics 365, and NetSuite accounts cannot use Joule and cannot become clients regardless of size, budget, or expressed AI interest. Source: 02_icp_interview.md §4 anti-ICP #1.

    # DISQUALIFY: Q_NEED_ARTICULATED is null AND Q_TIMELINE_STATED is null
    # Rationale: No named use case AND no stated timeline = SAP tire-kicker / exploratory inquiry. This pattern — interest in "AI in SAP" without a specific process problem or project timeline — is the most common wasted-discovery pattern. The firm uses the test "does the prospect say what SAP process they want to improve and by when?" If both are absent after two discovery sessions, move to 6-month nurture. Source: 04_qualification_interview.md §1 use-case gate, 02_icp_interview.md §4 "no named AI use case after two discovery sessions = tire-kicker."

    # DISQUALIFY: Q_BUDGET_CONFIRMED is null AND Q_TIMELINE_STATED is null AND S_S4_MIGRATION_TIMELINE is null
    # Rationale: ECC account with no S/4 roadmap and no pilot budget = multi-year nurture. This is the profile of L1 (energy company, DQ'd after Readiness Assessment): large SAP footprint on ECC 6.0, no funded S/4 migration, no pilot budget. Without an S/4 migration timeline or confirmed budget, the Joule implementation is technically and commercially unviable. Cost: 60 days of discovery time on L1. Do not activate in pipeline; place in 18-month nurture cycle. Source: 02_icp_interview.md §4 anti-ICP #2, 05_failure_modes_interview.md FM-SAP-01.

    # --- Auto-pass rules ---
    # AUTO_PASS: Q_AUTHORITY_IDENTIFIED AND Q_NEED_ARTICULATED AND Q_BUDGET_CONFIRMED AND S_JOULE_INTEREST AND confidence > 0.75
    # Rationale: All four qualification gates confirmed at high confidence: executive sponsor (CIO/CFO) engaged, named Joule use case from the end-customer, budget $150k-$500k confirmed or in active procurement, and direct Joule interest (not SAP AE-suggested). This combination predicts high conversion probability based on P1 and P3 deal profiles. P1 had all four confirmed by end of discovery and closed in 14 weeks; P3 had all four confirmed by the first call (peer referral pre-qualified) and closed in 10 weeks. Route to AE for proposal scoping immediately. Source: 04_qualification_interview.md §1 auto-pass criteria, 01_company_overview.md §3 deal economics.

    # AUTO_PASS: S_RISE_ADOPTION AND Q_AUTHORITY_IDENTIFIED AND Q_NEED_ARTICULATED AND confidence > 0.70
    # Rationale: RISE with SAP account with identified authority and named need: RISE subscription includes Joule entitlement and BTP credits, meaning there is no infrastructure barrier to a Joule pilot. When the end-customer has RISE confirmed plus an executive sponsor and a named use case, the implementation risk is lower than on-prem and the budget is likely already accounted for in the RISE contract. P2 (retail, $410k, RISE customer) confirms this profile. The confidence threshold is slightly lower (0.70) because RISE itself is a strong signal that reduces technical risk. Route to AE for proposal scoping. Source: 02_icp_interview.md §1 tech-stack signal #1 (RISE = "very high signal").

    # --- HIL rules ---
    # HIL: S_SAP_FIELD_CO_SELL AND Q_BUDGET_CONFIRMED is null
    # Rationale: SAP-field co-sell WITHOUT end-customer budget confirmation: this is the "channel mirage" guard, the most costly qualification failure mode. An SAP AE referral without direct end-customer budget evidence is NOT qualified. Route to Alliances Owner (not AE) to verify budget with the AE and confirm a direct end-customer meeting before activating. Do not route to AE until budget is confirmed — this avoids the L3 pattern (45 days wasted on AE referral with no real budget). SAP AE enthusiasm is a co-sell routing signal, not a qualification signal. Source: 04_qualification_interview.md §3 routing rules, 03_channel_interview.md §2 SAP-field failure mode.

    # HIL: S_SI_PARTNER_INVOLVED AND Q_BUDGET_CONFIRMED is null
    # Rationale: SI-partner pull-through WITHOUT prime contract confirmation: Big4 MD relationship without a live program is the "partner mirage" failure mode (FM-SAP-03). Route to SI-Partner Lead to confirm prime contract status and SOW slot. Do not activate in pipeline until prime contract signed or final-stage LOI. Investing delivery capacity in unconfirmed SI-partner pursuits is a high-cost failure mode that occurred twice in the last 12 months. Source: 04_qualification_interview.md §3 routing rules, 03_channel_interview.md §3 SI-partner failure mode.

    # HIL: Q_AUTHORITY_IDENTIFIED AND Q_NEED_ARTICULATED AND S_S4_MIGRATION_TIMELINE AND Q_BUDGET_CONFIRMED is null
    # Rationale: Executive sponsor and named use case confirmed, S/4 migration timeline confirmed, but budget not yet confirmed: this account has high intent but the budget process is behind. These accounts often convert within one budget cycle if pursued correctly. Route to AE for direct CFO/CIO budget conversation. Do not move to auto-pass until budget is confirmed — timeline + need without budget is L2 risk profile (manufacturer lost to Accenture because CFO engagement was insufficient). Source: 04_qualification_interview.md §2 (Q_BUDGET_CONFIRMED evidence gate), 02_icp_interview.md §3 L2 deal loss.

    # HIL: S_CLEAN_CORE_INITIATIVE AND S_S4_MIGRATION_TIMELINE AND Q_NEED_ARTICULATED is null
    # Rationale: Clean core initiative + S/4 migration timeline but no named use case: this account is on the right technical trajectory but has not yet identified a specific Joule use case. These are high-value nurture accounts — technically ready within 12 months but not yet a buyer. Route to AE for nurture call: goal is to help the prospect identify a high-ROI Joule use case, not to close immediately. FM-SAP-09 notes that accounts in clean core + RISE migration mode are often missed because they don't yet have a named use case. Proactive nurture converts these in 6-12 months. Source: 05_failure_modes_interview.md FM-SAP-09, FM-SAP-07.

