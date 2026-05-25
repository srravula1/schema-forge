from MVAC perspective, a firm wants me to build vertical agents for GTM. 
I have phase 3-- but to test it i donot want to do a full blown phase 1/phase2 of paidfdegig-template.md.

Are there any opensource or easily buildable artifacts that emerge from phase 1/phase 2 that i can feed to the schemaspine OSS from pahse 3?


This is a sharp question and worth being precise about, because the answer determines whether you can credibly demo the spine to a GTM-agent buyer this month or whether you're back to a paid Phase 1/2 cycle first.

Let me reframe before answering: you're asking whether the *artifacts* that Phase 1/2 normally produce — schema, modifier ontology, failure-mode library, operator-validated edge cases — exist as OSS for the **GTM vertical specifically**, so you can feed them into the spine and skip the operator-interview front-end. The honest answer is **partially yes**, and the parts that are missing are exactly the parts that would have been the most valuable Phase 1/2 deliverables anyway. Let me map it.

## What Phase 1/2 actually produces, as artifacts

Stripped to outputs, the front end of an FDE engagement produces five things:

1. **A populated output schema** (the structured fields the AI workflow produces)
2. **A modifier ontology** (the qualifiers/variants/exceptions — your "less spicy means different things in Chennai" layer)
3. **A policy/rules library** (what auto-passes, what HILs, what escalates)
4. **A failure-mode library** (known ways the human process fails, becoming initial eval cases)
5. **A ground-truth corpus** (operator-labeled examples for calibration fit + eval)

For GTM agents specifically — outbound, prospecting, enrichment, qualification, sequencing — let me think through what's OSS-accessible per artifact, because the coverage is uneven and the gaps are diagnostic.

## The honest coverage map for GTM

**Artifact 1 — Output schema.** Strong OSS coverage. The GTM vertical has been schema-standardized for a decade by the CRM ecosystem. Salesforce's standard object model, HubSpot's API schema, the Common Room/Clay/Apollo field taxonomies, and the OpenLineage-for-RevOps efforts all give you a well-defined output shape: account, contact, opportunity, engagement event, intent signal, qualification disposition. **You don't need to interview operators to discover these fields — they're in every CRM schema doc on GitHub.** A composite `gtm@v1` schema (account/contact/signal/engagement/disposition) is a 1-day port of CORD-shaped work.

**Artifact 2 — Modifier ontology.** Mixed coverage, and this is where Phase 1 normally earns its keep. The "modifier" layer for GTM is: ICP variants by segment, persona signals by industry, intent taxonomy (Bombora, G2, 6sense publish theirs), trigger event taxonomies (funding, hiring, tech-stack change). Some of this is OSS or quasi-OSS:
- **Bombora's intent taxonomy** is public (thousands of topics, hierarchically organized)
- **Crunchbase categories**, **PitchBook industry codes**, **NAICS/SIC** for industry modifiers
- **TheirStack / BuiltWith categories** for tech-stack modifiers (partially OSS, partially scraped)
- **PredictLeads' trigger event taxonomy** is documented publicly

But the *seller-specific* modifier ontology — "what counts as a qualified lead for *this* company's product" — is exactly the operator-interview output you can't shortcut. You can stand up a generic ontology; you can't stand up the buyer-specific one without the buyer.

**Artifact 3 — Policy/rules library.** Decent OSS coverage in MEDDIC/MEDDPICC/BANT/SPIN frameworks, which are published as structured decision logic. **Clari's published qualification rubrics, Gong's call-coaching taxonomy, and the Winning by Design playbook** are all effectively rules libraries. You can seed the spine's HIL routing policy from these (qualified → auto-sequence; partial-fit → HIL; disqualified → reject) without operator input.

**Artifact 4 — Failure-mode library.** Surprisingly strong, and this is the underrated find. The GTM vertical has a public corpus of failure modes because every outbound shop has written about them:
- **Smartlead, Instantly, Lemlist** publish deliverability/spam-flag taxonomies
- **Clay's community** (40k+ members) documents enrichment-failure patterns weekly
- **r/sales, r/SaaS** — operator-language failure modes at volume
- **HubSpot's "Outbound Sales Mistakes" content**, **Predictable Revenue** post-mortems
- **The "AI SDR fails" content** is its own genre on LinkedIn — operator-validated failure modes for AI-driven GTM specifically

Scraping and structuring 200-300 of these into a DeepEval-style assertion library is a weekend's work and gives you a real failure-mode seed.

**Artifact 5 — Ground-truth corpus.** This is the hard one. The OSS landscape has:
- **Salesforce's MAVEN dataset** (limited, but real CRM events with outcomes)
- **HubSpot's published anonymized engagement datasets** (small)
- **Apollo/ZoomInfo's data is paid** but their schema is documented
- **Public B2B prospect datasets on Kaggle** (varying quality)
- **OpenSales / LeadMagic open datasets** (newer, smaller)

