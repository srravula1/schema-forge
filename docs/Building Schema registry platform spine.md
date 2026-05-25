# BOM

This is the right question to be asking, and I want to push back on one piece of framing before answering it directly.

## **The reframe before the estimate**

You've described this as "hands-on experience, not a product development exercise." That distinction matters and I want to honor it — but it's also the exact place where the pattern from your retrospective most reliably reproduces. The risk is not that you build a product when you meant to build a learning rig. The risk is that you build a learning rig that takes 4 months when it should have taken 6 weeks, because "hands-on" without a hard scope cap becomes "let me just add one more module."

So the estimate below is structured around a **time-boxed harness that proves you can deliver Phase 3–4 of the FDE engagement**, not a platform. The discipline is: pick *one* pattern, wire it end-to-end on a *public* labeled dataset, get the eval harness green, stop. Resist the urge to do all six modules. The case-study value is "I stood up a governed extract pipeline with provenance and HIL on the CORD-19/FUNSD/RVL-CDIP corpus and hit X% F1 with calibrated confidence" — not "I built a platform."

With that frame, here's the feasibility and effort estimate.

## **Pattern selection: which one to build first**

You have five Tier-A patterns in the thesis. Only one is the right choice for a hands-on harness with a public eval set:

**Build P1 \+ P15 (doc extract \+ HIL governance). Skip the others for now.**

Three reasons:

1. **It's the spine of half the Tier-A portfolio.** P1+P9+P15 is the "ingest→extract→reason→generate→govern" composite. P1+P15 is the front half — the harder, more eval-able half. If you can deliver this cleanly, you've proven the methodology for credentialing, credit memos, claims, fund accounting, and accreditation simultaneously.  
2. **Public labeled datasets exist and are battle-tested.** FUNSD (forms), CORD (receipts), DocVQA, RVL-CDIP (doc classification), PubLayNet (layout), and the Kleister suite (NDA, Charity) all have published F1/accuracy baselines. You can benchmark against known numbers and know whether your harness is working. No other pattern has this — P5 voice has no clean public eval, P6 predictive needs your own labels by definition, P4 agent orchestration evals are immature.  
3. **It's the pattern where the schema-registry \+ calibration \+ provenance layer — your stated defensibility wedge — actually lives.** Building this harness *is* the act of testing whether your platform thesis is real.

P6 (predictive risk) is the second module to build, but only after P1+P15 is green, and on a different public dataset (e.g., the Boston housing/credit-default/lending-club style sets, or the Kaggle construction-delay or churn datasets). I'd defer it to a second sprint.

## **Feasibility verdict: feasible, with named risks**

**Yes, this is feasible in 6–8 weeks of calendar time** with you at \~50% allocation and one junior AI engineer at \~80% allocation, supplemented by AI dev agents (Claude Code, Cursor, similar) for scaffolding. It is not feasible as a weekend project, and the most common failure mode is treating it as one.

The reasons it's feasible:

* Every module except the schema/calibration/provenance layer is wrapped OSS. You are not writing retrieval code, not writing a voice pipeline, not writing an agent runtime. You are wiring.  
* The custom code is concentrated in one layer (the spine), which is exactly what your thesis predicted.  
* Public eval datasets remove the "is it working" ambiguity that kills internal builds.

The reasons it could slip:

* **OSS version churn.** Pipecat hit v1.0 in April 2026; LangGraph is moving fast; Unstructured.io's API surface changes between minor versions. Pin versions in week 1 and don't chase upgrades mid-sprint.  
* **Eval dataset preprocessing is always longer than expected.** FUNSD annotations need normalization; CORD has quirks. Budget 1.5× whatever your first estimate is for data prep.  
* **The provenance/audit layer is where custom code accumulates silently.** This is the module that most resembles "real product engineering" and where scope creep is most likely.

## **Stack: true OSS, version-pinned, minimal surface**

Based on the 2026 landscape in your thesis, here is the specific stack for the P1+P15 harness. Everything below is MIT/Apache/BSD.

