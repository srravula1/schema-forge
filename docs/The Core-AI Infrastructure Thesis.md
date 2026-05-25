# The Core-AI Infrastructure Thesis

### What you'd actually build once if one team built the AI-dependent products in this YC cofounder pool

---

**v2 UPDATE (442-idea dataset).** This thesis was originally written on 319 ideas. The dataset has since grown to **442 ideas** (123 appended, some being expanded re-entries of the same founder/product). Re-running the full classification and pattern-mapping on all 442:

- **Tier A: 140 · Tier B: 61 · Tier C: 241** (was 96 / 32 / 191\)  
- **The top-5 pattern ordering is unchanged:** P9 Doc-Generation (73) · P1 Doc-Extract (66) · P6 Predictive-Risk (53) · P4 Agent-Orchestration (48) · P8 Recommendation (44). The fact that the ordering survives a 38% increase in sample size is the strongest possible evidence the pattern structure is real and not an artifact of the original sample.  
- **Every conclusion below holds and strengthens.** The composite "ingest→extract→reason→generate→govern" spine now covers \~half of 140 Tier-A products. The build/wrap/buy verdicts are unchanged. Numbers in the body below are the original 319-figures; read them as directional — the 442 figures above are current.  
- Companion files: `YC_AI_Product_Classification.xlsx` (full per-product spreadsheet) and `Predictive_Risk_Harness_Deep_Dive.md` (Module E deep dive).

---

## TL;DR

Of **319 product ideas**, **96 are "Tier A"** — products where AI *is* the product or the moat — and **32 are "Tier B"** where AI is a major engine but the defensibility lives in data/network/distribution. The other **191 are Tier C**: marketplaces, directories, brokerages, and services businesses where you could delete the AI entirely and still have the product. Tier C is irrelevant to an AI-infrastructure thesis.

The 128 AI-dependent products **do not require 128 different AI systems**. They decompose into **\~15 recurring AI workflow patterns**, and the distribution is brutally concentrated: **five patterns cover the large majority of the portfolio**, and they are *vertical-agnostic*. The same "ingest messy documents → extract structured facts → generate a governed report → route low-confidence items to a human" pipeline is simultaneously: credit underwriting (LogiCov), physician credentialing (AICAP), construction-delay prediction (DelayIQ), accreditation management (Accreditopia), insurance-claim analysis (AiClaims 365), and biopharma portfolio management (Phlira).

**The infrastructure play is real**, but the honest finding is this: **most of the modules already exist as mature open source.** Calling an LLM is not the moat — you already knew that — but neither is RAG, agent orchestration, voice loops, or doc extraction *generically*. The defensible layer is narrow and specific, and I name it in Part 5\.

---

## Part 1 — Classification: which products are actually core-AI

### The three tiers

| Tier | Definition | Count | What it means |
| :---- | :---- | :---- | :---- |
| **A — AI is the moat** | Remove the model and there is no product; defensibility \= model/AI-system quality, proprietary eval, or expert-labeled data feeding a model | **96** | These define the infrastructure requirements |
| **B — AI-enabled** | AI is a major engine but the moat is network effects, inventory, regulatory position, or distribution | **32** | They consume the same infra but won't fund it alone |
| **C — AI-incidental** | "We'll add AI" sprinkled on a marketplace/SaaS/services business; AI is removable | **191** | Excluded from this analysis |

A note on method: a keyword scorer (counting "AI", "automate", "optimize", "predictive") tags \~107 as core-AI, but that over-counts — half of those say "AI-powered" the way 2021 startups said "blockchain". The classification here is read-by-hand. The dividing question is: **"If frontier models were 30% worse, does this product still work?"** If yes → not Tier A.

### Representative Tier-A products (the ones that prove the patterns)

