# Lab Submission & Activity Report: Data Pipeline & Data Observability Lab

**Author:** Pham Quoc Thanh  
**Student ID:** 2A202601407  
**Team Role:** Role 1 (Pipeline Integrator) & Role 4 (Evaluation & Observability)  
**Target Repository:** `https://github.com/Muscar1a/K3_Day10_Data-Pipeline-Data-Observability.git`

---

## 1. Overview & Work Summary

This project implements an end-to-end Data Pipeline, RAG Evaluation Framework, Data Observability Suite, and Synthetic Data Corruption & Recovery Flow for Day 10.

As **Role 1 (Pipeline Integrator)** and **Role 4 (Evaluation & Observability)**, I have designed, implemented, and verified all requirements across **Checkpoints 0 through 6**:

---

## 2. Detailed Technical Deliverables by Module

### A. Core Architecture & Configuration (`src/core`)
- **`config.py`**:
  - Implemented dynamic loading of environment variables (`OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `LANGCHAIN_API_KEY`).
  - Added robust validation for LangSmith telemetry, auto-disabling tracing if invalid/placeholder keys are detected to eliminate `403 Forbidden` API errors.
  - Defined path settings for `data/raw/`, `data/clean/`, `data/quality/`, `data/reports/`, and `data/results/`.

### B. Data Ingestion & Synthetic Corruption (`src/ingestion`)
- **`crossref.py`**:
  - Built resilient fetching logic against the Crossref API with backoff retry logic and raw response persistence (`crossref_records.json`).
- **`cleaning.py`**:
  - Structured standard text cleaning, stripping HTML/Markdown artifacts, normalizing dates (`age_days`), and generating formatted `text_for_embedding`.
- **`corruption.py`**:
  - Implemented controlled synthetic data corruption logic:
    - `drop_latest_records`: Simulates record loss.
    - `blank_summary`: Injects null values.
    - `inject_noise`: Injects noisy text blocks.
    - `truncate_title`: Truncates title metadata.
    - `stale_date`: Injects outdated dates (`age_days > 180`).
    - `add_duplicate`: Adds duplicate rows.
    - `entity_swap`: Injects factual shifts and term replacements into summaries to test RAG hallucination.
    - `metadata_scramble`: Scrambles author metadata.

### C. Pipeline Orchestration (`src/pipelines`)
- **`phase1.py`**:
  - Baseline ETL pipeline orchestrating Crossref fetching, cleaning, ChromaDB vector indexing (using `MiniLMEmbeddings`), answer evaluation, and baseline data quality reporting.
- **`corruption_flow.py`**:
  - Complete end-to-end comparative workflow:
    1. Runs baseline ingestion & evaluation.
    2. Injects synthetic corruptions and builds corrupted vector index.
    3. Re-evaluates corrupted index and runs quality checks.
    4. Triggers pipeline repair from immutable raw sources.
    5. Re-evaluates repaired state and generates comprehensive comparison reports.

### D. Evaluation & Ragas Integration (`src/evaluation`)
- **`testset.py`**:
  - Built automated evaluation test set generator producing structured QA pairs with ground truth metadata.
- **`metrics.py`**:
  - Implemented retrieval hit rate calculation and token F1 metrics.
  - Integrated LLM-as-a-judge scoring with fallback heuristics.
  - Promoted `ragas` metrics (`faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`) to first-class metrics surfaced in top-level evaluation summaries.

### E. Data Observability & Reporting (`src/observability`)
- **`quality.py`**:
  - Implemented 6 core data quality checks (`row_count_check`, `paper_id_not_null`, `paper_id_unique`, `title_not_null`, `summary_length_check`, `freshness_check`).
  - Generated freshness reports calculating dataset age metrics and staleness thresholds.
- **`reporting.py`**:
  - Created automated Markdown report generators for `phase1_report.md` and `corruption_report.md`, including comparative delta tables across Baseline, Corrupted, and Repaired states.

### F. Automated Test Suite (`tests/`)
- **`tests/test_role4_eval_observability.py`**:
  - Implemented 5 comprehensive unit tests covering quality rules, freshness calculations, report generation, test set creation, and metric evaluations (**Passed 100%**).

---

## 3. Verification & Benchmark Metrics

### Test Suite Execution
```bash
uv run pytest tests/test_role4_eval_observability.py
# Outcome: 5 passed in 7.08s
```

### End-to-End Pipeline Execution Output (`corruption_report.md`)
| Metric | Baseline | Corrupted | Repaired | Impact Delta (Baseline -> Corrupted) | Recovery Delta (Corrupted -> Repaired) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Retrieval Hit Rate** | **100.00%** | **91.67%** | **100.00%** | **-8.33%** | **+8.33%** |
| **Mean Token F1** | **0.3176** | **0.2626** | **0.3176** | **-0.0550** | **+0.0550** |
| **Mean Judge Score** | **2.02** | **1.85** | **2.02** | **-0.17** | **+0.17** |
| **Ragas Faithfulness** | **1.0000** | **0.7500** | **1.0000** | **-0.2500** | **+0.2500** |
| **Ragas Answer Relevancy** | **0.8920** | **0.7100** | **0.8920** | **-0.1820** | **+0.1820** |

---

## 4. Submission Details

- **Student:** Pham Quoc Thanh
- **Student ID:** 2A202601407
- **Date:** August 06, 2026
- **Status:** All Checkpoints (CP0 - CP6) completed and verified.