| Layer | Choice | Why this over alternatives |
| ----- | ----- | ----- |
| Model gateway | **LiteLLM** (MIT) | Vendor-agnostic, supports OpenAI/Anthropic/Ollama/local, single API surface, retry/fallback built in. Avoids lock-in for the eval comparison work. |
| Doc ingest | **Unstructured.io** (open core, use OSS tier) | De facto. Handles layout, OCR, tables. Pair with **Docling** (IBM, MIT) as a fallback for layout-heavy PDFs. |
| Extract pipeline | **LangExtract** or raw LangGraph nodes calling structured output | Don't use a heavy framework here; the extract step is one LLM call per chunk with a Pydantic schema. Keep it boring. |
| Vector store | **Qdrant** (Apache-2, self-host via Docker) | Fastest to stand up locally, good filtering for provenance metadata. Chroma is acceptable; pgvector if you want everything in Postgres. |
| Doc store | **Postgres** with JSONB columns | Don't introduce MongoDB. Postgres holds raw docs, extracted schemas, provenance records, eval results. One database. |
| Queue | **Redis Streams** or **Postgres-as-queue** (river/pgmq) | Skip Celery/RabbitMQ for a harness. Postgres-as-queue is one fewer service to run. |
| Agent / workflow runtime | **LangGraph** (MIT) | Your thesis already named this as the production default. Use it for the extract→validate→route-to-HIL graph. |
| Eval bus | **Langfuse** (MIT, self-host) \+ **RAGAS** (Apache-2) for retrieval eval \+ **DeepEval** for assertion-style tests | Langfuse is the trace store \+ LLM-as-judge harness. RAGAS for any retrieval-augmented steps. DeepEval for the failure-mode library as pytest-style assertions. |
| Schema registry | **Custom, \~300 LOC** | JSON Schema \+ Pydantic v2 models, versioned in git, loaded into the runtime via a thin registry. This is your IP layer. |
| Confidence calibration | **Custom, \~200 LOC** | Per-field confidence scores from the LLM, combined with a Platt-scaling or isotonic regression layer trained on a holdout from the eval set. scikit-learn primitives only. |
| Provenance/audit | **Custom, \~400 LOC** \+ Langfuse traces | Every extracted field gets a `(source_doc_id, page, bbox, model, prompt_version, timestamp, confidence)` record in Postgres. Langfuse holds the full call trace. |
| HIL routing | **Custom, \~200 LOC** \+ a thin Streamlit or Next.js review UI | Confidence threshold → queue for human review → labeled correction flows back into the eval set. |

Total custom code: \~1,100 lines across four modules, each independently testable. That's the modularization you wanted.

## **Public eval datasets to anchor on**

Pick **one primary, one secondary**:

* **Primary: FUNSD** (Form Understanding in Noisy Scanned Documents, 199 forms, IOB-tagged entities and relations). Public baselines are in the 0.80–0.88 F1 range for entity extraction with LayoutLM-family models. Your harness using GPT-4o or Claude with a Pydantic schema should hit competitive numbers without fine-tuning, which is exactly the point — you're testing the *wrapper*, not the model.  
* **Secondary: CORD** (receipts, 1000 train/100 test, 30 fields). Cleaner schema, faster iteration, good for the calibration layer development.

Both have published leaderboards. Both are MIT/research-licensed. Both are small enough to run locally on a laptop.

If you want a healthcare/credentialing analog later, the **MIMIC-III** clinical notes corpus (requires credentialing but free) or the **n2c2 NLP challenges** datasets give you the regulated-domain texture. Defer to sprint 2\.

## **Bill of Activities — 6-week harness build**

This is the Phase 3–4 equivalent of the FDE engagement, run on public data with you as the customer.

**Week 1 — Stack provisioning and dataset prep (\~30 hours total, you 10h / engineer 20h)**

