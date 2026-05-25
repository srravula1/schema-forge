"""
spine/ingest/website.py — website ingest adapter for gtm@v1.

Mirrors spine/ingest/cord.py exactly: a per-vertical adapter that normalizes
a new source format into the spine's universal (documents, words) shape.
Reuses spine/ingest/store.py and spine/db.py UNCHANGED.

The spine's contract:
    Word = {source_doc_id, page, bbox, text}

For websites: page = 1 (no pagination), bbox = placeholder (HTML has no geometry,
same as FUNSD/CORD text-only mode). The honest read: bboxes here are even more
placeholder than CORD's. Real provenance-to-source linkage for websites would
need DOM-path or character-offset tracking, which is a Phase-3.5 lever, not v1.

Dependencies (add to pyproject.toml extras under [stack]):
    httpx>=0.27      # async HTTP with timeouts + retries
    selectolax       # fast HTML→text, handles malformed markup
    trafilatura      # boilerplate stripping (nav/footer/ads), the de-facto OSS pick
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse

import httpx
import trafilatura

from spine.ingest.models import Word, Document
from spine.ingest.store import upsert_document, upsert_words
from spine.db import get_conn

log = logging.getLogger(__name__)

# Conservative defaults. Override per-engagement.
HTTP_TIMEOUT_S = 20
HTTP_CONCURRENCY = 8         # be polite — don't hammer customer prospects
USER_AGENT = "SchemaSpine-Ingest/0.1 (+contact: you@example.com)"
MAX_BYTES_PER_PAGE = 2_000_000  # 2MB cap — refuse weirdly huge pages


@dataclass
class FetchResult:
    url: str
    doc_id: str
    status: int
    text: str | None
    error: str | None


def _doc_id_for(url: str) -> str:
    """Stable doc ID from URL hash. Lets you re-ingest idempotently."""
    return "web_" + hashlib.sha1(url.encode()).hexdigest()[:16]


async def _fetch_one(client: httpx.AsyncClient, url: str, sem: asyncio.Semaphore) -> FetchResult:
    doc_id = _doc_id_for(url)
    async with sem:
        try:
            r = await client.get(url, follow_redirects=True, timeout=HTTP_TIMEOUT_S)
        except httpx.HTTPError as e:
            return FetchResult(url, doc_id, status=-1, text=None, error=f"http_error: {e!r}")

        if r.status_code != 200:
            return FetchResult(url, doc_id, status=r.status_code, text=None, error=f"http_{r.status_code}")

        if len(r.content) > MAX_BYTES_PER_PAGE:
            return FetchResult(url, doc_id, status=r.status_code, text=None, error="too_large")

        # trafilatura strips nav/footer/ads, keeps main content as plain text.
        # Returns None if the page is empty / JS-rendered / paywall-blocked.
        text = trafilatura.extract(
            r.text,
            include_comments=False,
            include_tables=True,
            favor_recall=False,  # favor precision — fewer false-positive text spans
        )
        if not text or len(text.strip()) < 100:
            return FetchResult(url, doc_id, status=r.status_code, text=None, error="empty_after_extract")

        return FetchResult(url, doc_id, status=r.status_code, text=text, error=None)


async def fetch_many(urls: Iterable[str]) -> list[FetchResult]:
    """Fetch + extract main text from a list of URLs, concurrently."""
    sem = asyncio.Semaphore(HTTP_CONCURRENCY)
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en"}
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [_fetch_one(client, url, sem) for url in urls]
        return await asyncio.gather(*tasks)


def text_to_words(text: str, source_doc_id: str) -> list[Word]:
    """
    Tokenize cleaned text into the spine's Word shape.

    For HTML: page=1, bbox=[0,0,0,0] placeholder (same as CORD's text-only mode).
    One word per whitespace token — matches FUNSD/CORD granularity so eval/f1.py works.
    """
    words: list[Word] = []
    for tok in text.split():
        words.append(Word(
            source_doc_id=source_doc_id,
            page=1,
            bbox=[0, 0, 0, 0],   # placeholder, same convention as CORD text-only
            text=tok,
        ))
    return words


def load_websites(urls: list[str], dataset: str = "gtm") -> dict:
    """
    Entry point: fetch N URLs, normalize, persist into Postgres.
    Returns a small summary the runner prints.

    No gold entities — websites are not pre-labeled. This is unsupervised ingest.
    F1 will not be computable until you produce a small labeled set (the
    "benchmark call" output from your methodology).
    """
    results = asyncio.run(fetch_many(urls))

    persisted, failed = 0, []
    with get_conn() as conn:
        for r in results:
            if r.error or r.text is None:
                failed.append({"url": r.url, "error": r.error, "status": r.status})
                continue

            doc = Document(
                source_doc_id=r.doc_id,
                dataset=dataset,
                split="ingest",          # no train/dev/test — this is inference-time data
                source_uri=r.url,
                page_count=1,
            )
            upsert_document(conn, doc)
            words = text_to_words(r.text, r.doc_id)
            upsert_words(conn, r.doc_id, words)
            persisted += 1

    return {
        "requested": len(urls),
        "persisted": persisted,
        "failed_count": len(failed),
        "failed": failed[:10],   # cap the print
    }
