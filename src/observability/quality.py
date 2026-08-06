from pathlib import Path
from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Run data quality validation rules against dataframe and write quality report."""
    total_rows = len(df)
    if total_rows == 0:
        results = {
            "report_name": report_name,
            "passed": False,
            "total_rows": 0,
            "null_paper_ids": 0,
            "duplicate_paper_ids": 0,
            "null_titles": 0,
            "short_summaries": 0,
            "stale_rows": 0,
            "checks": {
                "row_count_check": False,
                "paper_id_not_null": False,
                "paper_id_unique": False,
                "title_not_null": False,
                "summary_length_check": False,
                "freshness_check": False,
            },
        }
    else:
        null_paper_ids = int(df["paper_id"].isnull().sum()) if "paper_id" in df.columns else total_rows
        duplicate_paper_ids = int(df["paper_id"].duplicated().sum()) if "paper_id" in df.columns else 0
        null_titles = int(df["title"].isnull().sum()) if "title" in df.columns else total_rows
        short_summaries = int((df["summary"].astype(str).str.len() < 20).sum()) if "summary" in df.columns else total_rows
        stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum()) if "age_days" in df.columns else 0

        checks = {
            "row_count_check": total_rows >= 5,
            "paper_id_not_null": null_paper_ids == 0,
            "paper_id_unique": duplicate_paper_ids == 0,
            "title_not_null": null_titles == 0,
            "summary_length_check": short_summaries == 0,
            "freshness_check": stale_rows == 0,
        }

        results = {
            "report_name": report_name,
            "passed": all(checks.values()),
            "total_rows": total_rows,
            "null_paper_ids": null_paper_ids,
            "duplicate_paper_ids": duplicate_paper_ids,
            "null_titles": null_titles,
            "short_summaries": short_summaries,
            "stale_rows": stale_rows,
            "checks": checks,
        }

    output_path = settings.paths.quality_dir / f"{report_name}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(output_path, results)
    return results


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """Calculate and write dataset freshness statistics."""
    out_p = Path(report_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if df.empty or "published" not in df.columns:
        report = {
            "latest_published": None,
            "oldest_published": None,
            "stale_rows": 0,
            "total_rows": len(df),
            "is_fresh": False,
        }
        write_json(out_p, report)
        return report

    pub_dates = pd.to_datetime(df["published"], errors="coerce").dropna()
    latest_published = pub_dates.max().isoformat() if not pub_dates.empty else None
    oldest_published = pub_dates.min().isoformat() if not pub_dates.empty else None

    stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum()) if "age_days" in df.columns else 0
    is_fresh = (stale_rows == 0) and len(df) > 0

    report = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "total_rows": len(df),
        "is_fresh": is_fresh,
    }
    write_json(out_p, report)
    return report