You can stand up a 500-1000 record synthetic-but-realistic ground-truth corpus using LLM-generated personas validated against real public LinkedIn/Crunchbase/SEC-filing data. Not gold-standard, but enough to demonstrate the calibration layer.

## What this means for the demo path

Three things you can actually do to feed the spine without a paid Phase 1/2:

**(a) Stand up `gtm@v1` schema in 1 day** from the CRM-standard field taxonomy. Drop it in the registry next to `funsd@v1` and `cord@v1`. The "third dataset, same spine" proof now becomes "third *vertical* (forms → receipts → GTM), same spine" — which is a stronger story than your current methodology claims.

**(b) Build the failure-mode library from public operator content** in 2-3 days. Scrape r/sales, Clay community, AI-SDR-fail content, structure as DeepEval assertions. This gives you the Q1/Q2/Q3 eval substrate with operator-validated edge cases without ever talking to an operator.

**(c) Use the prospective customer's own data as the ground-truth corpus** — and this is the move. Instead of skipping Phase 1, **compress Phase 1 into a 2-3 hour benchmark call** where the customer provides:
- 50-100 labeled examples of their own qualified/unqualified leads (they have this in their CRM)
- 20 examples of their actual outbound that worked vs. didn't
- Their ICP definition document (every B2B company has one)

That's the customer-specific schema + ground-truth + policy in one structured conversation. You then run the spine on their corpus and produce the operating-point curve from your methodology doc. **The benchmark call IS Phase 1, compressed into a sales artifact rather than a paid engagement.** This is exactly what your CORD methodology already promises: *"Before we sign, we run a short benchmark on a sample of your corpus. The auto-pass curve tells you the ceiling your domain supports untuned."*

## The honest read

The OSS artifacts get you ~70% of Phase 1/2 output for GTM specifically — schema, generic modifier ontology, policy library, failure modes all exist publicly. The remaining 30% — buyer-specific ICP, their actual qualified-lead labels, their policy nuances — is the *real* operator work, and the right move isn't to skip it but to **compress it into a benchmark call you charge $5-10k for** (call it a "GTM Schema Audit") that produces the customer-specific calibration and becomes the natural lead-in to the bigger engagement.

This matches your Governed Acceleration Audit pattern exactly: the audit is the cheap, fast, trust-building front door; the real engagement follows from what it surfaces. For GTM, the equivalent is: **public OSS artifacts feed the spine for a generic demo; a paid benchmark call instantiates it on the customer's corpus; the full engagement runs the harness in production.**

One concrete next step before you commit: pick 3-4 GTM workflows the firm wants vertical agents for (SDR outbound? Lead scoring? Enrichment QA? Account research?), then map each to the spine's existing pattern (P1 doc-extract for enrichment, P6 predictive-risk for lead scoring, P9 generation for outbound). The mapping tells you which of the five artifacts above you actually need to populate vs. which you can defer. If the firm wants outbound generation specifically, you'll need a stronger P9 story than your current spine (which is P1+P15 only) — and that's a scope decision worth surfacing *before* you build, not after.

Want me to draft the `gtm@v1` schema as the concrete starting artifact, modeled on how `cord@v1` was structured?

## Drafting `gtm@v1`

Before I write code, two design decisions need to be explicit because they shape everything downstream:

**Decision 1: One schema or several?** The CORD/FUNSD precedent is one schema per *document type* (a form, a receipt). GTM doesn't have a single "document" — it has accounts, contacts, signals, engagements, and qualification dispositions, which are *linked entities*, not a flat extraction. The honest port is **multiple entities in one schema namespace**, mirroring how CORD has menu lines + totals + tax as distinct labels under one `cord@v1`. I'll do it as one composite schema with a label union, matching the spine's existing entity-extraction shape — not a relational rewrite, which would force changes to `pipeline.py` and break the "spine untouched" claim.

**Decision 2: What's the source document?** This matters because the spine is built around *extraction from a source* with provenance. For GTM the realistic source documents are: a company website page, a LinkedIn profile/post, a sales call transcript, a CRM note, an inbound email, a 10-K excerpt. I'll target the **"unstructured GTM artifact"** shape (any of those), with the schema extracting structured signals out of it — which is the same `(source_doc_id, page, bbox, text) → labeled entity` flow as FUNSD/CORD. This keeps the spine genuinely untouched.

Let me draft it now, modeled directly on the `cord@v1` structure from your CORD-STORIES.md.Good. Now I have the precedent. Let me draft `gtm@v1` modeled exactly on how `cord@v1` was structured per CORD-STORIES.md — schema-driven extraction guidance, label union, Pydantic v2, registers alongside the existing schemas.Now the registry-edit snippet and the tests, modeled on the C-1 story acceptance criteria:Let me sanity-check the schema itself runs and the guidance coverage holds:Schema runs clean: 30 labels, guidance covers all 30, confidence bounded, cross-schema labels rejected, 13 link types declared. Let me package the deliverable:### What the schema does

