from dataclasses import asdict
from datetime import datetime, timezone

import pandas as pd

from core.utils import compact_join, normalize_whitespace
from ingestion.crossref import PaperRecord


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Clean raw records into a structured DataFrame ready for embedding and indexing."""
    if not records:
        return pd.DataFrame(
            columns=[
                "paper_id",
                "title",
                "summary",
                "authors",
                "categories",
                "primary_category",
                "published",
                "updated",
                "abs_url",
                "pdf_url",
                "comment",
                "authors_joined",
                "categories_joined",
                "summary_chars",
                "age_days",
                "text_for_embedding",
            ]
        )

    rows = []
    for rec in records:
        r_dict = asdict(rec)
        title = normalize_whitespace(r_dict.get("title", ""))
        summary = normalize_whitespace(r_dict.get("summary", ""))

        if not title or not summary:
            continue

        authors_list = r_dict.get("authors") or ["Unknown"]
        categories_list = r_dict.get("categories") or ["General"]

        authors_joined = compact_join(authors_list)
        categories_joined = compact_join(categories_list)

        published_str = r_dict.get("published", "2026-01-01")
        try:
            pub_dt = pd.to_datetime(published_str)
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.tz_localize("UTC")
            ref_dt = run_date if run_date.tzinfo is not None else run_date.replace(tzinfo=timezone.utc)
            age_days = max(0, (ref_dt - pub_dt).days)
        except Exception:
            age_days = 0

        text_for_embedding = f"Title: {title}\nAuthors: {authors_joined}\nCategories: {categories_joined}\nSummary: {summary}"

        r_dict["title"] = title
        r_dict["summary"] = summary
        r_dict["authors_joined"] = authors_joined
        r_dict["categories_joined"] = categories_joined
        r_dict["summary_chars"] = len(summary)
        r_dict["age_days"] = age_days
        r_dict["text_for_embedding"] = text_for_embedding

        rows.append(r_dict)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["paper_id"]).reset_index(drop=True)
        df = df.sort_values(by="published", ascending=False).reset_index(drop=True)

    return df
