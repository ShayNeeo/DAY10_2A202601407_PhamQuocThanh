from pathlib import Path

import pandas as pd

from core.utils import write_json


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """Inject synthetic errors into DataFrame (drop rows, blank summary, noise, truncate, stale dates, duplicates)."""
    if df.empty:
        write_json(Path(output_log_path), {"corruptions": []})
        return df.copy()

    corrupt_df = df.copy()
    logs = []

    # 1. Drop latest rows (if > 3 rows)
    if len(corrupt_df) > 3:
        dropped_ids = list(corrupt_df.iloc[:2]["paper_id"])
        corrupt_df = corrupt_df.iloc[2:].reset_index(drop=True)
        logs.append({"corruption_type": "drop_latest_records", "affected_ids": dropped_ids, "count": 2})

    # 2. Blank summary on first row
    if len(corrupt_df) > 0:
        target_id = corrupt_df.at[0, "paper_id"]
        corrupt_df.at[0, "summary"] = ""
        logs.append({"corruption_type": "blank_summary", "affected_ids": [target_id]})

    # 3. Inject noise into summary on second row
    if len(corrupt_df) > 1:
        target_id = corrupt_df.at[1, "paper_id"]
        corrupt_df.at[1, "summary"] = "NOISE_STRING_CORRUPTED " * 5
        logs.append({"corruption_type": "inject_noise", "affected_ids": [target_id]})

    # 4. Truncate title on third row
    if len(corrupt_df) > 2:
        target_id = corrupt_df.at[2, "paper_id"]
        corrupt_df.at[2, "title"] = "Short"
        logs.append({"corruption_type": "truncate_title", "affected_ids": [target_id]})

    # 5. Make date stale (age_days > 180)
    if len(corrupt_df) > 0:
        target_id = corrupt_df.at[0, "paper_id"]
        corrupt_df.at[0, "published"] = "2020-01-01"
        corrupt_df.at[0, "age_days"] = 2000
        logs.append({"corruption_type": "stale_date", "affected_ids": [target_id]})

    # 6. Add duplicate row
    if len(corrupt_df) > 0:
        dup_row = corrupt_df.iloc[[0]].copy()
        corrupt_df = pd.concat([corrupt_df, dup_row], ignore_index=True)
        logs.append({"corruption_type": "add_duplicate", "affected_ids": [dup_row.iloc[0]["paper_id"]]})

    # 7. Entity Swap in summary (if > 0 rows)
    if len(corrupt_df) > 0:
        target_id = corrupt_df.at[0, "paper_id"]
        original_summary = str(corrupt_df.at[0, "summary"])
        # Swap common words to simulate factual contradiction/entity shift
        swapped_summary = (
            original_summary.replace("learning", "UNLEARNING_SWAPPED")
            .replace("model", "HALLUCINATED_ENTITY")
            .replace("data", "NOISY_DATA")
        )
        if swapped_summary == original_summary:
            swapped_summary = "[ENTITY_SWAPPED_FACT] " + original_summary
        corrupt_df.at[0, "summary"] = swapped_summary
        logs.append({"corruption_type": "entity_swap", "affected_ids": [target_id]})

    # 8. Metadata scramble on authors (if > 1 row)
    if len(corrupt_df) > 1:
        target_id = corrupt_df.at[1, "paper_id"]
        authors = str(corrupt_df.at[1, "authors_joined"]).split(", ")
        scrambled = ", ".join(reversed(authors)) + ", UNKNOWN_AUTHOR_CORRUPTED"
        corrupt_df.at[1, "authors_joined"] = scrambled
        logs.append({"corruption_type": "metadata_scramble", "affected_ids": [target_id]})

    # 7. Rebuild text_for_embedding
    corrupt_df["summary_chars"] = corrupt_df["summary"].astype(str).str.len()
    corrupt_df["text_for_embedding"] = (
        "Title: "
        + corrupt_df["title"].astype(str)
        + "\nAuthors: "
        + corrupt_df["authors_joined"].astype(str)
        + "\nCategories: "
        + corrupt_df["categories_joined"].astype(str)
        + "\nSummary: "
        + corrupt_df["summary"].astype(str)
    )

    out_p = Path(output_log_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    write_json(out_p, {"corruptions": logs, "total_corrupted_rows": len(corrupt_df)})

    return corrupt_df
