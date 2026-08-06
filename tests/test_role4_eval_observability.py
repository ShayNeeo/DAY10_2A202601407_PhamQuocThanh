from pathlib import Path
import tempfile
import pandas as pd
import pytest

from core.config import load_settings
from evaluation.metrics import _token_f1
from evaluation.testset import build_test_set
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report, generate_phase1_report


def test_token_f1():
    assert _token_f1("hello world", "hello world") == 1.0
    assert _token_f1("hello world", "hello python") == 0.5
    assert _token_f1("hello world", "foo bar") == 0.0
    assert _token_f1("", "hello") == 0.0


def test_build_test_set():
    df = pd.DataFrame(
        [
            {
                "paper_id": "p001",
                "title": "Agentic AI RAG",
                "summary": "Comprehensive overview of agentic RAG architectures.",
                "authors": "Alice, Bob",
                "published": "2026-01-01",
                "categories": "Computer Science",
            }
        ]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_set.json"
        items = build_test_set(df, out_path)
        assert len(items) == 4
        assert out_path.exists()
        assert items[0]["ground_truth_doc_ids"] == ["p001"]


def test_data_quality_checks():
    settings = load_settings()
    clean_df = pd.DataFrame(
        [
            {
                "paper_id": f"p{i:03d}",
                "title": f"Title {i}",
                "summary": "This is a sufficiently long summary for paper evaluation.",
                "age_days": 10,
            }
            for i in range(10)
        ]
    )
    res_clean = run_data_quality_checks(clean_df, settings, "clean_test")
    assert res_clean["passed"] is True

    corrupted_df = pd.DataFrame(
        [
            {
                "paper_id": "p001",
                "title": None,
                "summary": "Short",
                "age_days": 999,
            }
        ]
    )
    res_corrupt = run_data_quality_checks(corrupted_df, settings, "corrupt_test")
    assert res_corrupt["passed"] is False


def test_freshness_report():
    settings = load_settings()
    df = pd.DataFrame(
        [
            {"published": "2026-01-01", "age_days": 10},
            {"published": "2025-01-01", "age_days": 300},
        ]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "freshness.json"
        report = build_freshness_report(df, settings, out_path)
        assert report["total_rows"] == 2
        assert report["stale_rows"] == 1
        assert report["is_fresh"] is False


def test_report_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        phase1_out = Path(tmpdir) / "phase1.md"
        generate_phase1_report(
            phase1_out,
            source_summary={"source_api": "Crossref", "total_raw": 10, "total_clean": 10},
            metrics={"samples": 5, "retrieval_hit_rate": 0.8, "mean_token_f1": 0.6, "judge_accuracy": 0.8, "mean_judge_score": 4.0},
            quality={"passed": True, "total_rows": 10, "null_paper_ids": 0, "duplicate_paper_ids": 0, "null_titles": 0, "short_summaries": 0},
            freshness={"is_fresh": True, "stale_rows": 0, "latest_published": "2026-01-01", "oldest_published": "2025-06-01"},
        )
        assert phase1_out.exists()
        assert "# Baseline Data Pipeline" in phase1_out.read_text()

        corruption_out = Path(tmpdir) / "corruption.md"
        generate_corruption_report(
            corruption_out,
            baseline_metrics={"retrieval_hit_rate": 0.8, "mean_token_f1": 0.6, "mean_judge_score": 4.0},
            corrupted_metrics={"retrieval_hit_rate": 0.4, "mean_token_f1": 0.2, "mean_judge_score": 2.0},
            repaired_metrics={"retrieval_hit_rate": 0.8, "mean_token_f1": 0.6, "mean_judge_score": 4.0},
            corrupted_quality={"passed": False, "total_rows": 8, "null_titles": 2, "short_summaries": 3},
            repaired_quality={"passed": True, "total_rows": 10, "null_titles": 0, "short_summaries": 0},
            corrupted_freshness={"stale_rows": 4},
            repaired_freshness={"stale_rows": 0},
        )
        assert corruption_out.exists()
        assert "# Data Quality Impact & Recovery Report" in corruption_out.read_text()