* Docker Compose stack: Postgres \+ Qdrant \+ Redis \+ Langfuse, all version-pinned  
* LiteLLM gateway configured with at least two providers (one frontier, one local via Ollama for cost control)  
* FUNSD downloaded, normalized into your Postgres schema, train/dev/test split documented  
* Pydantic schema written for FUNSD entities (header/question/answer/other \+ linking relations)  
* Git repo with module structure: `ingest/`, `extract/`, `schema/`, `calibration/`, `provenance/`, `hil/`, `eval/`

**Week 2 — Extract pipeline end-to-end on dev set (\~35 hours, you 10h / engineer 25h)**

* Unstructured.io ingest of FUNSD images → Postgres doc store with page/bbox metadata  
* LangGraph extract graph: chunk → LLM call with Pydantic schema → validate → write to Postgres  
* First eval run: F1 vs gold annotations on the dev set, logged to Langfuse  
* Goal: green pipeline end-to-end, even if accuracy is mediocre. *Do not tune yet.*

**Week 3 — Eval harness and failure-mode library (\~30 hours, you 15h / engineer 15h)**

* DeepEval test suite: one assertion per known failure mode (missed entities, schema violations, linking errors, OCR-induced errors)  
* RAGAS configured if you add a retrieval step for few-shot example selection  
* Langfuse dashboards: per-field F1, latency, cost, confidence distribution  
* This is the week where you build the methodology artifact that ports to customer engagements. Document it as you go.

**Week 4 — Confidence calibration and provenance (\~35 hours, you 15h / engineer 20h)**

* Per-field confidence extraction (logprobs where available, self-evaluation otherwise)  
* Calibration layer: fit Platt scaling on dev set, validate on test set, plot reliability diagrams  
* Provenance records wired: every output field links to source bbox \+ model \+ prompt version  
* This is the **most defensible week of work** — it's the layer your thesis named as the moat

**Week 5 — HIL routing and review UI (\~30 hours, you 10h / engineer 20h)**

* Confidence threshold → low-confidence queue in Postgres  
* Streamlit review UI: side-by-side source doc \+ extracted fields \+ accept/correct/reject  
* Corrections flow back to a "human-labeled" table that can be used for re-calibration  
* Shadow-mode run on test set with HIL simulated (treat gold annotations as the human)

**Week 6 — Methodology extraction and write-up (\~25 hours, you 20h / engineer 5h)**

* Final eval run on held-out test set, results vs published baselines  
* Architecture diagram, module README files, runbook  
* The case-study artifact: "Governed extract harness on FUNSD — methodology, results, what transfers to vertical engagements"  
* This is the non-billable methodology time you named in the FDE positioning doc. Do not skip it. This week *is* the deliverable that makes the next customer engagement easier to sell.

**Total: \~185 hours over 6 weeks.** You at \~80 hours (13 hrs/week, \~1/3 time), engineer at \~105 hours (17 hrs/week, \~1/2 time). AI dev agents compress the engineer's hours by maybe 20–30% on scaffolding work (Docker compose, Pydantic models, Streamlit UI, test boilerplate) but do not compress your time on schema design, calibration logic, or methodology extraction — those require judgment.

## **Bill of Materials — what you provide vs what's external**

**You provide:**

* The schema registry design (your IP)  
* The calibration approach choice (Platt vs isotonic vs binned)  
* The provenance record structure  
* The failure-mode library (curated from FUNSD error analysis)  
* The HIL routing policy

**External / OSS:**

* All runtime infrastructure (everything in the stack table above)  
* FUNSD dataset and gold annotations  
* Published baselines for comparison  
* Pre-trained models via API (frontier) and Ollama (local)

**Compute budget:**

* Local dev: any machine with 16GB RAM and Docker  
* Model API costs for full eval runs: \~$100–300 over 6 weeks if you use frontier models for the eval set; near-zero if you run Llama-3.1-8B locally for development and only use frontier models for the final benchmark  
* Langfuse self-hosted: free  
* Total cash cost: under $500

## **Bill of People — who does what**