- **Document-intelligence engines:** LogiCov (credit memos), AICAP (physician credentialing), Accreditopia (accreditation), AiClaims 365 (insurance claims), Exact NAV (fund accounting), Phlira / AI Biopharma PM (portfolio mgmt), AIPER (satellite-mfr docs), Loan Sheet (loan underwriting), Foia Agent (public records), AI Lab Procurement Agent  
- **Predictive risk on operational data:** DelayIQ (schedule slip), Axiomic (construction-portfolio risk), Stellarus (SMT factory), Workforce Risk Intelligence, Insights (employment-legal risk), BayOS (collision-shop sequencing), AiFleetOS (trucking)  
- **RAG over a private/expert corpus:** Soar (parenting, "Harvey for parents"), TectorAI (knowledge-native firms), Atlas, Caddie (CAD copilot), Walid Rizk's service-as-software, Accreditopia  
- **Voice agent loops:** Falcco (tutor), Casgrain (sales roleplay), Straz (actor scene partner), Herald (exec assistant), Wiillow (school counseling), Si Tran (coaching infra), Zistful (live presentation coaching)  
- **Vision inspection:** ArchiMind (floor plans), AI Construction Progress (BIM vs footage), Stayfax ("Carfax for Airbnbs"), MyFitfix (food log), S18Labs (skill-feedback CV)  
- **The AI-infra-on-AI plays:** Egis AI (agent failure analysis), Polycentria (reasoning-state audit), iAloha (prompt-injection defense), MoirAI (causal AI) — these *are* infrastructure products themselves, which is a signal worth noting

---

## Part 2 — The AI workflow patterns

Every Tier-A/B product was decomposed into the actual sequence of model operations it requires. Fifteen patterns account for all 128 products. Frequency (number of AI-dependent products that need each):

| \# | Pattern | Products | One-line definition |
| :---- | :---- | ----: | :---- |
| **P9** | **Document / artifact generation** | **47** | Generate a governed long-form artifact: memo, report, plan, proposal, with rules & house style |
| **P1** | **Document ingest → structured extract** | **41** | Messy PDF/email/scope/photo → typed structured fields & entities |
| **P6** | **Predictive risk / forecast** | **37** | Score or forecast over tabular \+ text \+ time-series (slip, churn, credit, burnout) |
| **P2** | **RAG over a private corpus** | **30** | Grounded Q\&A/generation over a private or expert knowledge base |
| **P4** | **Agent / multi-agent orchestration** | **30** | Multi-step tool-using task execution with state & retries |
| **P8** | **Recommendation / taste profile** | **27** | Personalized reco built on a learned behavior/taste profile |
| **P5** | **Real-time voice agent loop** | **22** | STT → LLM → TTS at conversational latency, with turn-taking |
| **P11** | **Streaming event / crisis detection** | **13** | Live signal → anomaly/safety/crisis event → alert |
| **P13** | **Adaptive diagnostic scoring** | **12** | Psychometric/behavioral engine that diagnoses *why*, not just *what* |
| **P3** | **Knowledge graph / GraphRAG** | **10** | Entity-relationship extraction into a queryable/causal graph |
| **P7** | **Vision inspection** | **10** | Image/video → detection/measurement → condition report |
| **P15** | **Human-in-loop review harness** | **7** | Confidence-gated routing of AI output to human approval |
| **P10** | **Simulation / roleplay** | **6** | Generative scenario for practice or scored assessment |
| **P12** | **Generative media pipeline** | **6** | Video/voice/animation/3D production |
| **P14** | **AI eval / observability** | **3** | Monitoring/audit/guardrails for AI systems themselves |

**The single most important observation:** P1 \+ P9 \+ P15 together form one composite pipeline — *"ingest → extract → reason → generate → govern"* — and that composite is the spine of roughly **half the Tier-A products**, spanning healthcare, construction, finance, legal, and biopharma. The vertical changes; the pipeline does not. That is the entire infrastructure argument in one sentence.

---

## Part 3 — Are these patterns modular? Yes, and the boundaries are clean

The patterns aren't just thematically similar — they have **stable interfaces**, which is the real test of modularity. A module is only worth extracting if its boundary doesn't move when you change verticals. These do:

                          ┌─────────────────────────────────────┐

                          │   PRODUCT LAYER (96 Tier-A apps)     │

                          │  vertical UI, domain logic, GTM      │

                          └───────────────┬─────────────────────┘

                                          │ stable API contracts

        ┌──────────────┬─────────────┬────┴───────┬──────────────┬─────────────┐

        ▼              ▼             ▼            ▼              ▼             ▼

   ┌─────────┐   ┌──────────┐  ┌──────────┐ ┌──────────┐  ┌──────────┐ ┌──────────┐

   │ DOC I/O │   │   RAG /  │  │  AGENT   │ │ PREDICT  │  │  VOICE   │ │ GOVERN   │

   │ extract │   │ KNOWLEDGE│  │ ORCHESTR.│ │  RISK    │  │  LOOP    │ │ eval/HIL │

   │  (P1)   │   │ (P2/P3)  │  │  (P4)    │ │  (P6)    │  │  (P5)    │ │(P14/P15) │

   └────┬────┘   └────┬─────┘  └────┬─────┘ └────┬─────┘  └────┬─────┘ └────┬─────┘

        └─────────────┴─────────────┴────────────┴─────────────┴───────────┘

                                          │

                          ┌───────────────┴─────────────────────┐

                          │  FOUNDATION: model gateway, vector   │

                          │  store, doc store, queue, eval bus   │

                          └─────────────────────────────────────┘

