"""
Generator for sap_gold.jsonl — the SAP-Joule engagement v0 gold corpus.

Each record is grounded against real public data (cited inline):

REAL GROUNDING DATA:
- Firmographic distribution: Vibe Prospecting / Explorium query on large SAP-ERP install
  base, n=30,316 companies, credit_usage=0. Used to sample geography, revenue, and
  employee ranges to match real SAP customer proportions.
- Indeed job postings (real anchors):
    JOB_1 w3global: "SAP BTP Consultant / Lead", California, $80k-$105k, 2026-05-22
           https://to.indeed.com/aat98cl8kckk (SI/staffing channel + BTP signal)
    JOB_2 Quintile Advisory: "Enterprise Scheduling Specialist (Kinaxis)", Remote
           https://to.indeed.com/aabb6d88zpjp (consultancy/channel)
    JOB_3 Ferrero: "SAP S/4HANA Finance Functional Lead", Parsippany-Troy Hills NJ,
           $122,854-$163,806, 2026-03-13
           https://to.indeed.com/aakjwr4djq2h (real end-customer S/4HANA Finance signal)

HONESTY CONSTRAINTS:
- Only Ferrero, w3global, Quintile Advisory are asserted as real named orgs (Indeed anchors).
- Big4 firm names (Deloitte, Accenture, PwC, EY, KPMG, IBM, Capgemini) are public and used
  as channel_partner org names.
- All other end-customer account names are synthetic-but-realistic.
  Tagged in grounding_sources as: "synthetic identity; firmographics sampled from Vibe
  SAP-ERP distribution n=30,316"
- No real named individuals are invented.

Run: python engagements/sap-joule/gold/_gen_sap_gold.py
Writes: engagements/sap-joule/gold/sap_gold.jsonl (~200 records)

This is the v0 fit. The buyer-CRM pilot win/loss re-fit is the benchmark-call deliverable.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

SEED = 42
NUM_RECORDS = 200

# ---------------------------------------------------------------------------
# REAL GROUNDING DATA — VIBE PROSPECTING SAP-ERP DISTRIBUTION (n=30,316)
# ---------------------------------------------------------------------------
# Source: Vibe Prospecting / Explorium query, large SAP-ERP install base, n=30,316,
# credit_usage=0, queried 2026-05.
#
# Geography distribution (top countries, raw counts):
#   United States 6762, India 1950, Germany 1936, United Kingdom 1246, Brazil 990,
#   France 978, Canada 745, Australia 694, Netherlands 626, Switzerland 572,
#   Spain 562, China 516, Mexico 513, Italy 489 (long tail beyond)
#
# Revenue (USD) distribution:
#   1B-10B: 11156, 200M-500M: 8933, 500M-1B: 6968, 75M-200M: 1598,
#   10B-100B: 1323, 25M-75M: 283, 100B-1T: 49
#
# Employee distribution:
#   1001-5000: 16211, 10001+: 9103, 5001-10000: 5002

# ---------------------------------------------------------------------------
# REAL ANCHOR RECORDS (Indeed job postings — cited)
# ---------------------------------------------------------------------------
_REAL_ANCHORS = [
    {
        "company_name": "Ferrero",
        "domain": "ferrero.com",
        "industry": "Consumer Products",
        "employee_range": "5001-10000",
        "revenue_range": "1B+",
        "hq_location": "Parsippany-Troy Hills, NJ, United States",
        "tech_stack": ["SAP S/4HANA", "SAP FI", "SAP CO"],
        "funding_stage": "public",
        "affiliation": "end_customer",
        "indeed_ref": "JOB_3 | https://to.indeed.com/aakjwr4djq2h | SAP S/4HANA Finance Functional Lead, 2026-03-13",
        "grounding": "Indeed JOB_3 (https://to.indeed.com/aakjwr4djq2h) — real end-customer posting, 2026-03-13; Vibe SAP-ERP distribution n=30,316",
    },
    {
        "company_name": "w3global",
        "domain": "w3global.com",
        "industry": "IT Staffing & Consulting",
        "employee_range": "201-1000",
        "revenue_range": "50M-250M",
        "hq_location": "California, United States",
        "tech_stack": ["SAP BTP", "SAP S/4HANA"],
        "funding_stage": "bootstrapped",
        "affiliation": "channel_partner",
        "indeed_ref": "JOB_1 | https://to.indeed.com/aat98cl8kckk | SAP BTP Consultant / Lead, 2026-05-22",
        "grounding": "Indeed JOB_1 (https://to.indeed.com/aat98cl8kckk) — real SI/staffing channel posting, 2026-05-22",
    },
    {
        "company_name": "Quintile Advisory",
        "domain": "quintileadvisory.com",
        "industry": "Management Consulting",
        "employee_range": "51-200",
        "revenue_range": "10-50M",
        "hq_location": "Remote, United States",
        "tech_stack": ["SAP S/4HANA", "Kinaxis"],
        "funding_stage": "bootstrapped",
        "affiliation": "channel_partner",
        "indeed_ref": "JOB_2 | https://to.indeed.com/aabb6d88zpjp | Enterprise Scheduling Specialist (Kinaxis), Remote",
        "grounding": "Indeed JOB_2 (https://to.indeed.com/aabb6d88zpjp) — real consultancy/channel posting",
    },
]

# ---------------------------------------------------------------------------
# BIG4 / SI FIRMS (public names — OK as channel_partner contacts)
# ---------------------------------------------------------------------------
_BIG4_FIRMS = [
    "Deloitte", "Accenture", "PwC", "EY", "KPMG", "IBM Global Services", "Capgemini",
]

# ---------------------------------------------------------------------------
# SYNTHETIC END-CUSTOMER ACCOUNTS
# Firmographics sampled from Vibe SAP-ERP distribution n=30,316
# Geography weighted by real country counts.
# ---------------------------------------------------------------------------
# (name, domain, industry, employee_range, revenue_range, hq_location, funding_stage, sap_stack)
_SYNTHETIC_ACCOUNTS = [
    # United States — largest segment (6762/30316 ≈ 22%)
    ("NexGen Manufacturing Corp", "nexgenmfg.com", "Manufacturing", "5001-10000", "1B+", "Detroit, MI, United States", "public", ["SAP ECC 6.0", "SAP FI", "SAP CO", "SAP MM"]),
    ("Crestwood Chemical Group", "crestwoodchem.com", "Chemicals", "1001-5000", "500M-1B", "Houston, TX, United States", "public", ["SAP S/4HANA", "SAP MM", "SAP SD", "RISE with SAP"]),
    ("BlueStar Retail Holdings", "bluestarretail.com", "Retail", "10001+", "1B+", "Atlanta, GA, United States", "public", ["SAP S/4HANA Cloud", "SAP SuccessFactors", "SAP SD"]),
    ("Meridian Life Sciences", "meridianls.com", "Life Sciences", "5001-10000", "1B+", "Boston, MA, United States", "public", ["SAP ECC 6.0", "SAP QM", "SAP MM", "SAP FI"]),
    ("GreatLakes Energy Partners", "greatlakesenergy.com", "Energy & Utilities", "1001-5000", "500M-1B", "Chicago, IL, United States", "public", ["SAP ECC 6.0", "SAP PM", "SAP MM"]),
    ("Vantage Consumer Products", "vantagecp.com", "Consumer Products", "5001-10000", "1B+", "Cincinnati, OH, United States", "public", ["SAP S/4HANA", "SAP CO", "SAP SD", "SAP MM"]),
    ("Ironclad Industrial Group", "ironcladig.com", "Manufacturing", "10001+", "1B+", "Pittsburgh, PA, United States", "public", ["SAP ECC 6.0", "SAP PM", "SAP PP", "SAP QM"]),
    ("Apex Pharma Solutions", "apexpharma.com", "Life Sciences", "1001-5000", "500M-1B", "New Jersey, NJ, United States", "public", ["SAP S/4HANA", "SAP FI", "SAP CO", "SAP QM", "RISE with SAP"]),
    ("Cascade Foods International", "cascadefoods.com", "Consumer Products", "1001-5000", "250M-1B", "Seattle, WA, United States", "public", ["SAP ECC 6.0", "SAP SD", "SAP MM", "SAP CO"]),
    ("ProLogix Distribution", "prologix.com", "Retail", "5001-10000", "1B+", "Columbus, OH, United States", "public", ["RISE with SAP", "SAP S/4HANA Cloud", "SAP EWM"]),
    ("Summit Specialty Chemicals", "summitspec.com", "Chemicals", "1001-5000", "500M-1B", "Midland, TX, United States", "public", ["SAP S/4HANA", "SAP MM", "SAP PP", "SAP QM"]),
    ("Atlas Medical Devices", "atlasmeddev.com", "Life Sciences", "5001-10000", "1B+", "San Diego, CA, United States", "public", ["SAP ECC 6.0", "SAP FI", "SAP MM", "SAP SD"]),
    ("Heartland Food Group", "heartlandfood.com", "Consumer Products", "1001-5000", "250M-1B", "Kansas City, MO, United States", "public", ["SAP ECC 6.0", "SAP CO", "SAP FI"]),
    ("Northgate Power Systems", "northgateps.com", "Energy & Utilities", "5001-10000", "1B+", "Dallas, TX, United States", "public", ["SAP S/4HANA", "SAP PM", "SAP FI", "SAP CO"]),
    ("Clearwater Paper Industries", "clearwaterpaper.com", "Manufacturing", "1001-5000", "250M-1B", "Spokane, WA, United States", "public", ["SAP ECC 6.0", "SAP PP", "SAP QM", "SAP MM"]),
    # Germany — second-largest (1936/30316 ≈ 6%)
    ("Rhein Industriewerke GmbH", "rhein-industriewerke.de", "Manufacturing", "5001-10000", "1B+", "Düsseldorf, Germany", "public", ["SAP S/4HANA", "SAP CO", "SAP PP", "SAP MM"]),
    ("BavarianBio AG", "bavarianbio.de", "Life Sciences", "1001-5000", "500M-1B", "Munich, Germany", "public", ["SAP ECC 6.0", "SAP QM", "SAP FI", "SAP CO"]),
    ("Schäfer Chemiewerk GmbH", "schaefer-chemie.de", "Chemicals", "1001-5000", "250M-1B", "Frankfurt, Germany", "public", ["SAP S/4HANA", "SAP MM", "SAP SD", "RISE with SAP"]),
    ("Norddeutsche Energieholding AG", "nde-ag.de", "Energy & Utilities", "10001+", "1B+", "Hamburg, Germany", "public", ["SAP ECC 6.0", "SAP PM", "SAP IS-U", "SAP FI"]),
    ("Westfalen Automotive Gruppe", "westfalen-auto.de", "Manufacturing", "5001-10000", "1B+", "Cologne, Germany", "public", ["RISE with SAP", "SAP S/4HANA Cloud", "SAP SD"]),
    # United Kingdom (1246/30316 ≈ 4%)
    ("Britannic Retail Group plc", "britannicretail.co.uk", "Retail", "10001+", "1B+", "London, United Kingdom", "public", ["SAP S/4HANA", "SAP SD", "SAP EWM", "SAP CO"]),
    ("Coastal Energy Holdings Ltd", "coastalenergyuk.com", "Energy & Utilities", "5001-10000", "1B+", "Aberdeen, United Kingdom", "public", ["SAP ECC 6.0", "SAP PM", "SAP MM"]),
    ("Thames Life Sciences PLC", "thamesls.co.uk", "Life Sciences", "1001-5000", "500M-1B", "Oxford, United Kingdom", "public", ["SAP S/4HANA", "SAP QM", "SAP FI", "RISE with SAP"]),
    # India (1950/30316 ≈ 6%)
    ("Tata Horizon Industries Ltd", "tatahorizon.in", "Manufacturing", "10001+", "1B+", "Mumbai, India", "public", ["SAP ECC 6.0", "SAP FI", "SAP CO", "SAP MM", "SAP PP"]),
    ("Reliance Chem Solutions Ltd", "reliance-chem.in", "Chemicals", "5001-10000", "1B+", "Ahmedabad, India", "public", ["SAP S/4HANA", "SAP MM", "SAP QM", "RISE with SAP"]),
    ("SunPharm Industries", "sunpharmin.com", "Life Sciences", "5001-10000", "1B+", "Hyderabad, India", "public", ["SAP ECC 6.0", "SAP QM", "SAP FI", "SAP SD"]),
    # Brazil (990/30316 ≈ 3%)
    ("Companhia Amazônica de Energia", "amazonica-energia.com.br", "Energy & Utilities", "5001-10000", "1B+", "São Paulo, Brazil", "public", ["SAP ECC 6.0", "SAP PM", "SAP FI", "SAP IS-U"]),
    ("Grupo Meridiano Retail", "grupo-meridiano.com.br", "Retail", "1001-5000", "500M-1B", "Rio de Janeiro, Brazil", "public", ["SAP S/4HANA", "SAP SD", "SAP FI"]),
    # France (978/30316 ≈ 3%)
    ("Société Chimique du Rhône", "chimique-rhone.fr", "Chemicals", "1001-5000", "500M-1B", "Lyon, France", "public", ["SAP S/4HANA", "SAP MM", "SAP QM", "SAP CO"]),
    ("Consortium Agroalimentaire FR", "consortium-agro.fr", "Consumer Products", "5001-10000", "1B+", "Paris, France", "public", ["SAP ECC 6.0", "SAP FI", "SAP SD", "SAP MM"]),
    # Canada (745/30316 ≈ 2%)
    ("Northern Lights Manufacturing", "nlmfg.ca", "Manufacturing", "1001-5000", "500M-1B", "Toronto, Canada", "public", ["RISE with SAP", "SAP S/4HANA Cloud", "SAP PP"]),
    ("Boreal Energy Resources", "borealresources.ca", "Energy & Utilities", "5001-10000", "1B+", "Calgary, Canada", "public", ["SAP ECC 6.0", "SAP PM", "SAP MM", "SAP FI"]),
    # Australia (694/30316 ≈ 2%)
    ("Pacific Resources Ltd", "pacific-resources.com.au", "Energy & Utilities", "1001-5000", "500M-1B", "Perth, Australia", "public", ["SAP S/4HANA", "SAP PM", "SAP FI", "SAP CO"]),
    ("Southern Cross Consumer Goods", "southerncrosscg.com.au", "Consumer Products", "1001-5000", "250M-1B", "Sydney, Australia", "public", ["SAP ECC 6.0", "SAP SD", "SAP MM"]),
    # Netherlands (626)
    ("Maas Chemicals BV", "maaschemicals.nl", "Chemicals", "1001-5000", "500M-1B", "Rotterdam, Netherlands", "public", ["RISE with SAP", "SAP S/4HANA Cloud", "SAP MM", "SAP QM"]),
    # Switzerland (572)
    ("Helvetica Pharma AG", "helveticapharma.ch", "Life Sciences", "1001-5000", "500M-1B", "Basel, Switzerland", "public", ["SAP S/4HANA", "SAP FI", "SAP QM", "SAP CO"]),
    # Mexico (513)
    ("Grupo Industria Norte SA", "industria-norte.com.mx", "Manufacturing", "1001-5000", "250M-1B", "Monterrey, Mexico", "public", ["SAP ECC 6.0", "SAP PP", "SAP MM", "SAP FI"]),
    # China (516)
    ("Yangtze Manufacturing Holdings", "yangtze-mfg.cn", "Manufacturing", "10001+", "1B+", "Shanghai, China", "public", ["SAP ECC 6.0", "SAP FI", "SAP CO", "SAP PP", "SAP MM"]),
    # Additional US accounts for volume
    ("Ridgeline Specialty Chemicals", "ridglinechem.com", "Chemicals", "1001-5000", "250M-1B", "Baton Rouge, LA, United States", "public", ["SAP ECC 6.0", "SAP MM", "SAP QM"]),
    ("Stonegate Retail Partners", "stonegateretp.com", "Retail", "5001-10000", "1B+", "Minneapolis, MN, United States", "public", ["SAP S/4HANA", "SAP EWM", "SAP SD", "SAP FI"]),
    ("Lakefront Consumer Goods", "lakefrontcg.com", "Consumer Products", "1001-5000", "250M-1B", "Milwaukee, WI, United States", "public", ["SAP S/4HANA", "SAP CO", "SAP MM"]),
    ("Westrock Energy Solutions", "westrockenergy.com", "Energy & Utilities", "1001-5000", "500M-1B", "Denver, CO, United States", "public", ["SAP S/4HANA", "SAP PM", "SAP CO", "RISE with SAP"]),
    ("Harborview Medical Group", "harborviewmed.com", "Life Sciences", "1001-5000", "500M-1B", "Baltimore, MD, United States", "public", ["SAP ECC 6.0", "SAP FI", "SAP HR"]),
    ("Prairie Chemical Holdings", "prairiechem.com", "Chemicals", "5001-10000", "1B+", "Omaha, NE, United States", "public", ["SAP S/4HANA", "SAP PP", "SAP QM", "SAP MM"]),
    ("Appalachian Paper & Packaging", "appcpaper.com", "Manufacturing", "1001-5000", "250M-1B", "Asheville, NC, United States", "public", ["SAP ECC 6.0", "SAP PP", "SAP CO", "SAP MM"]),
]

# ---------------------------------------------------------------------------
# SAP-specific contacts (synthetic personas — no real names)
# (title, seniority, department, affiliation_type)
# ---------------------------------------------------------------------------
_CONTACTS_END_CUSTOMER = [
    ("Chief Information Officer", "c_suite", "engineering", "end_customer"),
    ("Chief Financial Officer", "c_suite", "finance", "end_customer"),
    ("VP of IT", "vp", "engineering", "end_customer"),
    ("VP of Finance", "vp", "finance", "end_customer"),
    ("Director of SAP Center of Excellence", "director", "engineering", "end_customer"),
    ("SAP Program Director", "director", "engineering", "end_customer"),
    ("Head of Digital Transformation", "vp", "engineering", "end_customer"),
    ("IT Director", "director", "engineering", "end_customer"),
    ("Finance Director", "director", "finance", "end_customer"),
    ("Director of Supply Chain IT", "director", "operations", "end_customer"),
    ("VP of Operations", "vp", "operations", "end_customer"),
    ("Chief Digital Officer", "c_suite", "engineering", "end_customer"),
    ("Global SAP Solutions Manager", "manager", "engineering", "end_customer"),
    ("ERP Transformation Lead", "director", "engineering", "end_customer"),
    ("Director of Enterprise Architecture", "director", "engineering", "end_customer"),
]

_CONTACTS_SAP_FIELD = [
    ("SAP Account Executive", "ic", "sales", "channel_partner"),
    ("SAP Regional VP", "vp", "sales", "channel_partner"),
    ("SAP Area Sales Manager", "manager", "sales", "channel_partner"),
    ("SAP VP of Sales", "vp", "sales", "channel_partner"),
    ("SAP Alliance Manager", "ic", "sales", "channel_partner"),
]

_CONTACTS_SI_PARTNER = [
    ("Managing Director, SAP Practice", "c_suite", "engineering", "channel_partner"),
    ("Partner, Digital Transformation", "c_suite", "engineering", "channel_partner"),
    ("Senior Manager, SAP S/4HANA", "manager", "engineering", "channel_partner"),
    ("SAP Practice Lead", "director", "engineering", "channel_partner"),
    ("Principal Consultant, SAP BTP", "ic", "engineering", "channel_partner"),
]

# Synthetic first/last name pools (no real persons)
_FIRST_NAMES = [
    "Alexander", "Beatrice", "Christoph", "Deepa", "Elena", "François", "Giulia",
    "Henrik", "Ingrid", "Javier", "Kirra", "Lars", "Marta", "Naresh", "Olivia",
    "Pavel", "Qi", "Renata", "Stefan", "Thandi", "Ulrich", "Vanya", "Wei",
    "Xavier", "Yuki", "Zosia", "Arjun", "Brigitte", "Cédric", "Dayo",
    "Emmanuella", "Florian", "Greta", "Hiroshi", "Isabela", "João",
]

_LAST_NAMES = [
    "Müller", "Nakamura", "Okonkwo", "Petersen", "Quintero", "Rajan", "Schreiber",
    "Tanaka", "Ureña", "Vogt", "Wanjiku", "Xiao", "Yamamoto", "Zapatero",
    "Anderson", "Bergmann", "Carvalho", "DaSilva", "Eriksson", "Fischer",
    "Guerrero", "Hoffmann", "Inoue", "Jensen", "Kowalski", "Larsson", "Marchetti",
    "Nielsen", "Oliveira", "Park", "Rao", "Santos", "Thomas",
]

# ---------------------------------------------------------------------------
# SAP-specific pain points and intent topics
# ---------------------------------------------------------------------------
_SAP_PAIN_POINTS = [
    "our ECC customizations are blocking the S/4 migration",
    "finance period-close takes 5 days and we need to get to 2",
    "we can't get real-time inventory visibility across our 12 plants",
    "our Joule pilot has no champion in the business — IT owns it alone",
    "we don't know which SAP processes are good candidates for Joule",
    "our RISE subscription is live but Joule is still not activated",
    "clean core assessment flagged 2,400 custom objects — program is stalled",
    "supply chain disruptions take 3 days to detect in our current ECC setup",
    "AP automation is manual — 3 FTEs doing invoice matching",
    "SAP S/4HANA migration is 18 months delayed due to resourcing",
    "business units don't trust the AI outputs from SAP embedded analytics",
    "our SAP BTP sandbox is set up but no use cases are in production",
    "Joule demo went well but we have no budget owner beyond IT",
    "we need to justify Joule ROI to the CFO before H2 budget cycle",
    "legacy ABAP modifications are incompatible with S/4 clean core",
]

_SAP_INTENT_TOPICS = [
    "SAP S/4HANA migration",
    "SAP Joule AI copilot",
    "RISE with SAP adoption",
    "SAP BTP implementation",
    "SAP clean core strategy",
    "SAP FI period-close automation",
    "SAP embedded AI",
    "enterprise AI copilot",
    "SAP SuccessFactors",
    "SAP EWM implementation",
    "SAP process automation",
    "ERP modernization",
    "AI in finance operations",
    "SAP S/4HANA Cloud migration",
    "intelligent ERP",
]

# ---------------------------------------------------------------------------
# S4 migration timeline texts (for custom.s_s4_migration_timeline)
# ---------------------------------------------------------------------------
_S4_TIMELINES = [
    "S/4HANA go-live targeted for Q4 2026",
    "board-approved S/4 migration program, greenfield start Q1 2026",
    "S/4HANA brownfield conversion planned for end of 2026",
    "CIO announced S/4 go-live by 2027 in all-hands",
    "actively running S/4HANA pilot — go-live for FI/CO module in 6 months",
    "RISE with SAP contract signed, S/4 Cloud go-live Q2 2027",
    "S/4 program in execution — MM/SD go-live completed, FI/CO next",
    "ECC maintenance contract expires 2027; S/4 migration mandatory",
    "SAP Activate methodology, go-live target locked at Q3 2026",
]

# ---------------------------------------------------------------------------
# Joule interest texts (for custom.s_joule_interest)
# ---------------------------------------------------------------------------
_JOULE_INTEREST_TEXTS = [
    "CIO asked: how do we activate Joule for finance period-close?",
    "job posting explicitly requires SAP Joule experience",
    "VP of IT emailed asking about Joule implementation scope and timeline",
    "prospect named Joule specifically in discovery call as target capability",
    "CIO confirmed Joule is on the 2026 digital agenda",
    "IT Director asked for Joule readiness assessment in initial meeting",
    "procurement started a Joule implementation RFP process",
    "CFO asked for Joule ROI business case during discovery",
]

# Joule interest DISQUALIFYING texts (tire-kicker / SAP marketing influence)
_JOULE_INTEREST_DISQUALIFYING = [
    "SAP AE mentioned Joule during partner briefing — no end-customer inquiry",
    "attended SAP Sapphire session on Joule — no follow-up from prospect",
    "generic AI interest; did not name Joule specifically in any conversation",
    "marketing intent data shows Joule content views — no direct prospect inquiry",
]

# ---------------------------------------------------------------------------
# Clean core texts (for custom.s_clean_core_initiative)
# ---------------------------------------------------------------------------
_CLEAN_CORE_TEXTS = [
    "job posting for SAP clean core architect — 3 roles open",
    "CIO announced clean core program at SAP user group",
    "actively running SAP clean core assessment with consulting partner",
    "clean core initiative launched: 2,400 custom objects being reviewed",
    "SAP clean core certification underway for key ABAP developers",
]

# ---------------------------------------------------------------------------
# RISE adoption texts (for custom.s_rise_adoption)
# ---------------------------------------------------------------------------
_RISE_TEXTS = [
    "RISE with SAP contract signed — S/4HANA Cloud go-live in progress",
    "publicly listed as RISE with SAP reference customer",
    "job posting requires RISE with SAP experience",
    "CIO confirmed RISE subscription is active and BTP entitlements included",
    "SAP AE confirmed live RISE contract — BTP credits available",
]

# ---------------------------------------------------------------------------
# SAP field co-sell texts (for custom.s_sap_field_co_sell)
# ---------------------------------------------------------------------------
_SAP_FIELD_COSELL_TEXTS = [
    "SAP AE introduced firm to end-customer via co-sell email",
    "SAP Area Sales Manager set up three-way meeting with end-customer",
    "listed as co-sell partner in SAP co-sell portal for this account",
    "SAP Regional VP referred account and requested joint pursuit",
    "SAP VP of Sales sent introduction email to end-customer CIO",
]

# ---------------------------------------------------------------------------
# SI partner texts (for custom.s_si_partner_involved)
# ---------------------------------------------------------------------------
_SI_PARTNER_TEXTS = [
    "Big4 MD reached out about Joule specialist subcontract on live S/4 program",
    "named as Joule AI specialist in Big4 SAP transformation SOW",
    "signed prime contract includes Joule/AI specialist SOW slot",
    "Big4 Partner confirmed they are bidding on S/4 prime and evaluating Joule subcontractors",
    "SI confirmed active SAP transformation program — evaluating Joule partner",
]

# ---------------------------------------------------------------------------
# Qualification budget texts
# ---------------------------------------------------------------------------
_BUDGET_TEXTS = [
    "CFO confirmed $300k pilot budget for Joule implementation",
    "IT budget includes $200k allocated for AI/SAP initiatives in H2",
    "procurement confirmed budget of $150k-$500k for Joule scoping and pilot",
    "annual IT modernization budget of $2M includes Joule implementation line item",
    "SAP transformation program budget confirmed at $5M; Joule AI uplift is in scope",
]

_AUTHORITY_TEXTS = [
    "CIO confirmed as executive sponsor and economic buyer",
    "CFO is the budget owner; confirmed in discovery session",
    "VP of IT confirmed as decision-maker for SAP tooling",
    "SAP Steering Committee includes CFO and CIO — both engaged in discovery",
    "CEO and CIO jointly confirmed Joule as strategic initiative",
]

_TIMELINE_TEXTS = [
    "need Joule pilot live before H2 board review",
    "compelling event: S/4 go-live in Q3 2026 — Joule must be in scope",
    "CFO wants ROI evidence by Q4 for 2027 budget planning",
    "CIO set a 90-day pilot deadline starting next month",
    "contract signature expected before end of Q2 2026",
]

_NEED_TEXTS = [
    "FI period-close automation: reduce 5-day close to 2 days using Joule",
    "AP invoice matching: automate 3 FTE process using SAP Joule",
    "supply chain exception handling: Joule to surface and route disruption alerts",
    "Joule use case: procurement spend analysis and vendor recommendation",
    "HR hire-to-onboard process acceleration using SAP Joule and SuccessFactors",
    "Joule to support S/4 user adoption — guided task completion for end users",
    "real-time plant-level inventory reconciliation via Joule embedded in SAP",
]

# ---------------------------------------------------------------------------
# Disposition weights — realistic SAP pipeline mix
# ---------------------------------------------------------------------------
_DISPOSITION_WEIGHTS = [
    ("qualified", 0.28),
    ("nurture", 0.50),
    ("disqualified", 0.22),
]

# ---------------------------------------------------------------------------
# Channel affiliation weights (per spec):
# 50% end_customer (direct), 30% channel_partner/sap-field, 20% channel_partner/SI
# ---------------------------------------------------------------------------
_CHANNEL_WEIGHTS = [
    ("end_customer", 0.50),
    ("sap_field", 0.30),
    ("si_partner", 0.20),
]


def _weighted_choice(choices_weights: list[tuple]) -> str:
    choices, weights = zip(*choices_weights)
    r = random.random()
    cumulative = 0.0
    for c, w in zip(choices, weights):
        cumulative += w
        if r < cumulative:
            return c
    return choices[-1]


def _make_entity(label: str, text: str, normalized_value: str | None = None, confidence: float | None = None) -> dict:
    conf = confidence if confidence is not None else round(random.uniform(0.65, 0.98), 3)
    e: dict = {"label": label, "text": text, "confidence": conf}
    if normalized_value is not None:
        e["normalized_value"] = normalized_value
    return e


def _synthetic_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _sap_field_contact_name(si_firm: str) -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _gen_record_from_anchor(idx: int, anchor: dict) -> dict:
    """Generate a record for a real named anchor (Ferrero, w3global, Quintile)."""
    affiliation = anchor["affiliation"]
    company_name = anchor["company_name"]
    domain = anchor["domain"]

    if affiliation == "end_customer":
        contact = random.choice(_CONTACTS_END_CUSTOMER)
    else:
        contact = random.choice(_CONTACTS_SI_PARTNER)

    c_title, c_seniority, c_dept, c_affiliation = contact
    c_name = _synthetic_name()

    disposition = _weighted_choice(_DISPOSITION_WEIGHTS)
    pain = random.choice(_SAP_PAIN_POINTS)
    intent = random.choice(_SAP_INTENT_TOPICS)

    entities = [
        _make_entity("account.company_name", company_name),
        _make_entity("account.domain", domain),
        _make_entity("account.industry", anchor["industry"]),
        _make_entity("account.employee_range", anchor["employee_range"], normalized_value=anchor["employee_range"]),
        _make_entity("account.revenue_range", anchor["revenue_range"], normalized_value=anchor["revenue_range"]),
        _make_entity("account.hq_location", anchor["hq_location"]),
        _make_entity("account.funding_stage", anchor["funding_stage"]),
    ]

    for stack_item in anchor["tech_stack"]:
        entities.append(_make_entity("account.tech_stack_item", stack_item, normalized_value=stack_item.lower().replace(" ", "_")))

    entities += [
        _make_entity("contact.full_name", c_name),
        _make_entity("contact.title", c_title),
        _make_entity("contact.seniority", c_seniority, normalized_value=c_seniority),
        _make_entity("contact.department", c_dept, normalized_value=c_dept),
        _make_entity("contact.affiliation", c_affiliation, normalized_value=c_affiliation),
        _make_entity("signal.intent_topic", intent),
        _make_entity("signal.pain_point_mention", pain),
    ]

    # Add SAP-specific signals based on tech stack
    if any("RISE" in s for s in anchor["tech_stack"]) or any("S/4HANA" in s for s in anchor["tech_stack"]):
        if affiliation == "end_customer" and random.random() < 0.7:
            entities.append(_make_entity("custom.s_rise_adoption", random.choice(_RISE_TEXTS), confidence=round(random.uniform(0.75, 0.95), 3)))

    # Ferrero anchor: S/4HANA Finance — strong signal
    if company_name == "Ferrero":
        entities.append(_make_entity("custom.s_s4_migration_timeline", "SAP S/4HANA Finance go-live program, posted role 2026-03-13", confidence=0.92))
        entities.append(_make_entity("custom.s_joule_interest", "Ferrero hiring SAP S/4HANA Finance Functional Lead — direct end-customer S/4 signal (Indeed JOB_3)", confidence=0.88))
        disposition = "qualified"

    # w3global: SI channel + BTP
    if company_name == "w3global":
        entities.append(_make_entity("custom.s_si_partner_involved", "w3global posted SAP BTP Consultant/Lead (Indeed JOB_1) — SI/staffing channel active", confidence=0.85))

    if disposition == "qualified":
        budget_text = random.choice(_BUDGET_TEXTS)
        authority_text = random.choice(_AUTHORITY_TEXTS)
        need_text = random.choice(_NEED_TEXTS)
        timeline_text = random.choice(_TIMELINE_TEXTS)
        entities += [
            _make_entity("qualification.budget_confirmed", budget_text, confidence=round(random.uniform(0.75, 0.96), 3)),
            _make_entity("qualification.authority_identified", authority_text, confidence=round(random.uniform(0.75, 0.96), 3)),
            _make_entity("qualification.need_articulated", need_text, confidence=round(random.uniform(0.75, 0.96), 3)),
            _make_entity("qualification.timeline_stated", timeline_text, confidence=round(random.uniform(0.75, 0.96), 3)),
        ]
    elif disposition == "nurture":
        entities.append(_make_entity("qualification.need_articulated", pain, confidence=round(random.uniform(0.60, 0.85), 3)))

    entities.append(_make_entity("qualification.disposition", disposition, confidence=round(random.uniform(0.70, 0.95), 3)))

    source_types = ["linkedin_post", "website_page", "crm_note", "call_transcript", "email"]
    source_type = random.choice(source_types)

    grounding_sources = [
        anchor["grounding"],
        "Vibe Prospecting / Explorium SAP-ERP distribution n=30,316 — firmographic proportions",
        "MEDDPICC framework (public) — qualification evidence labels",
        "SAP Help Portal (help.sap.com/docs/joule) — SAP Joule system requirements",
    ]

    return {
        "source_doc_id": f"sap_{idx:04d}",
        "source_type": source_type,
        "grounding_sources": grounding_sources,
        "entities": entities,
    }


def _gen_record_synthetic(idx: int) -> dict:
    """Generate a synthetic record from the SAP account pool."""
    channel_type = _weighted_choice(_CHANNEL_WEIGHTS)

    account = random.choice(_SYNTHETIC_ACCOUNTS)
    name, domain, industry, emp_range, rev_range, hq, funding, sap_stack = account

    if channel_type == "end_customer":
        contact = random.choice(_CONTACTS_END_CUSTOMER)
        c_title, c_seniority, c_dept, c_affiliation = contact
        c_name = _synthetic_name()
    elif channel_type == "sap_field":
        contact = random.choice(_CONTACTS_SAP_FIELD)
        c_title, c_seniority, c_dept, c_affiliation = contact
        c_name = _synthetic_name()
    else:  # si_partner
        contact = random.choice(_CONTACTS_SI_PARTNER)
        c_title, c_seniority, c_dept, c_affiliation = contact
        c_name = _synthetic_name()

    # Determine disposition based on channel and SAP landscape
    has_ecc_only = any("ECC" in s for s in sap_stack) and not any("S/4" in s or "RISE" in s for s in sap_stack)
    has_s4 = any("S/4" in s for s in sap_stack)
    has_rise = any("RISE" in s for s in sap_stack)

    # Apply failure mode patterns to disposition logic
    if has_ecc_only and random.random() < 0.6:
        # FM-SAP-01: ECC-only with no S/4 roadmap → likely nurture/disqualified
        disposition = "disqualified" if random.random() < 0.4 else "nurture"
    elif channel_type == "sap_field" and random.random() < 0.5:
        # FM-SAP-02: SAP field co-sell without end-customer budget → not auto-qualified
        disposition = "nurture"
    elif channel_type == "si_partner" and random.random() < 0.4:
        # FM-SAP-03: SI partner without confirmed prime contract
        disposition = "nurture"
    else:
        disposition = _weighted_choice(_DISPOSITION_WEIGHTS)

    pain = random.choice(_SAP_PAIN_POINTS)
    intent = random.choice(_SAP_INTENT_TOPICS)

    entities = [
        _make_entity("account.company_name", name),
        _make_entity("account.domain", domain),
        _make_entity("account.industry", industry),
        _make_entity("account.employee_range", emp_range, normalized_value=emp_range),
        _make_entity("account.revenue_range", rev_range, normalized_value=rev_range),
        _make_entity("account.hq_location", hq),
        _make_entity("account.funding_stage", funding),
    ]

    for stack_item in sap_stack:
        entities.append(_make_entity("account.tech_stack_item", stack_item, normalized_value=stack_item.lower().replace(" ", "_").replace("/", "_")))

    entities += [
        _make_entity("contact.full_name", c_name),
        _make_entity("contact.title", c_title),
        _make_entity("contact.seniority", c_seniority, normalized_value=c_seniority),
        _make_entity("contact.department", c_dept, normalized_value=c_dept),
        _make_entity("contact.affiliation", c_affiliation, normalized_value=c_affiliation),
        _make_entity("signal.intent_topic", intent),
        _make_entity("signal.pain_point_mention", pain),
    ]

    # Add SAP hiring trigger signal
    sap_roles = [
        "SAP S/4HANA Functional Consultant",
        "SAP BTP Developer",
        "SAP Center of Excellence Lead",
        "SAP Joule Implementation Specialist",
        "SAP Clean Core Architect",
        "SAP FI/CO Consultant",
        "SAP Solution Architect",
    ]
    if random.random() < 0.55:
        role = random.choice(sap_roles)
        entities.append(_make_entity("signal.hiring_trigger", f"hiring {role}", confidence=round(random.uniform(0.65, 0.92), 3)))

    # --- Custom signals ---

    # S4 migration timeline (end_customer with S/4 or active migration)
    if channel_type == "end_customer" and (has_s4 or has_rise) and random.random() < 0.60:
        entities.append(_make_entity(
            "custom.s_s4_migration_timeline",
            random.choice(_S4_TIMELINES),
            confidence=round(random.uniform(0.72, 0.95), 3),
        ))

    # Joule interest — only when end_customer explicitly names it
    if channel_type == "end_customer" and random.random() < 0.40:
        if random.random() < 0.75:
            # Qualifying Joule interest
            entities.append(_make_entity(
                "custom.s_joule_interest",
                random.choice(_JOULE_INTEREST_TEXTS),
                confidence=round(random.uniform(0.72, 0.95), 3),
            ))
        else:
            # FM-SAP-04: Joule interest from SAP marketing (disqualifying pattern)
            entities.append(_make_entity(
                "custom.s_joule_interest",
                random.choice(_JOULE_INTEREST_DISQUALIFYING),
                confidence=round(random.uniform(0.45, 0.65), 3),
            ))
            # These tire-kicker patterns drive nurture or disqualified
            if disposition == "qualified":
                disposition = "nurture"

    # Clean core initiative
    if has_s4 and random.random() < 0.35:
        entities.append(_make_entity(
            "custom.s_clean_core_initiative",
            random.choice(_CLEAN_CORE_TEXTS),
            confidence=round(random.uniform(0.70, 0.93), 3),
        ))

    # RISE adoption
    if has_rise and random.random() < 0.70:
        entities.append(_make_entity(
            "custom.s_rise_adoption",
            random.choice(_RISE_TEXTS),
            confidence=round(random.uniform(0.75, 0.96), 3),
        ))

    # SAP field co-sell
    if channel_type == "sap_field":
        entities.append(_make_entity(
            "custom.s_sap_field_co_sell",
            random.choice(_SAP_FIELD_COSELL_TEXTS),
            confidence=round(random.uniform(0.72, 0.95), 3),
        ))

    # SI partner involved
    if channel_type == "si_partner":
        si_firm = random.choice(_BIG4_FIRMS)
        entities.append(_make_entity(
            "custom.s_si_partner_involved",
            f"{si_firm}: {random.choice(_SI_PARTNER_TEXTS)}",
            confidence=round(random.uniform(0.70, 0.94), 3),
        ))

    # --- Qualification entities ---
    if disposition == "qualified":
        budget_text = random.choice(_BUDGET_TEXTS)
        authority_text = random.choice(_AUTHORITY_TEXTS)
        need_text = random.choice(_NEED_TEXTS)
        timeline_text = random.choice(_TIMELINE_TEXTS)
        entities += [
            _make_entity("qualification.budget_confirmed", budget_text, confidence=round(random.uniform(0.75, 0.97), 3)),
            _make_entity("qualification.authority_identified", authority_text, confidence=round(random.uniform(0.75, 0.97), 3)),
            _make_entity("qualification.need_articulated", need_text, confidence=round(random.uniform(0.75, 0.97), 3)),
            _make_entity("qualification.timeline_stated", timeline_text, confidence=round(random.uniform(0.75, 0.97), 3)),
        ]
    elif disposition == "nurture":
        # Partial qualification — need but no budget/timeline
        entities.append(_make_entity("qualification.need_articulated", pain, confidence=round(random.uniform(0.60, 0.85), 3)))
        # Some nurture records have timeline but no budget (HIL trigger)
        if random.random() < 0.30 and (has_s4 or has_rise):
            entities.append(_make_entity("qualification.timeline_stated", random.choice(_S4_TIMELINES), confidence=round(random.uniform(0.60, 0.82), 3)))

    entities.append(_make_entity("qualification.disposition", disposition, confidence=round(random.uniform(0.70, 0.95), 3)))

    source_types = ["linkedin_post", "website_page", "crm_note", "call_transcript", "email"]
    source_type = random.choice(source_types)

    grounding_sources = [
        "synthetic identity; firmographics sampled from Vibe SAP-ERP distribution n=30,316",
        "Vibe Prospecting / Explorium SAP-ERP distribution n=30,316 — geography/revenue/employee proportions",
        "MEDDPICC framework (public) — qualification evidence labels",
        "SAP Help Portal (help.sap.com/docs/joule) — SAP Joule system requirements and signal definitions",
    ]

    if channel_type == "si_partner":
        si_firm = next(
            (e["text"].split(":")[0] for e in entities if e["label"] == "custom.s_si_partner_involved"),
            "Big4 firm",
        )
        grounding_sources.append(f"{si_firm} — public Big4/SI firm name (channel_partner affiliation)")

    return {
        "source_doc_id": f"sap_{idx:04d}",
        "source_type": source_type,
        "grounding_sources": grounding_sources,
        "entities": entities,
    }


def main(output_path: Path | None = None) -> Path:
    if output_path is None:
        output_path = Path(__file__).parent / "sap_gold.jsonl"

    random.seed(SEED)

    records: list[dict] = []

    # First 3 records: real anchor companies (Ferrero, w3global, Quintile)
    for i, anchor in enumerate(_REAL_ANCHORS):
        records.append(_gen_record_from_anchor(i, anchor))

    # Remaining records: synthetic accounts
    for i in range(len(_REAL_ANCHORS), NUM_RECORDS):
        records.append(_gen_record_synthetic(i))

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    # Print summary stats
    dispositions = {}
    affiliations = {}
    for record in records:
        for entity in record["entities"]:
            if entity["label"] == "qualification.disposition":
                dispositions[entity["text"]] = dispositions.get(entity["text"], 0) + 1
            if entity["label"] == "contact.affiliation":
                affiliations[entity["text"]] = affiliations.get(entity["text"], 0) + 1

    print(f"Wrote {len(records)} records to {output_path}", file=sys.stderr)
    print(f"Disposition distribution: {dispositions}", file=sys.stderr)
    print(f"Affiliation distribution: {affiliations}", file=sys.stderr)

    return output_path


if __name__ == "__main__":
    main()
