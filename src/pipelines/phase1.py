from __future__ import annotations

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


def _step(n: int, label: str) -> None:
    print(f"\n{'='*55}")
    print(f"  STEP {n}/8 — {label}")
    print(f"{'='*55}")


def main() -> None:
    _step(0, "Load settings")
    settings = load_settings()
    print(f"  LLM      : {settings.llm_provider} / {settings.model_name}")
    print(f"  Embedding: {settings.embedding_model}")

    _step(1, "Ingest raw records")
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        print("  → Fetching from Crossref API...")
        records = fetch_source_records(settings)
    else:
        print("  → Loading from snapshot (REFRESH_SOURCE=1 to re-fetch)")
        records = load_raw_records(settings.paths.raw_records_json)
    print(f"  → {len(records)} raw records")

    _step(2, "Clean data")
    clean_df = build_clean_dataframe(records, now_utc())
    write_csv(clean_df, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, clean_df.to_dict(orient="records"))
    print(f"  → {len(clean_df)} clean records saved")

    _step(3, "Build embedding index")
    print(f"  → Collection: papers-baseline")
    index = LocalEmbeddingIndex.build(clean_df, settings, embeddings_output_path=settings.paths.embeddings_json)
    print(f"  → {len(clean_df)} documents embedded")

    _step(4, "Build test set")
    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        items = build_test_set(clean_df, settings.paths.eval_testset)
        print(f"  → {len(items)} test items generated")
    else:
        print("  → Using existing test set (REFRESH_TEST_SET=1 to rebuild)")

    _step(5, "Evaluate pipeline")
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )
    m = eval_bundle.summary
    print(f"  → retrieval_hit_rate : {m.get('retrieval_hit_rate', 0):.2%}")
    print(f"  → mean_token_f1      : {m.get('mean_token_f1', 0):.4f}")
    print(f"  → judge_accuracy     : {m.get('judge_accuracy', 0):.2%}")
    print(f"  → mean_judge_score   : {m.get('mean_judge_score', 0):.2f}/5")

    _step(6, "Data quality & freshness")
    quality = run_data_quality_checks(clean_df, settings, "baseline_quality")
    freshness = build_freshness_report(clean_df, settings, settings.paths.freshness_report)

    _step(7, "Generate report")
    source_summary = {
        "source_api": settings.source_api,
        "total_raw": len(records),
        "total_clean": len(clean_df),
    }
    generate_phase1_report(settings.paths.baseline_report, source_summary, eval_bundle.summary, quality, freshness)
    print(f"  → {settings.paths.baseline_report}")

    _step(8, "Agent demo")
    try:
        agent = build_agent(settings, index)
        demo_q = "What is the main topic of these papers?"
        ans = run_agent_question(agent, demo_q)
        write_json(settings.paths.demo_answers, [{"question": demo_q, "answer": ans}])
        print(f"  Q: {demo_q}")
        print(f"  A: {ans[:120]}...")
    except Exception as exc:
        print(f"  ! Agent demo skipped: {exc}")

    print(f"\n{'='*55}")
    print("  PHASE 1 COMPLETE")
    print(f"{'='*55}\n")