- **The boundary that matters: a typed schema contract.** Every Tier-A app, regardless of vertical, hands the platform (a) a document/signal, (b) a target schema, (c) a policy/ruleset, and gets back (d) a structured result with confidence \+ provenance. AICAP's schema is "physician credential fields"; Phlira's is "clinical-program milestones"; DelayIQ's is "schedule activities \+ slip probability." Same contract, different schema. **The schema registry is the integration seam, and it's the same seam everywhere.**  
- **Boilerplate vs. core-AI infrastructure — your distinction is right.** Auth, billing, multi-tenancy, file storage, a model gateway → commodity boilerplate, buy or template it, never a moat. The six modules above are *core-AI infrastructure* and are the only thing worth a platform team's time.  
- The recommendation/taste-profile pattern (P8, 27 products) is the one near-exception: it's modular in shape but the value is the *data*, not the code. More on this in Part 5\.

---

## Part 4 — Does it already exist on GitHub? (the deep dive)

Short answer: **yes for almost every module, and they're mature.** This is the uncomfortable part of the thesis. Here's the honest landscape per module, with the build/buy/wrap verdict. Sources are 2026-current.

### Module A — Document ingest → structured extract (P1, 41 products)

| Option | License | Maturity | Notes |
| :---- | :---- | :---- | :---- |
| **Unstructured.io** | open core | high | de-facto preprocessing layer; layout-aware, OCR, tables, handwriting handles multi-column layouts, forms and tables, handwritten text detection, and scanned/smartphone-captured documents |
| **Unstract** | open source | high | no-code LLM platform to launch APIs and ETL pipelines that structure unstructured documents; deploy schema-extraction as an API in one click |
| **RAGFlow** | open source | high | strongest at extracting information from complex documents including tables and visual elements; built-in OCR/layout |
| **LLM-AIx** | open source (academic) | medium | privacy-preserving on-prem extraction, built for regulated (clinical) data — relevant for the healthcare Tier-A cluster |

**Verdict: WRAP, don't build.** The ingest→extract pipeline is solved. The *only* thing you build here is the **schema-registry \+ confidence-calibration layer** on top — and that piece *is* differentiating because it's where domain accuracy lives.

### Module B — RAG / knowledge corpus (P2, 30 products) & Knowledge graph (P3, 10\)

| Option | License | Role |
| :---- | :---- | :---- |
| **LlamaIndex** | MIT | retrieval-first; 300+ data connectors and sophisticated query engines for document-heavy retrieval; the default if the problem is "mountain of documents, accurate answers" |
| **LangChain / LangGraph** | MIT | orchestration \+ agentic RAG; pick LangGraph when building agentic systems with human-in-the-loop, state persistence, or cyclic workflows |
| **Haystack** (deepset) | Apache-2 | production systems where stability matters more than features; explicit, debuggable pipelines |
| **Microsoft GraphRAG** | MIT | community-aware knowledge graph from documents enabling local entity-centric and global theme-level queries — for the GraphRAG/causal cluster (Walid Rizk, TectorAI, MoirAI) |
| **R2R / RAGFlow** | open source | production-ready RAG with built-in agentic reasoning, hybrid search, automatic citations |
| **RAGAS** | open source | the evaluation half — context precision, context recall, faithfulness, answer relevancy, framework-agnostic |

**Verdict: WRAP \+ COMPOSE.** No single framework wins; the best production stacks in 2026 are compositional — a retrieval layer, an orchestration layer, and an evaluation layer working together. The 2026 consensus pattern: **LlamaIndex for ingestion/indexing \+ LangGraph for orchestration \+ RAGAS for eval.** Build nothing here except the corpus-governance and citation-provenance policy.