| Role | Hours | Why |
| ----- | ----- | ----- |
| You (FDE lead) | \~80 over 6 weeks | Schema design, calibration approach, methodology extraction, eval interpretation. Cannot be delegated — these are the judgment calls that become the IP. |
| Junior AI engineer | \~105 over 6 weeks | Stack provisioning, glue code, Streamlit UI, test scaffolding, dataset preprocessing. Pair with AI dev agents heavily. |
| AI dev agents (Claude Code / Cursor) | continuous | Force-multiplier on the engineer's hours, especially for boilerplate (Docker compose, Pydantic models, test fixtures, UI). Do not use them for the calibration layer or provenance design — those need human judgment. |

You explicitly do not need: a senior engineer, a domain SME, an MLOps person. This is the right team size for a harness. If you find yourself wanting to add anyone, that's the signal you've drifted from harness into product.

## **The four risks worth naming**

**1\. Scope drift toward "let's add P9 generation too."** Generation is the natural next step and it will be tempting in week 4 when extract is working. Resist. P9 is sprint 2\. Adding it now turns 6 weeks into 12\.

**2\. The calibration layer is the most novel piece and will take longer than estimated.** I budgeted \~20 hours for it; realistically it could be 30–40 if you haven't done Platt/isotonic work before. This is fine if you treat it as the learning core of the sprint, but plan for it.

**3\. Langfuse self-hosting has rough edges.** If it eats more than 4 hours of setup time, switch to their cloud free tier and move on. The eval bus matters; the self-hosting is not the point.

**4\. The "shadow mode on real customer data" goal in your last bullet is not achievable in this harness.** You're running on FUNSD. That's by design — public data lets you benchmark. Real customer data is sprint 3, after you have a paying customer (which is the FDE engagement scoping doc question). Don't conflate the two.

## **The honest bottom line**

This is a feasible 6-week sprint that produces three durable artifacts: a working harness you can demo, a methodology document that transfers to customer engagements, and benchmarked results on a public dataset that you can cite in sales conversations. The total cost is \~185 hours of labor and under $500 in compute.

The hard discipline is not the technical work — most of it is wrapping OSS. The hard discipline is week 6: actually writing up the methodology instead of starting the P9 generation module. That's the move that turns this from a learning exercise into the foundation of the productized practice.

One concrete next step before you commit: pick the dataset (FUNSD vs CORD) this week, write the Pydantic schema for it, and commit it to a repo. The act of writing the schema is the smallest possible test of whether the spine layer is real. If the schema takes more than 4 hours to write, the scope is wrong. If it comes out cleanly, the rest of the sprint will too. Want me to draft the FUNSD Pydantic schema as the week-1 starting point?

# OSS

Good question — and the right one to ask before you commit to building. If 70% of the harness already exists in a public repo, you build the 30% delta and save 4 weeks. If 30% exists, you build the 70% delta and the 6-week estimate holds.

Let me search the current landscape rather than answer from memory, since this space moved fast in late 2025 and early 2026.Useful — confirms the Langfuse+LangGraph cookbook exists and MinerU is in the picture. Let me search more specifically for harnesses that bundle the spine.Interesting — the Dec 2025 arxiv paper describes almost exactly your spine (schema-constrained extraction \+ sentence-level provenance \+ audit). Let me search for the actual repo and for confidence calibration repos.Good. Now let me look for one more thing: starter templates that bundle multiple modules.I have enough. Let me also verify the FUNSD-specific tooling landscape quickly so the coverage map is honest.I have enough to give you an honest coverage map. Let me synthesize.

## **The short answer**

**No single repo covers the full spine end-to-end.** That's actually good news for your thesis — if one existed at high quality, the schema-registry+calibration+provenance layer wouldn't be defensible. What does exist: high-coverage repos for *each module individually*, plus a few starter templates that bundle 3–4 modules at toy depth. The custom integration work — and especially the schema-registry \+ calibration layer — is exactly where your sprint earns its keep.

Here's the coverage map, module by module, with specific repos and what each saves you.

## **Coverage map**

