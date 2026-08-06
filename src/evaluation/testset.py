from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import write_json


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """Generate evaluation Q&A pairs from clean dataframe and save to output_path."""
    if df.empty:
        items: list[dict[str, Any]] = []
        write_json(Path(output_path), items)
        return items

    items = []
    idx = 1
    for _, row in df.iterrows():
        paper_id = str(row.get("paper_id", ""))
        title = str(row.get("title", ""))
        summary = str(row.get("summary", ""))
        authors = str(row.get("authors_joined", ""))
        published = str(row.get("published", ""))
        categories = str(row.get("categories_joined", ""))

        if not paper_id or not title:
            continue

        # Summary question
        if summary:
            items.append({
                "id": f"eval_{idx:03d}",
                "question_type": "summary",
                "question": f"What is the main summary or objective of the paper '{title}'?",
                "ground_truth": summary,
                "ground_truth_doc_ids": [paper_id],
            })
            idx += 1

        # Authors question
        if authors and authors != "Unknown":
            items.append({
                "id": f"eval_{idx:03d}",
                "question_type": "authors",
                "question": f"Who are the authors of the paper '{title}'?",
                "ground_truth": authors,
                "ground_truth_doc_ids": [paper_id],
            })
            idx += 1

        # Date question
        if published:
            items.append({
                "id": f"eval_{idx:03d}",
                "question_type": "date",
                "question": f"When was the paper '{title}' published?",
                "ground_truth": published,
                "ground_truth_doc_ids": [paper_id],
            })
            idx += 1

        # Categories question
        if categories and categories != "General":
            items.append({
                "id": f"eval_{idx:03d}",
                "question_type": "categories",
                "question": f"What domain or categories does the paper '{title}' belong to?",
                "ground_truth": categories,
                "ground_truth_doc_ids": [paper_id],
            })
            idx += 1

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_p, items)
    return items