### Module C — Agent / multi-agent orchestration (P4, 30 products)

| Option | License | Best for |
| :---- | :---- | :---- |
| **LangGraph** | MIT | The production default. The production standard in 2026 for stateful, auditable agentic workflows, especially regulated environments where auditability, deterministic control, and human approval steps matter. MIT-licensed, built-in memory, native human-in-the-loop checks |
| **CrewAI** | open source | Fastest prototype; role-based crews, code reads like English, \~18% token overhead vs LangGraph. Teams outgrow it for production |
| **AutoGen / AG2** | open source | Conversational multi-agent; Microsoft shifted strategic focus away; major new feature development has slowed — avoid for new builds |
| **OpenAI Agents SDK** | open source | Clean handoffs but model-locked to OpenAI, no BYOM, no built-in checkpointing — disqualifying for a multi-model platform |

**Verdict: BUILD-ON LangGraph.** This is the orchestration backbone. It's MIT, model-agnostic, and has the auditability the regulated Tier-A products (credentialing, credit, legal) require. You build the **domain workflow graphs** on top — those *are* product IP — not the runtime.

### Module D — Real-time voice agent loop (P5, 22 products)

| Option | License | Notes |
| :---- | :---- | :---- |
| **Pipecat** (Daily) | open source (BSD) | The reference framework. Vendor-agnostic, 100% open source, reached v1.0.0 on April 14, 2026; 20+ STT providers, 20+ LLMs, 30+ TTS engines, WebRTC/WebSocket transports, subagents and Flows for stateful dialog |
| **LiveKit Agents** | open source (Apache-2) | v1.5.6 (April 2026\) with adaptive interruption handling at 86% precision/100% recall and preemptive generation by default |
| **Self-host stack** | mixed OSS | Pipecat \+ Ollama \+ Speaches (faster-whisper) \+ Kokoro TTS over WebRTC for full data sovereignty (matters for the healthcare voice products) |

**Verdict: WRAP Pipecat or LiveKit.** Real-time voice plumbing (turn-taking, interruption, sub-second latency) is genuinely hard and fully solved by these. Building it from scratch would be the single biggest waste in the portfolio. The product value is the *conversation design \+ domain grounding*, not the pipeline.

### Module E — Predictive risk / forecast (P6, 37 products)

This is the **least "GitHub-solved"** module and it's the most interesting. There's no "LangChain for predictive risk." It's classical ML (gradient-boosted trees on tabular features \+ text embeddings \+ time-series), and the open source is the *primitives* (XGBoost/LightGBM, sktime/Nixtla for forecasting, scikit-learn, feature stores like Feast), not a turnkey module. Each Tier-A predictive product (DelayIQ, Stellarus, Workforce Risk, Insights) needs **its own labeled outcome data and feature engineering**.