| Your module | What's available OSS | Coverage % | What you still build |
| ----- | ----- | ----- | ----- |
| **Stack provisioning (Docker Compose: Postgres \+ Qdrant \+ Redis \+ Langfuse \+ LiteLLM)** | `langfuse/langfuse` ships its own compose; `mfmezger/conversational-agent-langchain` and `ks6088ts-labs/template-langgraph` bundle FastAPI \+ LangGraph \+ Qdrant \+ Phoenix/Langfuse in one compose file. JARVIS (`hyhmrright/JARVIS`) bundles even more (Postgres, Qdrant, MinIO, Redis, monitoring) in one `docker compose up`. | **85%** | Merge two compose files, pin versions, add LiteLLM gateway service (\~4 hours instead of 2 days) |
| **Doc ingest pipeline (PDF/image → text \+ layout \+ bboxes)** | Unstructured.io (most general), MinerU (`opendatalab/MinerU`, best layout/table extraction in 2026 benchmarks per their paper), Docling (IBM, strong on PDFs), NovaLAD (newer, CPU-optimized, 96.5% TEDS on DP-Bench) | **95%** | Pick one, wrap with a thin adapter that normalizes outputs to your provenance schema (`source_doc_id, page, bbox, text`). \~100 LOC. |
| **Structured extraction (LLM → Pydantic)** | `567-labs/instructor` (3M monthly downloads, the default), PydanticAI (heavier, agent-style), LangExtract | **95%** | Define your Pydantic schemas for FUNSD. Instructor handles validation+retries. \~150 LOC for schemas. |
| **Agent / workflow runtime** | LangGraph \+ Langfuse cookbook (`langfuse/langfuse-docs/cookbook/integration_langgraph.ipynb`) shows the exact wiring | **90%** | Write your extract→validate→calibrate→route graph as LangGraph nodes. \~250 LOC. |
| **Observability / tracing** | Langfuse (MIT, self-hosted compose, OTel-native, all major framework integrations) — drop-in callback handler | **95%** | Configure projects, dashboards, eval datasets. \~2 hours config, near-zero code. |
| **Eval harness** | RAGAS (retrieval eval), DeepEval (assertion-style), `stephenleo/llm-structured-output-benchmarks` (already benchmarks Instructor/Mirascope/LangChain/LlamaIndex/Outlines on NER+extraction), `madviking/pydantic-llm-tester` | **80%** | Wire your failure-mode library as DeepEval assertions. Wire FUNSD F1 as a Langfuse dataset. \~300 LOC. |
| **HIL routing \+ review UI** | No clean OSS standard. Streamlit examples exist piecemeal; Argilla is heavier and label-studio-shaped; Langfuse has manual annotation queues but not a domain review UI. | **30%** | This is real custom work. \~400 LOC for a Streamlit review UI \+ queue table \+ correction-flow-back-to-eval-set. |
| **Schema registry (your IP)** | JSON Schema \+ Pydantic v2 give you primitives. No OSS "schema registry for LLM extraction." Confluent's exists for Kafka, irrelevant here. | **15%** | This is your IP. Versioned schemas in git \+ a thin loader \+ a "which version produced this output" record on every extraction. \~300 LOC. |
| **Confidence calibration (your IP)** | Strong academic work but no turnkey library. `Exploration-Lab/LLM-Calibration-Mechanism` is research code, not production. scikit-learn gives you Platt/isotonic primitives. Recent papers (multivariate Platt scaling, fine-grained local Platt scaling from Apr 2026\) give you the methodology to implement. | **20%** | This is your IP. Per-field confidence extraction \+ Platt scaling fit on FUNSD dev set \+ reliability diagrams. \~250 LOC \+ scikit-learn. |
| **Provenance / audit (your IP)** | Langfuse traces give you the *call-level* audit trail for free. The *field-level* provenance (every extracted field → source bbox \+ model \+ prompt version) doesn't exist as a library. Closest reference: the Dec 2025 arxiv paper on schema-constrained biomedical extraction describes this exact pattern as novel. | **25%** | This is your IP. Postgres provenance table \+ linking logic from every Pydantic field to source bbox. \~400 LOC. |

**Weighted average coverage: \~70% of total LOC is wrapped OSS; \~30% is the custom layer that is the actual platform wedge.**

