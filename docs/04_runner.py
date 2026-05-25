# ============================================================
# A) New file: spine/ingest/__main__.py addition (or a new module
#    spine/ingest/run_websites.py) — the CLI entrypoint.
# ============================================================

# spine/ingest/run_websites.py
"""
CLI: read URLs from a file (one per line), ingest + extract them under gtm@v1.

Usage:
    .venv/bin/python -m spine.ingest.run_websites \\
        --urls urls.txt \\
        --schema gtm@v1
"""
import argparse
import json
from pathlib import Path

from spine.ingest.website import load_websites
from spine.extract.pipeline import extract_document
from spine.db import get_conn


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--urls", type=Path, required=True, help="file with one URL per line")
    p.add_argument("--schema", default="gtm@v1")
    p.add_argument("--dataset", default="gtm")
    args = p.parse_args()

    urls = [
        line.strip()
        for line in args.urls.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    print(f"[1/2] ingesting {len(urls)} URLs...")
    ingest_summary = load_websites(urls, dataset=args.dataset)
    print(json.dumps(ingest_summary, indent=2))

    # Now run the SAME extract pipeline that runs on FUNSD and CORD.
    # No changes to extract/pipeline.py — it loads the schema by name,
    # builds the prompt from extraction_guidance(), validates, persists,
    # records provenance, gates by calibrated confidence into HIL.
    print(f"[2/2] extracting under schema {args.schema}...")
    with get_conn() as conn:
        # fetch the doc_ids we just ingested
        rows = conn.execute(
            "SELECT source_doc_id FROM documents WHERE dataset = %s AND split = %s",
            (args.dataset, "ingest"),
        ).fetchall()
        for (doc_id,) in rows:
            try:
                result = extract_document(doc_id=doc_id, schema_name=args.schema)
                print(f"  {doc_id}: {result['entity_count']} entities, "
                      f"{result['failed_chunks']} failed chunks")
            except Exception as e:
                print(f"  {doc_id}: EXTRACTION_FAILED {e!r}")

    print("done. inspect results with:")
    print(f"  SELECT * FROM extractions WHERE schema_version = '{args.schema}';")
    print(f"  SELECT * FROM provenance WHERE schema_version = '{args.schema}';")
    print(f"  SELECT * FROM review_queue WHERE schema_version = '{args.schema}';")


if __name__ == "__main__":
    main()


# ============================================================
# B) Makefile addition — one new target.
# ============================================================
#
# Append to your existing Makefile:
#
# ----------------------------------------------------------------
# gtm-load-and-extract:                                            ## ingest websites + extract under gtm@v1
# 	@test -f $(URLS) || (echo "Usage: make gtm-load-and-extract URLS=urls.txt"; exit 1)
# 	$(PY) -m spine.ingest.run_websites --urls $(URLS) --schema gtm@v1
# ----------------------------------------------------------------
#
# Then use it:
#
#   $ cat > urls.txt <<EOF
#   https://www.acme.com/about
#   https://www.acme.com/customers
#   https://www.contoso.io
#   ... (97 more)
#   EOF
#
#   $ make gtm-load-and-extract URLS=urls.txt
