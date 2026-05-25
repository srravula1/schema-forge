# schema-forge — Claude Code project guide

## What this is
A standalone, CLI-driven **schema generator**. It takes a domain *baseline* plus a
buyer's interview-derived *overrides* and emits the five artifacts that the OSS
**spine** (a separate repo) consumes. v0 ships exactly one engagement: the
AI-consulting GTM schema.

Canonical references (read before changing scope):
- `docs/schema_forge_plan.md` — the plan this repo implements (scope, roadmap, CLI, merge semantics).
- `docs/gtm_schema_context.md` — how the five GTM baseline artifacts are sourced (Path B).
- `docs/The Core-AI Infrastructure Thesis.md`, `docs/Building Schema registry platform spine.md` — why the spine exists.
- `docs/gtm.py`, `docs/test_gtm_schema.py`, `docs/0*_*.py` — reference artifacts showing the target format (LLM-generated drafts; port, don't import).

## What it is NOT (scope cuts — honor these)
- **Not a UI.** CLI + YAML/JSON inputs only.
- **Not multi-tenant.** No auth, no DB. One repo clone per engagement.
- **Not coupled to the spine.** This repo outputs files; the spine imports nothing
  from here and this repo imports nothing from the spine. The interface is the
  file format (`docs/INTERFACE.md`), not a Python import. A test/grep enforces no spine import.
- **Not a generic any-domain generator yet.** v0 is GTM only. New domains are added
  by copying the GTM module (Stage 3), not by building configurability now.
- **Does not run extraction, eval, or ingest** — that is the spine's job.
- **Off-roadmap, do not build:** auto-domain-detection from samples, LLM "schema
  discovery" without operator interviews, a web-based interview tool.

## Pipeline
`init` (scaffold engagement) → fill interview markdown → `extract-overrides`
(LLM normalizes free-text answers into structured override YAML; **human reviews
before generate**) → `generate` (deterministic merge, **no LLM**, byte-deterministic) →
`validate` → manual, documented handoff to the spine.

Engagement directory: `01_interview_inputs/ 02_baseline/ 03_overrides/ 04_output/ manifest.yaml`.

Five artifacts produced: schema `.py`, modifiers `.yaml`, policy `.py`,
`failure_modes/` dir, gold `.jsonl`.

## Conventions
- Python 3.11+, Pydantic v2. (The global TS-first preference does not apply here —
  this repo is Python to match the spine and the artifact format.)
- `generate` must stay LLM-free and deterministic: identical inputs → byte-identical outputs.
- Every override entry carries a `rationale`; `manifest.yaml` is the audit trail —
  every change traces back to an interview answer.
- Baseline artifacts are citation-backed (Path B): every label, modifier, and
  failure mode cites a public source.
- `gtm@v1` is frozen at 30 labels; new labels come from buyer calls as `gtm@v2`.

## Discipline
The roadmap is staged around **engagements, not features**. Build v0 (Stage 1) only.
Stages 2–5 exist as deferred tracking issues — do not build them speculatively.
Do not factor out a reusable `forge_core/` until ≥3 engagements of pattern data exist.

## Commands
- `pytest` — run tests
- `schema-forge init | extract-overrides | generate | validate` — the CLI (see `--help`)
