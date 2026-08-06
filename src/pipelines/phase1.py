from __future__ import annotations

import logging

from core.config import load_settings, require_llm_credentials
from core.utils import now_utc, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.agent import build_agent, run_agent_question
from retrieval.index import LocalEmbeddingIndex

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    """Run baseline end-to-end pipeline (Phase 1)."""
    logging.info("Starting Phase 1 Baseline Pipeline...")
    settings = load_settings()

    # 1. Load or fetch raw records
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        logging.info("Fetching raw records from source...")
        records = fetch_source_records(settings)
    else:
        logging.info("Loading existing raw records...")
        records = load_raw_records(settings.paths.raw_records_json)

    # 2. Clean data
    logging.info("Cleaning data...")
    clean_df = build_clean_dataframe(records, now_utc())
    write_csv(clean_df, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, clean_df.to_dict(orient="records"))

    # 3. Build Chroma index
    logging.info("Building baseline Chroma index...")
    index = LocalEmbeddingIndex.build(clean_df, settings, embeddings_output_path=settings.paths.embeddings_json)

    # 4. Create or load evaluation test set
    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        logging.info("Generating new evaluation test set...")
        build_test_set(clean_df, settings.paths.eval_testset)

    # 5. Evaluate pipeline
    logging.info("Evaluating baseline pipeline...")
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )

    # 6. Quality & Freshness checks
    logging.info("Running quality checks and freshness monitoring...")
    quality = run_data_quality_checks(clean_df, settings, "baseline_quality")
    freshness = build_freshness_report(clean_df, settings, settings.paths.freshness_report)

    # 7. Generate markdown report
    logging.info("Generating Phase 1 report...")
    source_summary = {
        "source_api": settings.source_api,
        "total_raw": len(records),
        "total_clean": len(clean_df),
    }
    generate_phase1_report(
        settings.paths.baseline_report,
        source_summary,
        eval_bundle.summary,
        quality,
        freshness,
    )

    # 8. Agent demo sample
    try:
        if len(clean_df) > 0:
            logging.info("Running quick agent demo...")
            agent = build_agent(settings, index)
            demo_q = "What is the main topic of these papers?"
            ans = run_agent_question(agent, demo_q)
            write_json(settings.paths.demo_answers, [{"question": demo_q, "answer": ans}])
    except Exception as exc:
        logging.warning("Agent demo skipped due to provider credentials or model error: %s", exc)

    logging.info("Phase 1 Baseline Pipeline completed successfully!")
