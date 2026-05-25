"""
gtm@v1 — vertical schema for GTM artifact extraction.

Source documents are unstructured GTM artifacts: a company website page, a LinkedIn
profile or post, a sales call transcript, a CRM note, an inbound email, a 10-K excerpt.
The schema extracts structured signals (account attributes, contact attributes,
intent/trigger signals, engagement events, qualification dispositions) from any of these.

Modeled directly on the cord@v1 + funsd@v1 precedent: one composite schema with a
label union over linked entities, fed into the same extract → calibrate → provenance → HIL
pipeline. The spine does not change. Only this file, an ingest adapter, and the
schema-driven prompt path are touched.

Registers as: gtm@v1
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GtmLabel(str, Enum):
    """
    The GTM label union. Five entity families, each with a small flat label set.
    Kept deliberately compact — the *modifier* layer (ICP specifics, persona nuances,
    intent topic taxonomies) is per-customer and lives outside the schema, fit during
    the benchmark call. This is the generic spine.

    Families:
      A_*  Account     — company-level attributes
      C_*  Contact     — person-level attributes
      S_*  Signal      — intent / trigger event signals
      E_*  Engagement  — outbound/inbound interaction events
      Q_*  Qualification — disposition labels (MEDDIC/BANT-derived)
    """

    # --- Account family ---
    A_COMPANY_NAME = "account.company_name"
    A_DOMAIN = "account.domain"
    A_INDUSTRY = "account.industry"            # NAICS/SIC-style, free-text at v1
    A_EMPLOYEE_RANGE = "account.employee_range"  # e.g. "51-200" — CORD-style bucket
    A_REVENUE_RANGE = "account.revenue_range"   # e.g. "10M-50M"
    A_HQ_LOCATION = "account.hq_location"
    A_TECH_STACK_ITEM = "account.tech_stack_item"  # one row per detected technology
    A_FUNDING_STAGE = "account.funding_stage"   # e.g. "series_b", "bootstrapped", "public"

    # --- Contact family ---
    C_FULL_NAME = "contact.full_name"
    C_TITLE = "contact.title"
    C_SENIORITY = "contact.seniority"          # e.g. "director", "vp", "c-suite"
    C_DEPARTMENT = "contact.department"        # e.g. "engineering", "revops"
    C_EMAIL = "contact.email"
    C_LINKEDIN_URL = "contact.linkedin_url"

    # --- Signal family (intent / trigger events) ---
    S_HIRING_TRIGGER = "signal.hiring_trigger"        # e.g. "hiring 5 SDRs"
    S_FUNDING_TRIGGER = "signal.funding_trigger"      # e.g. "raised $20M Series B"
    S_TECH_ADOPTION = "signal.tech_adoption"          # e.g. "deployed Snowflake"
    S_PAIN_POINT_MENTION = "signal.pain_point_mention"
    S_COMPETITOR_MENTION = "signal.competitor_mention"
    S_INTENT_TOPIC = "signal.intent_topic"            # Bombora-style topic surge

    # --- Engagement family ---
    E_EMAIL_OPEN = "engagement.email_open"
    E_EMAIL_REPLY = "engagement.email_reply"
    E_MEETING_BOOKED = "engagement.meeting_booked"
    E_CALL_TRANSCRIPT_REF = "engagement.call_transcript_ref"
    E_FORM_SUBMIT = "engagement.form_submit"

    # --- Qualification family (MEDDIC/BANT-derived dispositions) ---
    Q_BUDGET_CONFIRMED = "qualification.budget_confirmed"
    Q_AUTHORITY_IDENTIFIED = "qualification.authority_identified"
    Q_NEED_ARTICULATED = "qualification.need_articulated"
    Q_TIMELINE_STATED = "qualification.timeline_stated"
    Q_DISPOSITION = "qualification.disposition"  # "qualified" | "nurture" | "disqualified"


class GtmEntity(BaseModel):
    """
    Schema-stamped entity. Mirrors the FUNSD/CORD entity shape exactly so the
    spine's pipeline.py, calibration/, provenance/, hil/, and eval/f1.py do not change.
    """
    model_config = ConfigDict(extra="forbid")

    label: GtmLabel
    text: str = Field(..., description="The raw extracted span from the source.")
    normalized_value: Optional[str] = Field(
        default=None,
        description=(
            "Optional canonical form. E.g. 'VP of Sales' → 'vice_president'; "
            "'$20M Series B' → '20000000'. Spine doesn't require this — F1 uses "
            "(label, normalized_text) match, with normalized_text falling back to text."
        ),
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Required and bounded [0,1] — matches funsd@v2/cord@v1 contract.",
    )


class GtmEntityLink(BaseModel):
    """
    Mirrors gold_entity_links shape. Used for: contact→account membership,
    signal→account attribution, engagement→contact attribution, qualification→account.
    Spine handles this generically; the schema only declares which link types are valid.
    """
    model_config = ConfigDict(extra="forbid")

    from_label: GtmLabel
    to_label: GtmLabel
    relation: str  # e.g. "works_at", "occurred_at", "concerns"


# ---------------------------------------------------------------------------
# extraction_guidance() — the schema-driven prompt surface.
#
# This is the function extract/llm.py calls (per Story C-3, after the prompt
# genericization). The schema OWNS its label definitions, so the spine's
# prompt-building code does not branch on dataset.
# ---------------------------------------------------------------------------

def extraction_guidance() -> dict[str, str]:
    """
    Return a {label_value: human_definition} mapping. The extractor prompt
    is assembled from this dict — same code path as cord@v1, no per-vertical
    branching in pipeline.py.
    """
    return {
        # Account
        GtmLabel.A_COMPANY_NAME.value: "The legal or commonly-used name of a company being discussed.",
        GtmLabel.A_DOMAIN.value: "The primary web domain of a company (e.g. 'acme.com').",
        GtmLabel.A_INDUSTRY.value: "The industry the company operates in. Use the most specific form stated.",
        GtmLabel.A_EMPLOYEE_RANGE.value: (
            "Employee count as a bucket. Use one of: '1-10', '11-50', '51-200', "
            "'201-1000', '1001-5000', '5000+'. Map exact counts to the right bucket."
        ),
        GtmLabel.A_REVENUE_RANGE.value: (
            "Annual revenue bucket. Use one of: '<1M', '1-10M', '10-50M', "
            "'50-250M', '250M-1B', '1B+'."
        ),
        GtmLabel.A_HQ_LOCATION.value: "Headquarters city/region/country, as stated.",
        GtmLabel.A_TECH_STACK_ITEM.value: (
            "A specific technology, tool, or vendor the company uses (e.g. 'Salesforce', "
            "'Snowflake', 'React'). Extract one entity per technology mentioned."
        ),
        GtmLabel.A_FUNDING_STAGE.value: (
            "Funding stage. Use one of: 'bootstrapped', 'pre_seed', 'seed', 'series_a', "
            "'series_b', 'series_c', 'series_d_plus', 'public', 'acquired'."
        ),

        # Contact
        GtmLabel.C_FULL_NAME.value: "A person's full name when referenced as a professional contact.",
        GtmLabel.C_TITLE.value: "The exact job title as stated (e.g. 'Director of Revenue Operations').",
        GtmLabel.C_SENIORITY.value: (
            "Seniority bucket. Use one of: 'ic', 'manager', 'director', 'vp', 'c_suite', 'founder'."
        ),
        GtmLabel.C_DEPARTMENT.value: (
            "Department bucket. Use one of: 'engineering', 'product', 'sales', 'marketing', "
            "'revops', 'cs', 'finance', 'hr', 'legal', 'operations', 'other'."
        ),
        GtmLabel.C_EMAIL.value: "A professional email address for the contact.",
        GtmLabel.C_LINKEDIN_URL.value: "A LinkedIn profile URL for the contact.",

        # Signal
        GtmLabel.S_HIRING_TRIGGER.value: (
            "A mention that the company is hiring for a specific role or team in a way "
            "that signals buying intent (e.g. 'hiring a Head of Data', 'expanding the SDR team')."
        ),
        GtmLabel.S_FUNDING_TRIGGER.value: (
            "A funding event with timing or amount (e.g. 'raised $20M Series B in March')."
        ),
        GtmLabel.S_TECH_ADOPTION.value: (
            "A statement that the company has adopted, migrated to, or deployed a specific "
            "technology recently (not just 'uses')."
        ),
        GtmLabel.S_PAIN_POINT_MENTION.value: (
            "A stated problem, frustration, or gap (e.g. 'our pipeline reporting is broken', "
            "'we can't scale onboarding'). Extract the pain phrase as-stated."
        ),
        GtmLabel.S_COMPETITOR_MENTION.value: "A named competitor product or vendor.",
        GtmLabel.S_INTENT_TOPIC.value: (
            "A topic the account is actively researching (e.g. 'data warehouse migration', "
            "'AI sales tooling'). Use Bombora-style topic naming when possible."
        ),

        # Engagement
        GtmLabel.E_EMAIL_OPEN.value: "A recorded email open event.",
        GtmLabel.E_EMAIL_REPLY.value: "A recorded email reply event, including the reply text if available.",
        GtmLabel.E_MEETING_BOOKED.value: "A booked or scheduled meeting reference.",
        GtmLabel.E_CALL_TRANSCRIPT_REF.value: "A reference to or excerpt from a sales call transcript.",
        GtmLabel.E_FORM_SUBMIT.value: "A form submission (demo request, content download, etc.).",

        # Qualification — MEDDIC/BANT-derived. These are *evidence* labels, not verdicts;
        # the Q_DISPOSITION label captures the verdict.
        GtmLabel.Q_BUDGET_CONFIRMED.value: (
            "Explicit evidence that budget exists or has been allocated. Quote the evidence."
        ),
        GtmLabel.Q_AUTHORITY_IDENTIFIED.value: (
            "Explicit evidence that the decision-maker has been identified. Quote the evidence."
        ),
        GtmLabel.Q_NEED_ARTICULATED.value: (
            "Explicit evidence that a need or use case has been articulated. Quote the evidence."
        ),
        GtmLabel.Q_TIMELINE_STATED.value: (
            "Explicit evidence of a buying timeline or compelling event. Quote the evidence."
        ),
        GtmLabel.Q_DISPOSITION.value: (
            "The overall qualification verdict for the account/opportunity. "
            "Use one of: 'qualified', 'nurture', 'disqualified'."
        ),
    }


def valid_links() -> list[GtmEntityLink]:
    """
    Declared link types. The spine's gold_entity_links + provenance machinery is generic;
    this just tells the extractor / eval which relations are meaningful.
    """
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
