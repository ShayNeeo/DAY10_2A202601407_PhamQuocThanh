from __future__ import annotations

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


def _step(n: int, total: int, label: str) -> None:
    print(f"\n{'='*55}")
    print(f"  STEP {n}/{total} — {label}")
    print(f"{'='*55}")


def _print_metrics(label: str, m: dict) -> None:
    print(f"  [{label}]")
    print(f"    retrieval_hit_rate : {m.get('retrieval_hit_rate', 0):.2%}")
    print(f"    mean_token_f1      : {m.get('mean_token_f1', 0):.4f}")
    print(f"    judge_accuracy     : {m.get('judge_accuracy', 0):.2%}")
    print(f"    mean_judge_score   : {m.get('mean_judge_score', 0):.2f}/5")


def main() -> None:
    _step(0, 10, "Load settings & verify baseline")
    settings = load_settings()
    if not settings.paths.clean_csv.exists() or not settings.paths.baseline_metrics.exists():
        raise RuntimeError("Baseline artifacts missing — run phase1 first.")
    clean_df = pd.read_csv(settings.paths.clean_csv)
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    print(f"  → Baseline: {len(clean_df)} clean records loaded")
    _print_metrics("baseline", baseline_metrics)

    _step(1, 10, "Corrupt data")
    corrupt_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
    write_csv(corrupt_df, settings.paths.corrupted_clean_csv)
    write_json(settings.paths.corrupted_clean_json, corrupt_df.to_dict(orient="records"))
    print(f"  → {len(clean_df)} → {len(corrupt_df)} rows after corruption")
    print(f"  → Log: {settings.paths.corruption_log}")

    _step(2, 10, "Build corrupted embedding index")
    print("  → Collection: papers-corrupted")
    corrupted_index = LocalEmbeddingIndex.build(
        corrupt_df, settings, embeddings_output_path=settings.paths.corrupted_embeddings_json
    )
    print(f"  → {len(corrupt_df)} documents embedded")

    _step(3, 10, "Evaluate corrupted pipeline")
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers,
    )
    _print_metrics("corrupted", corrupted_bundle.summary)

    _step(4, 10, "Quality & freshness — corrupted")
    corrupted_quality = run_data_quality_checks(corrupt_df, settings, "corrupted_quality")
    corrupted_freshness = build_freshness_report(
        corrupt_df, settings, settings.paths.quality_dir / "corrupted_freshness_report.json"
    )
    print(f"  → passed={corrupted_quality.get('passed')}  stale={corrupted_quality.get('stale_rows')}  dupes={corrupted_quality.get('duplicate_paper_ids')}")

    _step(5, 10, "Repair from raw records")
    raw_records = load_raw_records(settings.paths.raw_records_json)
    repaired_df = build_clean_dataframe(raw_records, now_utc())
    write_csv(repaired_df, settings.paths.repaired_clean_csv)
    write_json(settings.paths.repaired_clean_json, repaired_df.to_dict(orient="records"))
    print(f"  → {len(repaired_df)} records repaired from raw source")

    _step(6, 10, "Build repaired embedding index")
    print("  → Collection: papers-repaired")
    repaired_index = LocalEmbeddingIndex.build(
        repaired_df, settings, embeddings_output_path=settings.paths.repaired_embeddings_json
    )
    print(f"  → {len(repaired_df)} documents embedded")

    _step(7, 10, "Evaluate repaired pipeline")
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers,
    )
    _print_metrics("repaired", repaired_bundle.summary)

    _step(8, 10, "Quality & freshness — repaired")
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(
        repaired_df, settings, settings.paths.quality_dir / "repaired_freshness_report.json"
    )
    print(f"  → passed={repaired_quality.get('passed')}  stale={repaired_quality.get('stale_rows')}  dupes={repaired_quality.get('duplicate_paper_ids')}")

    _step(9, 10, "Generate comparison report")
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
    print(f"  → {settings.paths.comparison_report}")

    _step(10, 10, "Summary")
    print(f"\n  {'Metric':<25} {'Baseline':>10} {'Corrupted':>10} {'Repaired':>10}")
    print(f"  {'-'*57}")
    for k in ("retrieval_hit_rate", "mean_token_f1", "judge_accuracy", "mean_judge_score"):
        b = baseline_metrics.get(k, 0)
        c = corrupted_bundle.summary.get(k, 0)
        r = repaired_bundle.summary.get(k, 0)
        print(f"  {k:<25} {b:>10.4f} {c:>10.4f} {r:>10.4f}")

    print(f"\n{'='*55}")
    print("  CORRUPTION FLOW COMPLETE")
    print(f"{'='*55}\n")
