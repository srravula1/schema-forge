"""
gtm_aiconsultingfirm@v1 — client-specific GTM schema derived from gtm@v1 baseline.

This module is self-contained. No spine or schema-forge imports are needed.
Drop this file into spine/schema/ to integrate.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GtmLabel(str, Enum):
    """GTM label union. Base labels (from the gtm baseline) + client-specific custom signals."""

    A_COMPANY_NAME = 'account.company_name'
    A_DOMAIN = 'account.domain'
    A_INDUSTRY = 'account.industry'
    A_EMPLOYEE_RANGE = 'account.employee_range'
    A_REVENUE_RANGE = 'account.revenue_range'
    A_HQ_LOCATION = 'account.hq_location'
    A_TECH_STACK_ITEM = 'account.tech_stack_item'
    A_FUNDING_STAGE = 'account.funding_stage'
    C_FULL_NAME = 'contact.full_name'
    C_TITLE = 'contact.title'
    C_SENIORITY = 'contact.seniority'
    C_DEPARTMENT = 'contact.department'
    C_EMAIL = 'contact.email'
    C_LINKEDIN_URL = 'contact.linkedin_url'
    C_AFFILIATION = 'contact.affiliation'
    S_HIRING_TRIGGER = 'signal.hiring_trigger'
    S_FUNDING_TRIGGER = 'signal.funding_trigger'
    S_TECH_ADOPTION = 'signal.tech_adoption'
    S_PAIN_POINT_MENTION = 'signal.pain_point_mention'
    S_COMPETITOR_MENTION = 'signal.competitor_mention'
    S_INTENT_TOPIC = 'signal.intent_topic'
    E_EMAIL_OPEN = 'engagement.email_open'
    E_EMAIL_REPLY = 'engagement.email_reply'
    E_MEETING_BOOKED = 'engagement.meeting_booked'
    E_CALL_TRANSCRIPT_REF = 'engagement.call_transcript_ref'
    E_FORM_SUBMIT = 'engagement.form_submit'
    Q_BUDGET_CONFIRMED = 'qualification.budget_confirmed'
    Q_AUTHORITY_IDENTIFIED = 'qualification.authority_identified'
    Q_NEED_ARTICULATED = 'qualification.need_articulated'
    Q_TIMELINE_STATED = 'qualification.timeline_stated'
    Q_DISPOSITION = 'qualification.disposition'

    # --- Custom signals (from channel_overrides) ---
    S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT = 'custom.s_linkedin_thought_leadership_engagement'


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
        'account.company_name': 'The legal or commonly-used name of a company being discussed.',
        'account.domain': "The primary web domain of a company (e.g. 'acme.com').",
        'account.industry': 'The industry the company operates in. Use the most specific form stated.',
        'account.employee_range': "Employee count as a bucket. Use one of: '1-10', '11-50', '51-200', '201-1000', '1001-5000', '5000+'. Map exact counts to the right bucket.",
        'account.revenue_range': "Annual revenue bucket. Use one of: '<1M', '1-10M', '10-50M', '50-250M', '250M-1B', '1B+'.",
        'account.hq_location': 'Headquarters city/region/country, as stated.',
        'account.tech_stack_item': "A specific technology, tool, or vendor the company uses (e.g. 'Salesforce', 'Snowflake', 'React'). Extract one entity per technology mentioned.",
        'account.funding_stage': "Funding stage. Use one of: 'bootstrapped', 'pre_seed', 'seed', 'series_a', 'series_b', 'series_c', 'series_d_plus', 'public', 'acquired'.",
        'contact.full_name': "A person's full name when referenced as a professional contact.",
        'contact.title': "The exact job title as stated (e.g. 'Director of Revenue Operations').",
        'contact.seniority': "Seniority bucket. Use one of: 'ic', 'manager', 'director', 'vp', 'c_suite', 'founder'.",
        'contact.department': "Department bucket. Use one of: 'engineering', 'product', 'sales', 'marketing', 'revops', 'cs', 'finance', 'hr', 'legal', 'operations', 'other'.",
        'contact.email': 'A professional email address for the contact.',
        'contact.linkedin_url': 'A LinkedIn profile URL for the contact.',
        'contact.affiliation': "The organization the contact belongs to relative to the deal. Use one of: 'end_customer' (works at the prospect/buying company), 'channel_partner' (a referral/co-sell partner, reseller, or systems integrator), 'vendor' (works for a solution vendor), 'internal' (your own company), 'unknown'. Engagement-specific partner sub-types (e.g. SAP field vs SI) stay in overrides.",
        'signal.hiring_trigger': "A mention that the company is hiring for a specific role or team in a way that signals buying intent (e.g. 'hiring a Head of Data', 'expanding the SDR team').",
        'signal.funding_trigger': "A funding event with timing or amount (e.g. 'raised $20M Series B in March').",
        'signal.tech_adoption': "A statement that the company has adopted, migrated to, or deployed a specific technology recently (not just 'uses').",
        'signal.pain_point_mention': "A stated problem, frustration, or gap (e.g. 'our pipeline reporting is broken', 'we can't scale onboarding'). Extract the pain phrase as-stated.",
        'signal.competitor_mention': 'A named competitor product or vendor.',
        'signal.intent_topic': "A topic the account is actively researching (e.g. 'data warehouse migration', 'AI sales tooling'). Use Bombora-style topic naming when possible.",
        'engagement.email_open': 'A recorded email open event.',
        'engagement.email_reply': 'A recorded email reply event, including the reply text if available.',
        'engagement.meeting_booked': 'A booked or scheduled meeting reference.',
        'engagement.call_transcript_ref': 'A reference to or excerpt from a sales call transcript.',
        'engagement.form_submit': 'A form submission (demo request, content download, etc.).',
        'qualification.budget_confirmed': 'Explicit evidence that budget exists or has been allocated. Quote the evidence.',
        'qualification.authority_identified': 'Explicit evidence that the decision-maker has been identified. Quote the evidence.',
        'qualification.need_articulated': 'Explicit evidence that a need or use case has been articulated. Quote the evidence.',
        'qualification.timeline_stated': 'Explicit evidence of a buying timeline or compelling event. Quote the evidence.',
        'qualification.disposition': "The overall qualification verdict for the account/opportunity. Use one of: 'qualified', 'nurture', 'disqualified'.",
        # Custom signals
        'custom.s_linkedin_thought_leadership_engagement': "Prospect has engaged with founder LinkedIn content on AI/LLM topics in the last 14 days, with engagement that contains specific technical or business context (not generic 'great post' comments). Qualifying engagement includes: comments describing a specific problem the prospect is facing, DMs with a business-specific AI question, or reshares with context that reveals organizational relevance. Does NOT qualify: generic likes, 'great insights' comments, single engagement events without follow-on activity.\n",
    }

    # ICP overrides — narrow value space
    _guidance['account.employee_range'] = _guidance.get('account.employee_range', '') + ' ' + 'Restrict to: 11-50, 51-200. Exclude: 1-10, 201-1000, 1001-5000, 5000+.'
    _guidance['account.funding_stage'] = _guidance.get('account.funding_stage', '') + ' ' + 'Exclude: pre_seed, seed.'
    _guidance['account.industry'] = _guidance.get('account.industry', '') + ' ' + 'For this engagement, preferred values are: AI/ML services, SaaS, Professional services, Data infrastructure, Legal technology, HR technology, Developer tools.'
    return _guidance


def valid_links() -> list[GtmEntityLink]:
    return [
        GtmEntityLink(from_label=GtmLabel.C_FULL_NAME, to_label=GtmLabel.A_COMPANY_NAME, relation='works_at'),
        GtmEntityLink(from_label=GtmLabel.C_TITLE, to_label=GtmLabel.C_FULL_NAME, relation='title_of'),
        GtmEntityLink(from_label=GtmLabel.S_HIRING_TRIGGER, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
        GtmEntityLink(from_label=GtmLabel.S_FUNDING_TRIGGER, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
        GtmEntityLink(from_label=GtmLabel.S_TECH_ADOPTION, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
        GtmEntityLink(from_label=GtmLabel.S_PAIN_POINT_MENTION, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
        GtmEntityLink(from_label=GtmLabel.E_EMAIL_REPLY, to_label=GtmLabel.C_FULL_NAME, relation='from_contact'),
        GtmEntityLink(from_label=GtmLabel.E_MEETING_BOOKED, to_label=GtmLabel.C_FULL_NAME, relation='with_contact'),
        GtmEntityLink(from_label=GtmLabel.Q_BUDGET_CONFIRMED, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
        GtmEntityLink(from_label=GtmLabel.Q_AUTHORITY_IDENTIFIED, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
        GtmEntityLink(from_label=GtmLabel.Q_NEED_ARTICULATED, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
        GtmEntityLink(from_label=GtmLabel.Q_TIMELINE_STATED, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
        GtmEntityLink(from_label=GtmLabel.Q_DISPOSITION, to_label=GtmLabel.A_COMPANY_NAME, relation='concerns'),
    ]


SIGNAL_WEIGHTS: dict[str, float] = {
    'signal.funding_trigger': 0.55,
    'signal.hiring_trigger': 0.35,
    'signal.intent_topic': 0.78,
    'signal.pain_point_mention': 0.92,
    'signal.tech_adoption': 0.8,
}

def client_policy_rules() -> None:
    """Buyer-specific policy rules (from policy_overrides)."""
    pass
    # --- Disqualification rules ---
    # DISQUALIFY: A_EMPLOYEE_RANGE in ['1-10']
    # Rationale: Under 10 employees: insufficient internal infrastructure to absorb a $50k+ engagement. These companies lack a dedicated engineering owner, have immature data practices, and cannot allocate 20% of a technical lead's time to an engagement. Confirmed by regret R-1 (seed-stage, 12 employees — data unready) and multiple explicit disqualifications in the ICP interview. The '1-10' bucket maps to companies under ~10 people.

    # DISQUALIFY: A_FUNDING_STAGE in ['pre_seed', 'seed']
    # Rationale: Pre-seed and seed companies routinely fail the three project readiness gates: data readiness (no clean corpus), owner readiness (no named technical owner), infrastructure readiness (no production cloud deployment). Budget also typically insufficient for $50k+ sprint engagements. Confirmed by regret R-1 and ICP interview analysis. Note: bootstrapped companies are NOT disqualified — only VC-backed pre-revenue stages.

    # DISQUALIFY: Q_NEED_ARTICULATED is null AND Q_TIMELINE_STATED is null
    # Rationale: 'AI tire-kicker / fake yes' pattern: no articulated need + no stated timeline = exploratory intent, not a real project. Confirmed by failure modes interview §3 and ICP interview §5 (outsider question): "The word 'explore' is a red flag. Real buyers say 'we have X problem and we need to solve it by Y date.'" Both signals absent together is a reliable disqualification trigger.

    # --- Auto-pass rules ---
    # AUTO_PASS: Q_BUDGET_CONFIRMED AND Q_AUTHORITY_IDENTIFIED AND Q_NEED_ARTICULATED AND confidence > 0.75
    # Rationale: Three MEDDIC evidence gates confirmed (budget, authority, need) at high confidence. Won-deal analysis: all 5 closed-won deals had all three confirmed by end of discovery. When all three are present with confidence > 0.75, this combination predicts >80% close rate in the deal history reviewed. Route to AE for proposal scoping. The fourth gate (Q_TIMELINE_STATED) is still required before contract — this rule gates the discovery-to- proposal transition, not discovery-to-contract.

    # --- HIL rules ---
    # HIL: S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT AND Q_NEED_ARTICULATED AND confidence > 0.5
    # Rationale: LinkedIn-inbound with articulated need: this is the boundary between AI tire-kicker and real buyer, and automated routing gets it wrong too often. Human review required to assess whether the articulated need is specific (business-contextualized problem) or vague (exploratory). Channel interview §2: "a vendor name, a specific failure mode, and a business context in the first message is almost always a buyer" — that specificity check requires human judgment. Route to founder or senior AE for 5-minute assessment. S_LINKEDIN_THOUGHT_LEADERSHIP_ENGAGEMENT is the custom signal defined in channel_overrides.yaml (add_to_schema: true), so it is a valid reference here.

    # HIL: Q_BUDGET_CONFIRMED AND Q_AUTHORITY_IDENTIFIED AND Q_TIMELINE_STATED is null
    # Rationale: Budget and authority confirmed but no timeline = possible project not yet real. This combination appeared in 2 of 5 lost deals (L-4: budget cycle miss, L-2: CTO departure caused timing issue). Without a stated timeline, we cannot confirm that the project exists within the current budget cycle. HIL to probe: "Is this project specifically budgeted for Q[current], and who internally owns the timeline?"

    # HIL: A_EMPLOYEE_RANGE in ['51-200'] AND A_FUNDING_STAGE in ['series_b', 'series_c', 'series_d_plus']
    # Rationale: Series B/C+ companies in the employee sweet spot: these are high-value but may have procurement friction (see Deal L-1, 300-employee Series C that went to a larger firm on credibility). HIL to assess: is there a procurement process? Does our team size create delivery risk perception? These prospects need a different close motion (more references, possibly a subcontractor structure).