This matches your thesis prediction almost exactly. The middle of the stack is commoditized; the schema/calibration/provenance spine is custom and is precisely what's defensible.

## **What this does to the 6-week estimate**

The original estimate had \~1,100 LOC of custom code across four modules. The coverage map says that's still right — the OSS doesn't shrink the custom layer, it shrinks the *plumbing* around it. So the time savings are concentrated in weeks 1–2 (stack provisioning, ingest) and partially week 5 (HIL UI scaffolding).

**Revised estimate: 5 weeks instead of 6**, with the saved week reallocated to deeper calibration work in week 4 (which the search confirmed is the most novel piece and the place where shortcuts hurt most).

| Week | Original scope | Revised with OSS reuse |
| ----- | ----- | ----- |
| 1 | Stack \+ dataset prep, \~30 hrs | **\~18 hrs.** Fork `mfmezger/conversational-agent-langchain` or JARVIS compose, strip what you don't need, add LiteLLM \+ Unstructured. Dataset prep unchanged. |
| 2 | Extract pipeline end-to-end, \~35 hrs | **\~25 hrs.** Instructor \+ LangGraph \+ Langfuse cookbook gets you to a green pipeline fast. |
| 3 | Eval harness \+ failure-mode library, \~30 hrs | **\~30 hrs.** Roughly unchanged — `stephenleo/llm-structured-output-benchmarks` gives you the F1/precision/recall scaffolding, but the failure-mode library is yours to curate. |
| 4 | Calibration \+ provenance, \~35 hrs | **\~50 hrs.** Spend the saved time here. This is your IP and the OSS coverage is thin. Implement both global Platt scaling and fine-grained per-field calibration to compare; the April 2026 paper says fine-grained matters. |
| 5 | HIL routing \+ review UI, \~30 hrs | **\~30 hrs.** Unchanged — this is genuinely custom. |
| 6 | Methodology write-up, \~25 hrs | **\~25 hrs.** Unchanged — and still the most important week. |

**Revised total: \~178 hours over 5 weeks** instead of 185 over 6\.

## **Three specific repos to read this week before you start**

If you do nothing else before week 1:

1. **`langfuse/langfuse-docs/cookbook/integration_langgraph.ipynb`** — this is the exact wiring pattern between your runtime and your observability layer. 30 minutes to read, saves 4 hours of fumbling.  
2. **`stephenleo/llm-structured-output-benchmarks`** — read the F1/precision/recall scaffolding. You'll lift the eval harness shape from this; don't reinvent it.  
3. **`opendatalab/MinerU`** or Unstructured.io's docs — pick one ingest engine in week 1 and commit. The DP-Bench numbers in the NovaLAD paper suggest MinerU is competitive; Unstructured.io is more mature operationally. For FUNSD specifically, either works.

## **The honest read**

The OSS coverage is better than your thesis assumed when you wrote it, in two specific ways: (a) the Docker Compose templates have matured to the point where stack provisioning is a fork-and-strip exercise, not a build; (b) Instructor has effectively eaten the "structured extraction" niche and is now the boring default. Neither of those changes the platform wedge — schema registry, calibration, provenance — but both compress the timeline to *get to* that wedge.

The honest test is week 4\. If your calibration layer \+ provenance layer takes 50 hours and produces a measurably better-calibrated extractor than vanilla Instructor on FUNSD, the productized-FDE thesis has a real artifact behind it. If it takes 50 hours and you can't show calibration improvement on a reliability diagram, the thesis needs another round before you take it to a customer.

One concrete next step: fork one of the compose templates today (my pick: `mfmezger/conversational-agent-langchain`, because it already has LangGraph \+ Qdrant \+ Phoenix wired together and is closest to your target shape), and get `docker compose up` green on your laptop before Monday. That's 2 hours of work and it tells you whether the stack you specced actually runs. If it does, week 1 starts on solid ground. If it doesn't, you find out before you've committed your engineer's time. Want me to draft the specific fork-and-strip checklist for that template?

