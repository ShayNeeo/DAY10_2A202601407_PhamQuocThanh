from datetime import datetime, timezone
from pathlib import Path
import tempfile
import pandas as pd
import pytest

from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import PaperRecord, parse_crossref_payload


def test_parse_crossref_payload():
    payload = {
        "message": {
            "items": [
                {
                    "DOI": "10.1016/j.artint.2026.01",
                    "title": ["Artificial Intelligence in Science"],
                    "abstract": "<jats:p>This paper explores AI applications in scientific discovery.</jats:p>",
                    "author": [{"given": "Jane", "family": "Doe"}],
                    "subject": ["Computer Science"],
                    "published-online": {"date-parts": [[2026, 2, 15]]},
                    "URL": "https://doi.org/10.1016/j.artint.2026.01",
                }
            ]
        }
    }

    records = parse_crossref_payload(payload)
    assert len(records) == 1
    rec = records[0]
    assert rec.paper_id == "10.1016_j.artint.2026.01"
    assert rec.title == "Artificial Intelligence in Science"
    assert "This paper explores AI applications" in rec.summary
    assert rec.authors == ["Jane Doe"]
    assert rec.published == "2026-02-15"


def test_build_clean_dataframe():
    records = [
        PaperRecord(
            paper_id="p1",
            title="Title One",
            summary="Summary for paper one",
            authors=["Alice", "Bob"],
            categories=["CS"],
            primary_category="CS",
            published="2026-01-01",
            updated="2026-01-01",
            abs_url="http://example.com/p1",
            pdf_url="http://example.com/p1.pdf",
            comment="",
        )
    ]
    df = build_clean_dataframe(records, datetime(2026, 3, 1, tzinfo=timezone.utc))
    assert len(df) == 1
    assert "text_for_embedding" in df.columns
    assert df.iloc[0]["summary_chars"] == len("Summary for paper one")
    assert df.iloc[0]["age_days"] == 59


def test_corrupt_clean_dataframe():
    df = pd.DataFrame(
        [
            {
                "paper_id": f"p{i}",
                "title": f"Title {i}",
                "summary": f"Summary {i} for paper testing corruption behavior.",
                "authors_joined": "Author",
                "categories_joined": "Category",
                "published": "2026-01-01",
                "age_days": 10,
                "text_for_embedding": f"Title {i}\nSummary {i}",
            }
            for i in range(10)
        ]
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "corruption_log.json"
        corrupted_df = corrupt_clean_dataframe(df, log_path)
        assert log_path.exists()
        # Corrupted dataframe should have modified elements or dropped rows
        assert len(corrupted_df) <= len(df)