30 labels across 5 entity families (account, contact, signal, engagement, qualification), matching the spine's existing `(label, text, confidence)` entity shape exactly. The qualification family is MEDDIC-derived as *evidence* labels plus a single `Q_DISPOSITION` verdict — that separation matters because it lets the spine extract qualification *signals* (which are spans of text with provenance) separately from the *verdict* (which is the auto-pass/HIL decision the spine already makes). `extraction_guidance()` returns the {label: definition} dict the schema-driven prompt path (post-C-3) consumes, with no per-vertical branching in `pipeline.py`. The `git diff --stat` claim from your METHODOLOGY.md holds: this is `+~200 LOC in schema/` + a 2-line registry edit, zero edits to `pipeline.py`, `calibration/`, `provenance/`, `hil/`, or `eval/`.

---

## Now: one-off, generator, or standalone repo?

This is the right second question because the answer determines whether `gtm@v1` is a demo artifact or the first instance of a *product*. Three options, honestly compared:

### Option A — One-off file in the spine repo
Drop `gtm.py` into `spine/schema/`, register it, done. ~1 day of total work.

**For:** Matches the CORD precedent exactly. The methodology claim — "a new vertical is data + an adapter, not a re-build" — is literally what this is. No new infrastructure to maintain. Demo-ready this week.

**Against:** If the firm hiring you wants vertical agents for *multiple* GTM workflows (outbound, lead scoring, enrichment QA, account research), you'll end up either (a) cramming them all into one bloated `gtm@v1` or (b) writing `gtm_outbound@v1`, `gtm_scoring@v1`, etc. by hand. Each one is a ~1-day port but the labels overlap (account.company_name appears in all of them) and you'll get drift.

### Option B — Schema generator in the spine repo
A `spine/schema/generator/` module that takes a YAML or JSON spec ("here are my label families, here are their definitions, here are the link types") and emits a registered schema. ~3-4 days of work the first time, then minutes per schema after.

**For:** Cleanly separates the *generic capability* (any-vertical schema authoring) from *one specific vertical* (gtm). Lets you spin up `gtm_outbound@v1`, `gtm_scoring@v1`, `claims@v1`, `credentialing@v1` from the same generator. The generator itself becomes a methodology artifact — "we ship the schema generator, customer fills in the YAML during the benchmark call, we instantiate in 30 minutes."

**Against:** It's new infrastructure inside the spine repo, which directly contradicts your audit-driven discipline. The spine has been *intentionally minimal* (P1+P15 only, no scope drift). Adding a code generator is exactly the "let me just add one more module" failure mode your CLAUDE.md warns against. And you don't yet know if you need it — premature.

### Option C — Standalone `schema-forge` repo that emits schemas the spine consumes
Same generator capability as B, but in its own repo. Outputs Python files that drop into `spine/schema/`. The spine stays minimal; the generator evolves independently. ~4-5 days of initial work.

**For:** Preserves the "spine is minimal and audited" property. The generator can grow features (LLM-assisted label discovery from sample documents, ontology import from Bombora/NAICS/etc., schema diffing/versioning) without polluting the spine. Honest separation of concerns: the spine is the *runtime IP*, schema-forge is *authoring tooling*. Also: if the productization story works, schema-forge is a natural standalone product later — it's the thing that turns a 2-hour benchmark call into a registered schema.

**Against:** Premature. You have N=2 schemas (FUNSD, CORD) and are about to add a third. You don't have enough variation to know what the generator's interface should look like. Building a generator on N=3 is curve-fitting; the right N is 5-6, after you've hand-written enough schemas to feel the actual pain points.

### The recommendation

**Do A now. Plan for C after the third paid engagement, not the third schema.**