**Verdict: BUILD the harness, the data is the moat.** This is the one core-AI module where building is correct — not because the algorithms are secret (they're commodity) but because the **labeled outcome dataset per vertical is the actual defensibility**. This is the module that justifies a studio model: shared feature-store \+ training-harness infrastructure, vertical-specific label data owned per product.

### Module F — Govern: eval, observability, human-in-loop, guardrails (P14 \+ P15, 10 products — and *every* product needs it)

| Option | License | Role |
| :---- | :---- | :---- |
| **Langfuse** | MIT core | open-source observability with self-hosting; detailed trace logging of LLM calls, retrieval, embeddings, tool usage; prompt version control, A/B testing, LLM-as-judge |
| **RAGAS / DeepEval / TruLens** | open source | eval metrics; RAGAS for retrieval eval, DeepEval for CI/CD validation, pair with Langfuse for traceability |
| **LLM Guard** (Protect AI) | open source | input scanners for prompt-injection detection and PII anonymization; output scanners for content moderation and malicious-URL detection — this is literally what iAloha proposes to build |
| **MLflow** | Apache-2 | built-in LLM judges, multi-turn eval, integration with RAGAS/DeepEval/Phoenix/TruLens/Guardrails AI, plus GEPA/MIPRO prompt optimization |

**Verdict: WRAP for the harness; the AI-on-AI products (Egis AI, Polycentria, iAloha) are partially pre-empted by OSS.** Honest note for the founders in this pool: iAloha's prompt-injection defense substantially overlaps with LLM Guard; the differentiation has to be the *trust-scoring/hardware-binding* layer, not the injection detection itself. Egis AI overlaps with Langfuse \+ agent-eval tooling. This is useful competitive intel.

---

## Part 5 — Synthesis: what one team should actually build

### The build / wrap / buy verdict, consolidated

| Module | Pattern(s) | Products served | Verdict | Why |
| :---- | :---- | ----: | :---- | :---- |
| Doc ingest → extract | P1 | 41 | **WRAP** (Unstructured/Unstract/RAGFlow) | solved; build only the schema registry |
| RAG / knowledge / graph | P2,P3 | 34 | **COMPOSE** (LlamaIndex+LangGraph+RAGAS) | solved; build only corpus governance |
| Agent orchestration | P4 | 30 | **BUILD-ON** LangGraph | runtime is OSS; the workflow graphs are IP |
| Voice loop | P5 | 22 | **WRAP** Pipecat/LiveKit | hard, fully solved, never build |
| Predictive risk | P6 | 37 | **BUILD the harness; OWN the labels** | only true build; data is the moat |
| Govern (eval/HIL/guardrails) | P14,P15 | all | **WRAP** Langfuse+LLM Guard | solved; thin policy layer on top |
| Recommendation / taste | P8 | 27 | **BUILD light; OWN the data** | code is trivial; proprietary signals are everything |
| Media gen | P12 | 6 | **WRAP** (model APIs) | not enough volume to justify infra |
| Diagnostic scoring | P13 | 12 | **BUILD** (psychometrics \+ IRT) | genuinely specialized, low OSS coverage |

### The honest conclusion

**Calling an LLM is generic — and so is RAG, agent orchestration, voice, and doc extraction, *as generic capabilities*.** The 2026 OSS ecosystem has commoditized the entire middle of the stack. If the thesis was "build the AI infrastructure layer and license it" — that layer largely exists, is MIT/Apache licensed, and is maintained by well-funded teams. Competing with LangGraph or Pipecat head-on is a losing game.

**Where the defensibility actually concentrates — three places only:**

1. **The schema-registry \+ confidence-calibration \+ provenance layer that sits *between* the wrapped OSS modules and the vertical app.** This is the "ingest→extract→reason→generate→govern" spine, productized with per-vertical schemas, accuracy SLAs, and audit trails. Nobody open-sources *your* credentialing schema with *your* calibration on *your* error distribution. This is buildable in months on top of OSS and is the natural platform wedge.  
     
2. **Vertical labeled outcome data for the predictive-risk module (P6).** DelayIQ's value isn't "we use XGBoost"; it's "we have N years of construction schedules labeled with which activities actually slipped." A studio that builds shared predictive infrastructure and accumulates labeled outcomes across verticals has a compounding moat the OSS can't touch.  
     
3. **Proprietary behavioral signals for the recommendation layer (P8).** NovelNest's pitch is explicitly *"collecting different data points than competitors — a taste profile for AI."* The reco code is a weekend; the data network is the company.

**The studio-model recommendation:** build the **Module-A-through-F wrapper platform \+ the schema/calibration spine (defensibility \#1)** as shared internal infrastructure. Spin out Tier-A products on top of it, choosing first the ones whose **labeled data compounds** (predictive-risk verticals: DelayIQ-style construction, Stellarus-style manufacturing, Workforce Risk-style HR) — because that's where the wrapped-OSS commodity turns into a moat you own. The composite "doc-intelligence-as-a-service" spine alone could be a single platform company validated against the \~20 Tier-A document-intelligence products simultaneously.

---

## Appendix — Method & caveats

- Classification is hand-read against the "would it survive 30%-worse models?" test; reasonable people would move \~10–15 products between A and B at the margin. The pattern distribution is robust to that noise.  
- "Exists on GitHub" reflects the 2026 OSS landscape; this moves fast — re-check the agent-orchestration and voice space every \~6 months as it's consolidating rapidly.  
- Tier-C products (191) were excluded by design; if you want the full per-product tier assignment and pattern map as a spreadsheet, that's a quick follow-on.  
- This analysis assumed an OSS-first / studio-model framing (inferred from your prompt: "leverage existing modules rather than building from scratch"). A speed-first, API-wrap-everything framing would shift Modules B/C from COMPOSE/BUILD-ON toward pure WRAP and shorten time-to-first-product at the cost of long-run margin and data sovereignty.

