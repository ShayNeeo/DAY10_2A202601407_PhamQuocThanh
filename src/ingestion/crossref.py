import json
import logging
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import requests

from core.config import Settings
from core.utils import read_json, write_json


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_abstract(raw: str) -> str:
    if not raw:
        return ""
    # Strip JATS XML tags from Crossref abstracts
    cleaned = re.sub(r"<[^>]+>", "", raw)
    return cleaned.strip()


def parse_crossref_payload(payload: dict[str, Any]) -> list[PaperRecord]:
    """Parse Crossref API response items into list of PaperRecord objects."""
    items = payload.get("message", {}).get("items", [])
    records: list[PaperRecord] = []

    for item in items:
        doi = item.get("DOI", "")
        titles = item.get("title", [])
        title = titles[0] if titles else ""
        raw_abstract = item.get("abstract", "")
        summary = _clean_abstract(raw_abstract)

        if not doi or not title:
            continue

        authors_list = []
        for a in item.get("author", []):
            given = a.get("given", "")
            family = a.get("family", "")
            name = f"{given} {family}".strip() or a.get("name", "")
            if name:
                authors_list.append(name)

        categories = item.get("subject", [])
        primary_category = categories[0] if categories else "General"

        # Publication date parsing
        pub_parts = item.get("published-print", {}).get("date-parts") or item.get("published-online", {}).get("date-parts") or item.get("issued", {}).get("date-parts") or []
        if pub_parts and pub_parts[0]:
            dp = pub_parts[0]
            year = dp[0] if len(dp) > 0 else 2026
            month = dp[1] if len(dp) > 1 else 1
            day = dp[2] if len(dp) > 2 else 1
            published = f"{year:04d}-{month:02d}-{day:02d}"
        else:
            published = "2026-01-01"

        paper_id = doi.replace("/", "_").replace(":", "_")
        url = item.get("URL", f"https://doi.org/{doi}")

        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title.strip(),
                summary=summary,
                authors=authors_list or ["Unknown"],
                categories=categories or ["General"],
                primary_category=primary_category,
                published=published,
                updated=published,
                abs_url=url,
                pdf_url=url,
                comment="",
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Fetch metadata from Crossref REST API with backoff/retry, write raw files, and return records."""
    url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results,
    }
    headers = {"User-Agent": "Day10ObservabilityLab/1.0 (mailto:student@example.com)"}

    payload = {}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code == 200:
                payload = resp.json()
                break
            elif resp.status_code in {429, 503}:
                logging.warning("Crossref returned status %d. Retrying (%d/%d)...", resp.status_code, attempt + 1, max_retries)
                time.sleep(2 * (attempt + 1))
            else:
                resp.raise_for_status()
        except Exception as exc:
            if attempt == max_retries - 1:
                logging.error("Failed to fetch from Crossref after retries: %s", exc)
                raise
            time.sleep(2)

    # Persist raw response
    write_json(settings.paths.raw_api_response, payload)

    # Parse records
    records = parse_crossref_payload(payload)

    # Persist parsed records
    records_dict = [asdict(r) for r in records]
    write_json(settings.paths.raw_records_json, records_dict)

    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Load JSON raw records snapshot and return PaperRecord instances."""
    data = read_json(path)
    records = []
    for item in data:
        records.append(
            PaperRecord(
                paper_id=item["paper_id"],
                title=item["title"],
                summary=item["summary"],
                authors=item.get("authors", []),
                categories=item.get("categories", []),
                primary_category=item.get("primary_category", "General"),
                published=item.get("published", "2026-01-01"),
                updated=item.get("updated", "2026-01-01"),
                abs_url=item.get("abs_url", ""),
                pdf_url=item.get("pdf_url", ""),
                comment=item.get("comment", ""),
            )
        )
    return records
