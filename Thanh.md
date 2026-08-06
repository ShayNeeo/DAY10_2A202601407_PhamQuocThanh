# Lab Submission & Activity Report: Data Pipeline & Data Observability Lab

**Author:** Pham Quoc Thanh  
**Student ID:** 2A202601407  
**Team:** Nhóm 10 — Data Pipeline & Data Observability  
**Team Members & Roles:**
- **Phạm Quốc Thành (2A202601407):** Role 1 (Data Ingestion & Synthetic Corruption) & Role 4 (Data Observability, RAGAS Evaluation, CLI & Pipeline Orchestration)
- **Nguyễn Thành An (2A202601017):** Role 2 (Data Cleaning & Preprocessing)
- **Vũ Quang Nhật (2A202602038):** Role 3 (Vector Store & Retrieval Engine)

**Target Repository:** `https://github.com/Muscar1a/K3_Day10_Data-Pipeline-Data-Observability.git`

---

## 1. Overview & Work Summary

This project implements an end-to-end Data Pipeline, RAG Evaluation Framework, Data Observability Suite, and Synthetic Data Corruption & Recovery Flow for Day 10.

As **Role 1 (Data Ingestion & Synthetic Corruption Owner)** and **Role 4 (Evaluation, Observability & Orchestration Owner)**, I have designed, implemented, verified, and integrated all deliverables:

---

## 2. Detailed Technical Deliverables by Module

### A. Core Architecture & Configuration (`src/core`)
- **`config.py`**:
  - Implemented dynamic loading of environment variables (`OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `LANGCHAIN_API_KEY`).
  - Added validation for LangSmith telemetry to prevent 403 authorization errors on invalid keys.
  - Configured standardized path settings for `data/raw/`, `data/clean/`, `data/quality/`, `data/reports/`, and `data/results/`.

### B. Data Ingestion & Synthetic Corruption (`src/ingestion`)
- **`crossref.py`**:
  - Built resilient fetching logic against the Crossref API with backoff retry logic and raw response persistence (`crossref_records.json`).
- **`corruption.py`**:
  - Implemented 8 synthetic data corruption scenarios: `drop_latest_records`, `blank_summary`, `inject_noise`, `truncate_title`, `stale_date`, `add_duplicate`, `entity_swap` (factual shifts), and `metadata_scramble` (author scrambling).

### C. Pipeline Orchestration & CLI (`src/pipelines` & `script/`)
- **`phase1.py`**: Baseline ETL pipeline orchestrating Crossref fetching, cleaning, ChromaDB vector indexing (`papers-baseline`), answer evaluation, and baseline data quality reporting.
- **`corruption_flow.py`**: Comparative workflow driving baseline execution, synthetic corruption injection, quality validation, raw-snapshot ETL recovery, and comparison reporting.
- **`script/cli.py`**: Unified entrypoint supporting `run-all`, `run-phase1`, and `run-corruption`.

### D. Evaluation & Ragas Integration (`src/evaluation`)
- **`testset.py`**: Automated evaluation test set generator producing 96 structured QA pairs with ground truth metadata.
- **`metrics.py`**: Implemented retrieval hit rate calculation, token F1 metrics, LLM-as-a-judge scoring, and `ragas` metrics integration (`faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`).

### E. Data Observability & Visual Reporting (`src/observability`)
- **`quality.py`**: Implemented 6 core data quality rules (`row_count_check`, `paper_id_not_null`, `paper_id_unique`, `title_not_null`, `summary_length_check`, `freshness_check`).
- **`reporting.py`**: Built automated Markdown report generators for `phase1_report.md` and `corruption_report.md`, including comparative delta tables and Matplotlib chart generation (`metrics_comparison.png`).

### F. Automated Test Suite (`tests/`)
- **`tests/`**: Implemented 9 unit tests covering ingestion, cleaning, retrieval indexing, quality rules, freshness calculations, report generation, and metric evaluations (**Passed 9/9**).

---

## 3. Verification & Benchmark Metrics

### Test Suite Execution
```bash
uv run pytest tests/
# Outcome: 9 passed in 9.74s
```

### End-to-End Pipeline Metrics Comparison (`corruption_report.md`)
| Metric / Observability Signal | Baseline | Corrupted | Repaired | Impact Delta | Recovery Delta |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Retrieval Hit Rate** | **100.00%** | **91.67%** | **100.00%** | **-8.33%** | **+8.33%** |
| **Mean Token F1** | **0.3176** | **0.2626** | **0.3176** | **-0.0550** | **+0.0550** |
| **Mean Judge Score** | **2.02** | **1.85** | **2.02** | **-0.17** | **+0.17** |
| **Quality Checks Passed** | **True (Pass)** | **False (Fail)** | **True (Pass)** | **Pass -> Fail** | **Fail -> Pass** |
| **Freshness Stale Rows** | **0 rows** | **2 rows** | **0 rows** | **+2 stale rows** | **-2 stale rows** |

---

## 4. Submission Details

- **Student:** Pham Quoc Thanh
- **Student ID:** 2A202601407
- **Date:** August 06, 2026
- **Status:** All Checkpoints and Team Integration completed and verified.
