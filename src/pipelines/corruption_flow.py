from __future__ import annotations

import logging
import pandas as pd

from core.config import load_settings
from core.utils import now_utc, read_json, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report
from retrieval.index import LocalEmbeddingIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    """Run corruption simulation, impact measurement, repair, and comparison flow."""
    logging.info("Starting Corruption & Recovery Flow Pipeline...")
    settings = load_settings()

    # 1. Load baseline clean data and metrics
    if not settings.paths.clean_csv.exists() or not settings.paths.baseline_metrics.exists():
        raise RuntimeError("Baseline artifacts missing. Please run Phase 1 baseline pipeline first!")

    logging.info("Loading baseline clean dataset...")
    clean_df = pd.read_csv(settings.paths.clean_csv)
    baseline_metrics = read_json(settings.paths.baseline_metrics)

    # 2. Corrupt data
    logging.info("Applying synthetic data corruptions...")
    corrupt_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
    write_csv(corrupt_df, settings.paths.corrupted_clean_csv)
    write_json(settings.paths.corrupted_clean_json, corrupt_df.to_dict(orient="records"))

    # 3. Build corrupted Chroma index
    logging.info("Building corrupted Chroma index...")
    corrupted_index = LocalEmbeddingIndex.build(corrupt_df, settings, embeddings_output_path=settings.paths.corrupted_embeddings_json)

    # 4. Evaluate corrupted pipeline
    logging.info("Evaluating corrupted pipeline on baseline test set...")
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers,
    )

    # 5. Quality & Freshness checks on corrupted data
    logging.info("Running quality & freshness checks on corrupted data...")
    corrupted_quality = run_data_quality_checks(corrupt_df, settings, "corrupted_quality")
    corrupted_freshness = build_freshness_report(
        corrupt_df, settings, settings.paths.quality_dir / "corrupted_freshness_report.json"
    )

    # 6. Repair flow from raw records
    logging.info("Repairing data from raw source records...")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    repaired_df = build_clean_dataframe(raw_records, now_utc())
    write_csv(repaired_df, settings.paths.repaired_clean_csv)
    write_json(settings.paths.repaired_clean_json, repaired_df.to_dict(orient="records"))

    # 7. Build repaired Chroma index
    logging.info("Building repaired Chroma index...")
    repaired_index = LocalEmbeddingIndex.build(repaired_df, settings, embeddings_output_path=settings.paths.repaired_embeddings_json)

    # 8. Evaluate repaired pipeline
    logging.info("Evaluating repaired pipeline on baseline test set...")
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers,
    )

    # 9. Quality & Freshness checks on repaired data
    logging.info("Running quality & freshness checks on repaired data...")
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(
        repaired_df, settings, settings.paths.quality_dir / "repaired_freshness_report.json"
    )

    # 10. Generate comparison report
    logging.info("Generating comparison report (Baseline vs. Corrupted vs. Repaired)...")
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_bundle.summary,
        repaired_metrics=repaired_bundle.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )

    logging.info("Corruption & Recovery Flow Pipeline completed successfully!")
