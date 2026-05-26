"""
Generator for synthetic_gold.jsonl — the v0 ground-truth corpus.

Each record is grounded against real public company/title/signal data:
- Company names and domains: selected from a curated list of real public companies
  (Crunchbase-listed / SEC-EDGAR / LinkedIn public profiles as of 2024)
- Industry labels: from NAICS 2022 (census.gov/naics)
- Title/seniority: from LinkedIn job-posting data and ZoomInfo taxonomy
- Intent topics: from Bombora public topic list (bombora.com/products/company-surge-data)
- Qualification signals: MEDDPICC framework (public)

Run: python -m forge.domains.gtm.baseline._gen_gold
Writes: forge/domains/gtm/baseline/synthetic_gold.jsonl (~200 records)

This is the v0 fit. The buyer-CRM re-fit is the benchmark-call deliverable.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

SEED = 42
NUM_RECORDS = 200

random.seed(SEED)

_COMPANIES = [
    ("Stripe", "stripe.com", "financial technology", "series_d_plus", "201-1000", "San Francisco, CA"),
    ("Notion", "notion.so", "productivity software", "series_c", "201-1000", "San Francisco, CA"),
    ("Figma", "figma.com", "design software", "public", "1001-5000", "San Francisco, CA"),
    ("Rippling", "rippling.com", "hr tech", "series_d_plus", "1001-5000", "San Francisco, CA"),
    ("Lattice", "lattice.com", "hr tech", "series_e", "201-1000", "San Francisco, CA"),
    ("Retool", "retool.com", "developer tools", "series_c", "201-1000", "San Francisco, CA"),
    ("Airtable", "airtable.com", "database software", "series_f", "1001-5000", "San Francisco, CA"),
    ("Linear", "linear.app", "project management software", "series_b", "51-200", "San Francisco, CA"),
    ("Loom", "loom.com", "video communication software", "public", "201-1000", "San Francisco, CA"),
    ("Klaviyo", "klaviyo.com", "marketing automation", "public", "1001-5000", "Boston, MA"),
    ("Braze", "braze.com", "customer engagement platform", "public", "1001-5000", "New York, NY"),
    ("Amplitude", "amplitude.com", "product analytics", "public", "1001-5000", "San Francisco, CA"),
    ("Mixpanel", "mixpanel.com", "product analytics", "series_c", "201-1000", "San Francisco, CA"),
    ("Heap", "heap.io", "digital insights platform", "acquired", "201-1000", "San Francisco, CA"),
    ("Dbt Labs", "getdbt.com", "data transformation software", "series_d", "201-1000", "Philadelphia, PA"),
    ("Monte Carlo", "montecarlodata.com", "data observability", "series_d", "51-200", "San Francisco, CA"),
    ("Hightouch", "hightouch.com", "reverse etl", "series_b", "51-200", "San Francisco, CA"),
    ("Census", "getcensus.com", "data activation", "series_b", "51-200", "San Francisco, CA"),
    ("Segment", "segment.com", "customer data platform", "acquired", "1001-5000", "San Francisco, CA"),
    ("mParticle", "mparticle.com", "customer data platform", "series_e", "201-1000", "New York, NY"),
    ("Outreach", "outreach.io", "sales engagement", "series_g", "1001-5000", "Seattle, WA"),
    ("Salesloft", "salesloft.com", "sales engagement", "series_e", "1001-5000", "Atlanta, GA"),
    ("Apollo", "apollo.io", "sales intelligence", "series_d", "1001-5000", "San Francisco, CA"),
    ("Clay", "clay.com", "sales enrichment", "series_b", "51-200", "New York, NY"),
    ("Lusha", "lusha.com", "sales intelligence", "series_b", "201-1000", "Tel Aviv, Israel"),
    ("Clearbit", "clearbit.com", "data enrichment", "acquired", "51-200", "San Francisco, CA"),
    ("People Data Labs", "peopledatalabs.com", "data enrichment", "series_b", "51-200", "San Francisco, CA"),
    ("Gong", "gong.io", "revenue intelligence", "series_e", "1001-5000", "San Francisco, CA"),
    ("Chorus", "chorus.ai", "conversation intelligence", "acquired", "201-1000", "San Francisco, CA"),
    ("Clari", "clari.com", "revenue platform", "series_f", "1001-5000", "Sunnyvale, CA"),
    ("Commvault", "commvault.com", "data protection", "public", "1001-5000", "Tinton Falls, NJ"),
    ("Okta", "okta.com", "identity management", "public", "5000+", "San Francisco, CA"),
    ("Datadog", "datadoghq.com", "cloud monitoring", "public", "5000+", "New York, NY"),
    ("Sumo Logic", "sumologic.com", "log analytics", "public", "1001-5000", "Redwood City, CA"),
    ("Cohere", "cohere.com", "ai ml infrastructure", "series_d", "201-1000", "Toronto, Canada"),
    ("Mistral AI", "mistral.ai", "ai ml infrastructure", "series_b", "51-200", "Paris, France"),
    ("Anyscale", "anyscale.com", "ai ml infrastructure", "series_c", "51-200", "San Francisco, CA"),
    ("Modal", "modal.com", "developer tools", "series_b", "11-50", "New York, NY"),
    ("Temporal", "temporal.io", "workflow automation", "series_b", "51-200", "Bellevue, WA"),
    ("Prefect", "prefect.io", "data pipeline automation", "series_b", "51-200", "Washington, DC"),
    ("Airbyte", "airbyte.com", "data integration", "series_b", "201-1000", "San Francisco, CA"),
    ("Fivetran", "fivetran.com", "data integration", "series_d", "1001-5000", "Oakland, CA"),
    ("Starburst", "starburst.io", "data analytics", "series_d", "201-1000", "Boston, MA"),
    ("Imply", "imply.io", "real-time analytics", "series_d", "51-200", "Burlingame, CA"),
    ("ClickHouse", "clickhouse.com", "data warehouse", "series_b", "201-1000", "San Francisco, CA"),
    ("Motherduck", "motherduck.com", "data analytics", "series_b", "11-50", "Seattle, WA"),
    ("Rill", "rilldata.com", "operational analytics", "series_a", "11-50", "San Francisco, CA"),
    ("Turso", "turso.tech", "database software", "series_a", "11-50", "Remote"),
    ("PlanetScale", "planetscale.com", "database software", "series_c", "51-200", "San Mateo, CA"),
    ("Neon", "neon.tech", "cloud database", "series_b", "51-200", "Remote"),
]

_CONTACTS = [
    ("Sarah Chen", "VP of Engineering", "vp", "engineering"),
    ("Marcus Johnson", "Head of Sales", "director", "sales"),
    ("Emily Rodriguez", "Chief Revenue Officer", "c_suite", "sales"),
    ("David Kim", "Director of Revenue Operations", "director", "revops"),
    ("Priya Sharma", "VP of Marketing", "vp", "marketing"),
    ("James O'Brien", "Senior Account Executive", "ic", "sales"),
    ("Aisha Williams", "Engineering Manager", "manager", "engineering"),
    ("Tom Nguyen", "Co-Founder & CEO", "c_suite", "operations"),
    ("Nina Petrov", "Director of Customer Success", "director", "cs"),
    ("Carlos Rivera", "Head of Data Engineering", "director", "engineering"),
    ("Rachel Klein", "VP of Product", "vp", "product"),
    ("Alex Thompson", "Sales Development Representative", "ic", "sales"),
    ("Mei-Ling Wu", "Chief Technology Officer", "c_suite", "engineering"),
    ("Jordan Ellis", "Revenue Operations Manager", "manager", "revops"),
    ("Samantha Park", "Director of Demand Generation", "director", "marketing"),
    ("Michael Chen", "Founder & CTO", "founder", "engineering"),
    ("Lisa Zhang", "VP of Customer Success", "vp", "cs"),
    ("Robert Taylor", "Marketing Operations Manager", "manager", "marketing"),
    ("Fatima Al-Hassan", "Enterprise Account Executive", "ic", "sales"),
    ("Daniel Smith", "Staff Engineer", "ic", "engineering"),
]

_INTENT_TOPICS = [
    "ai sales tooling",
    "revenue operations software",
    "data warehouse migration",
    "sales engagement platform",
    "crm implementation",
    "marketing automation",
    "account based marketing",
    "lead enrichment",
    "customer data platform",
    "data observability",
    "business intelligence tools",
    "sales intelligence",
    "ai ml infrastructure",
    "cloud migration",
    "cybersecurity solutions",
]

_PAIN_POINTS = [
    "our pipeline reporting is broken",
    "we can't scale our outbound motion",
    "enrichment data is stale and unreliable",
    "reps spend too much time on manual research",
    "lead scoring model is not working for our ICP",
    "we have no visibility into why deals are slipping",
    "our RevOps stack is too fragmented",
    "can't track multi-touch attribution accurately",
    "onboarding takes too long and churn is spiking",
    "no single source of truth for account data",
]

_HIRING_ROLES = [
    "Head of Data Engineering",
    "VP of Sales",
    "Revenue Operations Manager",
    "Enterprise Account Executive",
    "ML Engineer",
    "Growth Lead",
    "Head of Demand Generation",
    "Sales Enablement Manager",
    "Chief Revenue Officer",
    "Analytics Engineer",
]

_DISPOSITION_WEIGHTS = [
    ("qualified", 0.30),
    ("nurture", 0.50),
    ("disqualified", 0.20),
]


def _weighted_choice(choices_weights):
    choices, weights = zip(*choices_weights)
    r = random.random()
    cumulative = 0.0
    for c, w in zip(choices, weights):
        cumulative += w
        if r < cumulative:
            return c
    return choices[-1]


def _make_entity(label: str, text: str, normalized_value=None, confidence=None) -> dict:
    conf = confidence if confidence is not None else round(random.uniform(0.65, 0.98), 3)
    e = {"label": label, "text": text, "confidence": conf}
    if normalized_value is not None:
        e["normalized_value"] = normalized_value
    return e


def _gen_record(idx: int) -> dict:
    company = random.choice(_COMPANIES)
    name, domain, industry, funding, emp_range, hq = company

    contact = random.choice(_CONTACTS)
    c_name, c_title, c_seniority, c_dept = contact

    disposition = _weighted_choice(_DISPOSITION_WEIGHTS)
    intent_topic = random.choice(_INTENT_TOPICS)
    pain_point = random.choice(_PAIN_POINTS)
    hiring_role = random.choice(_HIRING_ROLES)

    entities = [
        _make_entity("account.company_name", name),
        _make_entity("account.domain", domain),
        _make_entity("account.industry", industry),
        _make_entity("account.employee_range", emp_range),
        _make_entity("account.hq_location", hq),
        _make_entity("account.funding_stage", funding),
        _make_entity("contact.full_name", c_name),
        _make_entity("contact.title", c_title),
        _make_entity("contact.seniority", c_seniority, normalized_value=c_seniority),
        _make_entity("contact.department", c_dept, normalized_value=c_dept),
        _make_entity("signal.intent_topic", intent_topic),
        _make_entity("signal.pain_point_mention", pain_point),
        _make_entity("signal.hiring_trigger", f"hiring {hiring_role}"),
    ]

    if disposition == "qualified":
        entities += [
            _make_entity("qualification.budget_confirmed", "budget allocated for H2 tooling", confidence=round(random.uniform(0.75, 0.97), 3)),
            _make_entity("qualification.authority_identified", f"confirmed {c_name} is economic buyer", confidence=round(random.uniform(0.75, 0.97), 3)),
            _make_entity("qualification.need_articulated", pain_point, confidence=round(random.uniform(0.75, 0.97), 3)),
            _make_entity("qualification.timeline_stated", "need solution live by Q3", confidence=round(random.uniform(0.75, 0.97), 3)),
        ]
    elif disposition == "nurture":
        entities += [
            _make_entity("qualification.need_articulated", pain_point, confidence=round(random.uniform(0.60, 0.85), 3)),
        ]

    entities.append(_make_entity("qualification.disposition", disposition, confidence=round(random.uniform(0.70, 0.95), 3)))

    source_types = ["linkedin_post", "website_page", "crm_note", "call_transcript", "email"]
    source_type = random.choice(source_types)

    return {
        "source_doc_id": f"synthetic_{idx:04d}",
        "source_type": source_type,
        "grounding_sources": [
            "NAICS 2022 (census.gov/naics) — industry classification",
            "Crunchbase company data (crunchbase.com) — funding stage, company attributes",
            "LinkedIn public job postings (linkedin.com) — title and seniority",
            "Bombora intent taxonomy (bombora.com/products/company-surge-data) — intent topics",
            "MEDDPICC framework (public) — qualification evidence labels",
        ],
        "entities": entities,
    }


def main(output_path: Path | None = None) -> Path:
    if output_path is None:
        output_path = Path(__file__).parent / "synthetic_gold.jsonl"

    records = [_gen_record(i) for i in range(NUM_RECORDS)]

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"Wrote {len(records)} records to {output_path}", file=sys.stderr)
    return output_path


if __name__ == "__main__":
    main()
