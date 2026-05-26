# schema-forge

A standalone, CLI-driven **schema generator**. It takes a domain *baseline* plus a
buyer's interview-derived *overrides* and emits the five artifacts the OSS **spine**
(a separate repo) consumes. v0 ships exactly one engagement: the AI-consulting GTM schema.

## Workflow

```
init  ->  fill interview markdown  ->  extract-overrides  ->  review  ->  generate  ->  validate  ->  handoff
```

- `init` scaffolds an engagement directory from the domain baseline + interview templates.
- `extract-overrides` LLM-normalizes filled interviews into structured override YAML (you review before generating).
- `generate` deterministically merges baseline + overrides into the five output artifacts (no LLM; byte-deterministic).
- `validate` runs a sanity battery over the output.
- Handoff to the spine is a deliberate, manual copy.

## Scope (v0)

- **CLI + YAML/JSON only** — no UI.
- **No database, no multi-tenancy** — one repo clone per engagement.
- **Files-only contract with the spine** — neither repo imports the other (see [docs/INTERFACE.md](docs/INTERFACE.md)).
- **GTM domain only** — new domains are added later by copying the GTM module, not by building configurability now.
- Does **not** run extraction, eval, or ingest — that is the spine's job.

See [docs/schema_forge_plan.md](docs/schema_forge_plan.md) for the full plan and roadmap,
and [CLAUDE.md](CLAUDE.md) for contributor conventions.

## Develop

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
schema-forge --help
```