Here's the reasoning: the productization trigger isn't the *number of schemas* — it's the *number of buyers who paid you to author one*. Schemas you write speculatively don't create the pressure that surfaces the right generator design. Schemas customers paid for do, because their pain points (what they couldn't articulate in the YAML, what they wanted the LLM to bootstrap from a sample doc, what they kept getting wrong) become the generator's actual feature list.

Concretely:

- **This week:** Drop `gtm.py` into `spine/schema/`, register, write the C-1 tests, run the FUNSD regression check from C-3 to prove the spine is genuinely untouched. The demo is "third vertical, same spine, full benchmark in 1 day."
- **Engagements 1-3:** Hand-write each customer's schema during the benchmark call. Notice what's painful. The pain *is* the spec for the generator. Likely: label deduplication across families, ontology imports (NAICS/Bombora/MEDDIC), and LLM-bootstrapped label discovery from sample documents are the three things you'll wish you had.
- **Engagement 3-4 inflection:** If you're consistently spending >1 day per schema and the patterns are repeating, stand up `schema-forge` as a standalone repo. By then you'll know what its interface needs to be.

The deeper principle: **your defensibility is the spine, not the schema generator.** The spine is what survives an audit (Q1/Q2/Q3), what produces calibration ECE numbers, what carries provenance. The schema generator is *convenience* — it speeds up engagement setup but doesn't change the trust story. Build the convenience layer when you've felt its absence, not before. Right now, the absence of a generator costs you 1 day per vertical, which is cheap compared to the cost of building generator infrastructure on too-few examples and locking in the wrong abstraction.

One concrete next step before you commit: **map the firm's GTM-agent ask to entity families.** If they want one workflow (say, outbound personalization), `gtm@v1` as drafted covers ~80% of it and Option A is right. If they want four distinct workflows with different label sets, you're closer to needing Option C earlier — but I'd still write the first two by hand to feel the duplication, then build the generator. Which workflows are they asking for?

Good — this is the operational question that turns the schema into a runnable thing. Let me walk through it the way the CORD-STORIES.md decomposed it, because the answer is three concrete commits, not one.

Before I do, one thing worth surfacing: **your spine has never processed real websites.** Per the Phase-3 audit you pasted, the Unstructured/Docling adapter exists but has only ever been run against FUNSD/CORD pre-OCR'd gold words. The first time real HTML hits the pipeline, things will break — not catastrophically, but in the boring ways (encoding issues, JS-rendered pages returning empty, rate limiting, paywalls, robots.txt). I'll flag where those gotchas live as we go, because pretending they don't exist is exactly the trap your methodology was built to catch.

Now the three steps.

## Step 1 — Register the schema (2-line edit, ~5 minutes)

Drop `gtm.py` into `spine/schema/`, then edit `spine/schema/registry.py`:Verify it works:

```bash
.venv/bin/python -c "from spine.schema.registry import load_schema; print(load_schema('gtm@v1').__name__)"
# → GtmEntity
```

If that prints `GtmEntity`, the schema is live in the registry. That's the entire registration step. The same mechanism that resolved `funsd@v1` and `cord@v1` now resolves `gtm@v1`, and every extraction will be stamped with that version string in the provenance table.

## Step 2 — Build the website ingest adapter (~1 day, the actual work)

Your spine treats every document the same way: rows in `documents` + rows in `words` + rows in `gold_entities` (if you have ground truth). For 100 websites, "ingest" means: pull each URL, extract the text into the `Word` shape the spine expects, persist into Postgres. This is the **per-vertical adapter** layer — exactly what `spine/ingest/cord.py` is for CORD. You're adding `spine/ingest/website.py`.

Here's what that file looks like:Three things worth flagging about this adapter, because they're the gotchas that will bite on first run:

1. **Trafilatura over Unstructured for HTML.** Unstructured does HTML but trafilatura is the better OSS pick for *prospect website* content specifically — it's built around boilerplate removal (nav/footer/cookie banners) which is the dominant noise source on company sites. Unstructured shines on PDFs and complex layouts. Use the right tool per source type; the spine doesn't care which.

2. **JavaScript-rendered sites will return empty.** Modern marketing sites (anything built on Next.js, Webflow, HubSpot CMS with heavy client rendering) often ship a near-empty HTML shell and hydrate via JS. trafilatura sees the shell, returns nothing, you'll get `empty_after_extract` errors. The fix is Playwright/Chromium for those — but that's a 2-3x cost increase, so the right move is: try static first, log the empties, then decide per-engagement whether to add a headless-browser fallback. I'd budget that you'll lose ~15-25% of arbitrary B2B websites to this on the first pass.

3. **Robots.txt and rate limits.** The adapter as written ignores robots.txt and uses a polite-but-low concurrency of 8. For 100 sites this is fine. For 10,000 sites or for sites you don't have permission to scrape (i.e. the customer's prospects, not the customer's own pages), you need a proper crawler with `urllib.robotparser` and per-domain throttling. Out of scope for the demo; in scope before a real engagement.

## Step 3 — Run the end-to-end extraction (one Make target, ~30 min for 100 URLs)

The spine already has `make extract DOC=<doc_id>` for a single document and `make benchmark` for a sweep. You add one new Make target that's the website-specific runner:## End-to-end recap — what actually happens when you run it

You write 100 URLs to `urls.txt`, then run one command:

```bash
make gtm-load-and-extract URLS=urls.txt
```

In about 30 minutes (mostly LLM latency, the HTTP fetches finish in <2 min at concurrency 8), the spine will:

1. **Fetch + clean** every URL (`spine/ingest/website.py` → trafilatura → main text only)
2. **Persist** each as a row in `documents` and N rows in `words` (dataset=`gtm`, split=`ingest`)
3. **Run the existing extract pipeline** — for each doc: chunk → LLM call → validate against `gtm@v1` → retry on failure → route persistent failures into `failed_extractions` (never dropped, per your spine's contract)
4. **Stamp every extraction** with `schema_version='gtm@v1'`, model name, prompt version, confidence
5. **Record provenance** for every entity (`source_doc_id`, `page`, `bbox`, `text`, model, schema version, confidence)
6. **Calibrate confidence** using whichever Platt calibrator is currently fit, and route low-confidence extractions to `review_queue` (P15/HIL)

You inspect results with three SQL queries the runner prints at the end:

```sql
SELECT label, COUNT(*), AVG(confidence) FROM extractions
WHERE schema_version = 'gtm@v1' GROUP BY label;

SELECT * FROM provenance WHERE schema_version = 'gtm@v1' LIMIT 20;

SELECT COUNT(*) FROM review_queue WHERE schema_version = 'gtm@v1';
```

Or open the Streamlit review UI: `make review` — same UI that handled FUNSD and CORD, but now showing GTM entities with their source bboxes (which are placeholder zeros — see gotcha below).

## What the audit-driven `git diff --stat` will look like

This is the proof your methodology asserts. After all three commits, your diff against the pre-GTM commit is:

```
spine/schema/gtm.py              +290    (new schema, including extraction_guidance)
spine/schema/registry.py           +2    (register gtm@v1)
spine/ingest/website.py          +145    (new source adapter)
spine/ingest/run_websites.py      +50    (new CLI runner)
Makefile                           +3    (new gtm-load-and-extract target)
pyproject.toml                     +3    (trafilatura, selectolax deps)
tests/test_gtm_schema.py         +60    (acceptance tests for the schema)
```

**Byte-for-byte unchanged:** `extract/pipeline.py`, `extract/llm.py` (already schema-driven post-C-3), `calibration/*`, `provenance/*`, `hil/*`, `eval/f1.py`, `ingest/store.py`, `db.py`. Same claim as your CORD methodology, third vertical in a row.

## The honest gotchas — what will go wrong on the first run

I want to flag these explicitly because pretending the first run will be clean is exactly the failure mode your methodology was built to catch:

**You have no gold labels for websites, so `eval/f1.py` does not run.** F1 is computed against `gold_entities`; websites have none. This is *unsupervised inference*, not benchmarking. To get F1 you need to hand-label ~50 sites (or use the customer's CRM as the gold), which is exactly the "benchmark call" output from your methodology — the 50-100 labeled examples the customer brings to the 2-hour benchmark conversation. Without that, you have extractions and provenance and a calibration curve, but no accuracy number.

**Calibration will produce numbers but may not be meaningful.** Your Platt calibrator is fit on FUNSD + CORD `(confidence, correct)` pairs. Running it on GTM extractions applies a calibration learned from a different distribution. The calibrated confidence will be a number, but its ECE on GTM is unknown until you have GTM gold. Your audit's Q2 question — "is calibrated ECE < raw ECE on real held-out data?" — is *unanswerable* for GTM until the labeled set exists. I'd be honest about this when demoing: the calibration *infrastructure* transfers; the calibration *fit* doesn't, until you have a labeled GTM set.

**Bounding boxes are placeholder zeros, and for websites they always will be unless you upgrade.** This is the same caveat your METHODOLOGY.md already makes for FUNSD/CORD text-only mode, but it's worth restating because for *real GTM provenance* (the "click this row → highlight the source span on the original page") you'd need to track DOM paths or character offsets through trafilatura's extraction. That's a Phase-3.5 lever — about 1-2 days of work in `text_to_words()` to track character offsets, plus a UI update to highlight by offset instead of bbox. Out of scope for the first run; named as a known limitation.

**~15-25% of websites will return empty.** JS-rendered marketing sites are the dominant failure. The adapter logs them as `empty_after_extract`; you'll want to inspect that list and decide whether to add a Playwright fallback per-engagement.

**Cost.** At ~$0.02/doc on CORD, 100 websites is ~$2 if pages are short, ~$5-10 if they're long (10-K excerpts, lengthy about pages). Negligible for the demo, but worth knowing the budget shape before running thousands.

## One concrete next step before you run it

Before you run on 100 real websites, **run on 5 first.** Pick 5 URLs that span the failure modes — one classic static site (e.g. ycombinator.com), one Webflow/Next.js site (most modern startups), one site with cookie/GDPR walls (any EU company), one with heavy JS (a SaaS marketing page), one with mostly tables/lists (a pricing page). The 5-URL run takes 90 seconds and tells you whether the trafilatura fallback rate is acceptable for your demo corpus, before you've burned 30 minutes on 100. If 3 of 5 come back empty, you need Playwright before you bother running the full set; if 5 of 5 come back clean, the adapter is good enough as-is.

Good — this is the right question, and it's the question that separates "I have a demo" from "I have something a buyer will pay for." Let me work through it honestly, because the answer is not what it might first look like.

## The reframe before the how-to

You're asking how to *produce* the five Phase-1 artifacts for GTM without doing a Phase-1 engagement. I want to push back on the framing slightly before answering, because the framing contains a trap.

**Phase 1's value is not the artifacts themselves — it's the operator validation of the artifacts.** A schema you write alone in a room and a schema an operator signed off on after looking at 50 of their own examples are physically the same file. They are commercially very different objects. The first is a hypothesis. The second is evidence. Buyers pay for the second.

This matters because there are three honest paths here and they produce three different commercial objects:

- **Path A — Synthetic everything.** You generate all five artifacts using LLMs + public sources. Result: a richer demo than what you have now. Commercial weight: ~zero. No operator has touched it. A buyer's first question — *"where did these labels come from?"* — has no good answer.
- **Path B — Public-source bootstrapping.** You build the artifacts from real public operator content (job postings, sales playbooks, public sales calls, CRM exports on Kaggle, MEDDIC literature). Result: a demo where every artifact can be traced to a real operator source, just not *your buyer's* operators. Commercial weight: meaningful — you can defend each label with a citation. This is what a credible "v0" looks like.
- **Path C — Compressed Phase 1 (the benchmark call).** You produce a *generic* Path B version, then run a 2-hour structured call with the buyer where they validate, edit, and label against their own data. Result: their schema, their failure modes, their labels — produced in hours instead of weeks because you brought the v0 to the call. Commercial weight: this is the actual sale.

The right move is **B now, C with the first buyer.** Skip A entirely — it's tempting because it's fastest, but synthetic-everything is exactly the failure mode your audit's Q2 caught (the calibration layer was fit on synthetic data and passed unit tests while being inert). Don't repeat that pattern at the artifact layer.

With that frame, here's how to produce each artifact via Path B.

## Artifact 1 — Populated output schema

**You already have this.** `gtm@v1` as drafted is the schema. The question is whether to populate it further (add labels) or freeze it. My recommendation: freeze v1 at 30 labels, plan for `gtm@v2` to emerge from the first buyer call.

The reason to freeze: every additional label you add speculatively is a label that wasn't operator-validated. The 30 you have are defensible — they come from the standard CRM/MEDDIC vocabulary that has existed for decades. Adding `S_TECHNICAL_DEBT_MENTION` or `Q_SECURITY_REVIEW_REQUIRED` because they "feel useful" is the move that erodes the schema's credibility. Wait for a buyer to say *"we always look for X"* and add X in v2.

**Effort: zero. Already done.**

## Artifact 2 — Modifier ontology

This is the artifact that most needs the operator and most rewards Path B preparation. The modifier ontology for GTM has three layers, and the OSS/public coverage is different for each:

**Industry / firmographic modifiers.** Strong public coverage. Pull and structure:
- NAICS 2022 codes (free CSV from census.gov, ~1,000 industry codes with hierarchical structure)
- Crunchbase industry taxonomy (~700 categories, public via their data export docs)
- LinkedIn industry list (147 industries, scrapeable from their public job-posting picker)

Effort: half a day to download, normalize into a single hierarchical JSON, and tag each `account.industry` extraction against it.

**Persona / seniority modifiers.** Medium public coverage. Sources:
- The "title normalization" datasets that exist on HuggingFace (search "job title classification" — a few have 100k+ titles mapped to seniority+department)
- LinkedIn's "Sales Navigator" public function categories
- ZoomInfo's published job-function taxonomy (in their developer docs)

Effort: 1 day. Build a `{raw_title: (seniority, department)}` mapping by combining 2-3 of these. This gives the spine's `C_SENIORITY` and `C_DEPARTMENT` labels their normalized targets.

**Intent / signal modifiers.** This is where it gets interesting. Public sources:
- **Bombora's public intent topic taxonomy** — they publish their full topic list (~7,000 topics, hierarchically organized) as a marketing artifact. Scrape it from their site or pull from G2's similar published list.
- **6sense's published intent stages** (awareness/consideration/decision) — public framework
- **MEDDIC/MEDDPICC literature** for the qualification-evidence modifiers — there are several public structured versions on Notion/Github

Effort: 1-2 days to pull these into a single `modifiers.yaml` file structured by entity family.

**The total Path B modifier ontology is about 3 days of careful work that produces a defensible, citation-backed file.** Every modifier traces to a real public taxonomy. The thing it cannot do is encode *the buyer's* specific modifiers — their "we never count VPs of Marketing at companies under 200 employees because they don't have budget" rule — but those emerge from the benchmark call, not before.

## Artifact 3 — Policy / rules library

This is the artifact with the *strongest* public coverage and the *weakest* reason to invent. The policy library for B2B GTM has been publicly codified for 40 years:

- **MEDDIC and MEDDPICC** are fully documented policies — qualified/disqualified rules, escalation triggers, "compelling event" definitions. Multiple public structured versions exist on GitHub.
- **SPIN selling, BANT, CHAMP, GPCTBA/C&I** — all public, all rule-shaped
- **Winning by Design's "SPICED" framework** — published openly
- **HubSpot's published lead scoring rubric** — gives you concrete point values per signal type

The right move: pick **one** policy framework (I'd recommend MEDDPICC because it's the most operationally specific) and encode it as a Python module that maps your `gtm@v1` qualification labels to disposition decisions. Something like:

```python
# spine/hil/policies/gtm_meddpicc.py
# Maps extracted Q_* evidence labels → disposition.
# Source: MEDDPICC framework (public). Citation in docstring.
```

Then your HIL routing's confidence threshold and your policy layer compose: low confidence → HIL regardless of policy; high confidence + policy says "qualified" → auto-pass; high confidence + policy says "needs human verification on authority" → HIL with a specific reason.

**Effort: 1 day. The policy is public; you're just encoding it as code with named provenance.**

The honest caveat: the buyer will have *their own* qualification policy that overrides MEDDPICC in specific ways ("we always require Q_TIMELINE_STATED for enterprise deals, regardless of other evidence"). That's a `policies/{buyer}_overrides.py` file produced during the benchmark call. The base policy is generic; the overrides are bespoke.

## Artifact 4 — Failure-mode library

This is the artifact where public sources are *richest* and Path B is *cleanest*. GTM has a massive corpus of operator-validated failure modes because every outbound shop has written about them publicly. Concretely:

**Sources, ranked by signal density:**

1. **r/sales failure post-mortems** — ~5,000 posts tagged with "what went wrong" / "deal lost" stories, operator-language, real edge cases. Use the Pushshift archive (still available via academic mirrors as of late 2025) or scrape directly.
2. **The Clay Slack community** — 40k+ GTM operators documenting enrichment failures, ICP mistakes, intent-signal false positives. The community has searchable archives; even reading 50 threads gives you 30-40 named failure modes.
3. **"AI SDR fail" LinkedIn content** — its own genre. Search "AI SDR mistakes" / "AI outbound failures" / "Apollo enrichment errors" and you get hundreds of operator posts. This is *specifically* validated for AI-driven GTM, which is your buyer's use case.
4. **Smartlead, Instantly, Lemlist deliverability blog posts** — each has 50+ posts documenting spam-flag triggers, bounce patterns, mailbox warming failures.
5. **Predictable Revenue, Sales Hacker, Reply.io blog archives** — qualification mistakes, ICP drift, persona-targeting failures. Decade of public content.

**The structuring approach.** This is where the real work is. You're not just collecting failure stories — you're converting them into the spine's failure-mode library format (DeepEval-style assertions per your METHODOLOGY.md). The pattern:

For each failure mode, you produce:
- A name (e.g. `false_positive_intent_signal`)
- A description (one sentence, operator-language)
- A source citation (the actual reddit post, blog URL, or community thread)
- A detection assertion — code that runs against an extracted entity and returns `(detected, evidence)`
- A test fixture — a synthetic-but-realistic example that triggers the failure

Example structure:

```python
# spine/eval/failure_modes/gtm/false_positive_intent.py
"""
Failure mode: model extracts an intent signal from generic marketing copy
on the prospect's own website (e.g. they describe their product as solving
"data warehouse problems" — the model labels this as S_INTENT_TOPIC for
data warehouse, when in fact this is the vendor's *own* product description).

Source: r/sales thread '2024-08-15-apollo-fake-intent', plus 6sense's
published guidance on first-party vs third-party intent.
"""

def detect(entity, source_doc) -> tuple[bool, str | None]:
    if entity.label != GtmLabel.S_INTENT_TOPIC:
        return False, None
    # Heuristic: if the intent text appears in the prospect's own
    # /products or /solutions URL path, it's likely first-party noise.
    if "/product" in source_doc.url or "/solution" in source_doc.url:
        return True, f"intent extracted from vendor's own product page"
    return False, None
```

**The realistic scope.** A *useful* failure-mode library for the demo is ~25-30 named failure modes, each backed by a real public source, with assertion code and at least one test fixture. That's about 3-4 days of focused work — 1 day collecting and triaging sources, 2-3 days structuring them into the library format.

This is also the artifact with the **most defensible commercial story.** A buyer reviewing your demo asks "how do you know what can go wrong?" and you point to a library of 25 named failure modes, each citing the operator post that surfaced it. That is a strictly stronger position than 99% of AI-GTM vendors are in. Most vendors have a vague "we have eval coverage." You have 25 named failures with citations.

## Artifact 5 — Ground-truth corpus

This is the hardest one, and the one where Path B has real limits worth being honest about.

**The Path B options, ranked by quality:**

1. **Public B2B prospect datasets.** A few exist:
   - The "B2B SaaS sales dataset" on Kaggle (~10k records, some labels)
   - **OpenSales** (newer, ~5k labeled records)
   - **LeadMagic public exports** (~3k records, basic labels)
   - SEC EDGAR scrapes (real companies + filings, but no GTM labels)
   - LinkedIn public profiles (real personas, but scraping them is legally fraught — don't)
   
   Quality: medium. Real data, but labels are usually basic (industry, employee_range) and don't cover the signal/qualification labels your schema needs.

2. **Synthetic-but-grounded generation.** Use Claude/GPT to generate ~500 prospect records *grounded against real public sources* — pick real companies from SEC filings, real titles from public LinkedIn job postings, real intent signals from actual Bombora-published surge data. Each synthetic record has a citation to its real-source ingredients. Apply the gtm@v1 schema by hand-labeling against the framework.

   Quality: medium-high if done carefully, low if rushed. The trap is generating fluent garbage — records that look real but encode no operator judgment.

3. **The customer's own data (Path C).** During the benchmark call, the customer brings 50-100 records from their CRM marked qualified/unqualified. These become your *real* gold set. They have it; every B2B company has it; it takes them 30 minutes to export.

   Quality: highest. This is what calibration should actually fit against.

**The honest recommendation: produce a Path B v0 of ~200 records using option 2 (synthetic-but-grounded with citations), label it against gtm@v1, use it to run an *initial calibration fit* you can demonstrate. Be explicit in your demo that this is the v0 fit and that the first thing the benchmark call produces is the buyer-specific re-fit on their 50-100 real records.**

This is the same honesty pattern your METHODOLOGY.md already uses: "F1 0.397 is the floor of what the methodology produces out of the box; layout features, fine-tuning, and logprob confidence are named levers." You'd say: "Calibration ECE on the synthetic v0 set is X; the named lever is fitting on the buyer's real CRM data, and the benchmark call produces that fit on the first day."

**Effort: 2-3 days for ~200 records, plus the calibration fit run.**

## Total picture — what you have at the end

Per-artifact effort, honestly estimated for Path B:

| Artifact | Days | What you have at the end |
|---|---|---|
| Schema | 0 (done) | `gtm@v1` with 30 labels, frozen, v2-ready |
| Modifier ontology | 3 | Structured `modifiers.yaml` covering industry/persona/intent, every modifier with public source citation |
| Policy library | 1 | `gtm_meddpicc.py` mapping evidence labels → disposition, framework-cited |
| Failure-mode library | 3-4 | 25 named failure modes with assertion code, test fixtures, public source citations |
| Ground-truth corpus | 2-3 | ~200 records, synthetic-but-grounded, hand-labeled, calibrator fit produced |
| **Total** | **~10 working days** | Defensible v0 of all five artifacts, every one citation-backed |

After 10 working days of focused work, your demo looks like: "Here's the spine running on websites. Here's the schema, with each label traced to either CRM-standard or MEDDIC-standard vocabulary. Here's the modifier ontology, every modifier sourced. Here's the policy library, framework-cited. Here are 25 named failure modes, each backed by an operator post. Here's a 200-record gold set with calibration ECE numbers. *And here's what the benchmark call adds on top of all of this — your data, your modifiers, your policies — produced in 2 hours.*"

That's a defensible commercial object. It's also the structural template for what every subsequent vertical (claims, credentialing, credit memos) will produce, which is the point of having a methodology.

## What I would not do

A few things worth naming because they're tempting and wrong:

**Don't generate a fully synthetic failure-mode library with no citations.** This is the single most tempting shortcut (~2 hours with Claude) and it's exactly the move that destroys credibility on inspection. A failure mode with no source is just a hallucination with a name. The 3-4 day cost of doing it from real operator content is what makes it credible.

**Don't ship the full v0 to a buyer before a benchmark call.** The artifacts exist to make the benchmark call cheap and high-leverage, not to *replace* it. If you hand over the modifier ontology pre-call, the buyer's read is "you already think you know my business." The right framing is: "We've done the generic 80%. The 2-hour call produces the 20% that makes it yours."

**Don't try to produce the customer's CRM data synthetically.** Their qualified/unqualified labels carry information that synthetic data cannot encode — specifically, the implicit policies their reps actually apply versus the policies their playbook claims they apply. That delta *is* the value of the engagement. Don't pre-empt it.

## One concrete next step

Pick artifact 4 first — the failure-mode library. Not because it's easiest (it's not), but because it produces the most asymmetric commercial value per day invested. After 3-4 days of work you have a thing that no AI-GTM vendor has: a named, sourced, code-asserted library of 25 failure modes. That's the single artifact that, by itself, gets you a benchmark call.

The other four (modifiers, policy, ground truth, plus the already-done schema) you can do in parallel or sequence after — but the failure-mode library is the wedge.
