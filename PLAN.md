# Data Pipeline & Observability Implementation Plan (Agentic Execution)

This plan breaks down the Day 10 lab into isolated, rock-informative phases optimized for execution by smaller autonomous agents. Each phase targets a specific subsystem, minimizing context overhead and ensuring deterministic verification.

---

## 🏛️ Phase 1: Ingestion - Raw Data Fetching
**Target Files:** `src/ingestion/crossref.py`
**Objective:** Fetch raw academic paper metadata from Crossref API and persist it for traceability.

### 📋 Tasks
- [ ] **Implement `fetch_source_records`**:
  - Endpoint: `https://api.crossref.org/works`
  - Implement robust retry/backoff logic to handle `429 Too Many Requests` and `503 Service Unavailable`.
  - Extract relevant fields: title, abstract/summary, authors, categories/topics, publication date, DOI/URL.
- [ ] **Data Modeling**:
  - Parse the JSON response into instances of the `PaperRecord` schema (or equivalent).
- [ ] **Artifact Persistence**:
  - Save raw JSON response directly to `data/raw/raw_response.json`.
  - Save parsed records to `data/raw/raw_records.json`.

### 🔬 Verification Gate
- Run an isolated script or unit test to fetch data.
- **Pass if:** `data/raw/` contains both `raw_response.json` and `raw_records.json` with valid content.

---

## 🧹 Phase 2: Ingestion - Data Cleaning & Preparation
**Target Files:** `src/ingestion/cleaning.py`
**Objective:** Clean raw records, drop invalid entries, and prepare text for embedding.

### 📋 Tasks
- [ ] **Implement `build_clean_dataframe`**:
  - Load `data/raw/raw_records.json`.
  - **Filter**: Remove records with missing critical fields (e.g., no title or abstract).
  - **Normalize**: Clean whitespace and formatting for titles, summaries, and authors.
  - **Transform**: Create a `text_for_embedding` column (e.g., combining title + summary).
  - **Freshness**: Compute a `published` datetime field and an `age_days` integer field from the publication date.
- [ ] **Artifact Persistence**:
  - Save the cleaned dataframe to `data/clean/cleaned_records.csv` or `.json`.

### 🔬 Verification Gate
- **Pass if:** `data/clean/cleaned_records.*` exists, contains no nulls in critical columns, and has `text_for_embedding` and `age_days`.

---

## 🧪 Phase 3: Evaluation - Test Set Generation
**Target Files:** `src/evaluation/testset.py`
**Objective:** Generate a deterministic Q&A evaluation set based on the *clean* data.

### 📋 Tasks
- [ ] **Implement Test Set Generator**:
  - Read `data/clean/cleaned_records.csv`.
  - Generate a set of factual questions based on the paper abstracts.
  - For each question, store: `question`, `ground_truth` (answer), `ground_truth_doc_ids` (for retrieval hit rate), and `question_type`.
- [ ] **Artifact Persistence**:
  - Save to `data/eval/testset.json`.

### 🔬 Verification Gate
- **Pass if:** `data/eval/testset.json` is generated and contains the required schema for evaluation.

---

## 📊 Phase 4: Observability - Data Quality & Freshness
**Target Files:** `src/observability/quality.py`, `src/observability/reporting.py`, `src/observability/__init__.py`
**Objective:** Build mechanisms to assert data quality and generate human-readable Markdown reports.

### 📋 Tasks
- [ ] **Implement Quality Checks**:
  - Assert no missing values in `title`, `summary`, or `text_for_embedding`.
  - Assert uniqueness (no duplicate IDs/titles).
- [ ] **Implement Freshness Checks**:
  - Assert `age_days` does not exceed a reasonable threshold for the domain.
- [ ] **Implement Report Generation**:
  - `generate_phase1_report()`: Aggregate metrics, quality checks, and freshness into a Markdown report.
- [ ] **Artifact Persistence**:
  - Write checks to `data/quality/` and markdown to `data/reports/phase1_report.md`.

### 🔬 Verification Gate
- **Pass if:** Quality functions return deterministic Pass/Fail signals.

---

## 🚀 Phase 5: Baseline Pipeline Orchestration
**Target Files:** `src/pipelines/phase1.py`
**Objective:** Tie Phases 1-4 together into an end-to-end execution flow.

### 📋 Tasks
- [ ] **Implement `main()` in `phase1.py`**:
  1. Fetch/load raw records.
  2. Clean data.
  3. Initialize `LocalEmbeddingIndex` and build ChromaDB index from clean data.
  4. Generate/load the test set.
  5. Run `evaluate_pipeline()` to get baseline metrics.
  6. Run data quality and freshness checks.
  7. Generate and save `phase1_report.md`.
  8. Save metrics to `data/results/baseline_metrics.json`.

### 🔬 Verification Gate
- **Execution:** `uv run python script/run_phase1.py`
- **Pass if:** `data/results/baseline_metrics.json` exists with valid metrics (`retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`).

---

## 💥 Phase 6: Data Corruption Simulation
**Target Files:** `src/ingestion/corruption.py`
**Objective:** Inject synthetic anomalies into the clean data to simulate real-world ETL failures.

### 📋 Tasks
- [ ] **Implement `corrupt_clean_dataframe`**:
  - Take the clean dataframe as input.
  - **Deletions**: Randomly drop 10-20% of rows (simulating missing records).
  - **Nulls/Noise**: Blank out summaries or add random noise strings.
  - **Truncation**: Truncate titles to 10 characters.
  - **Staleness**: Artificially increase `age_days` or shift publication dates to the past.
  - **Duplicates**: Duplicate several rows.

### 🔬 Verification Gate
- **Pass if:** The corrupted dataframe fails the data quality checks implemented in Phase 4.

---

## 🔄 Phase 7: Corruption, Repair, and Comparison Flow
**Target Files:** `src/pipelines/corruption_flow.py`
**Objective:** Measure the impact of bad data on the Agent, repair the data from raw source, and compare all three states.

### 📋 Tasks
- [ ] **Implement `main()` in `corruption_flow.py`**:
  1. Load cleaned baseline data.
  2. Apply `corrupt_clean_dataframe()`.
  3. Rebuild `LocalEmbeddingIndex` with corrupted data.
  4. **Evaluate (Corrupted)**: Run evaluation using the *exact same* test set from Phase 3. Log metrics.
  5. Run quality checks (expecting failures).
  6. **Repair**: Reload from `data/raw/raw_records.json` and re-run cleaning logic to restore the dataset.
  7. Rebuild `LocalEmbeddingIndex` with repaired data.
  8. **Evaluate (Repaired)**: Run evaluation again. Log metrics.
  9. **Reporting**: Generate a markdown report comparing Baseline vs. Corrupted vs. Repaired metrics.
- [ ] **Artifact Persistence**:
  - Write metrics and log to `data/results/corruption_log.json`.
  - Write `data/reports/corruption_report.md`.

### 🔬 Verification Gate
- **Execution:** `uv run python script/run_corruption_flow.py`
- **Pass if:** `corruption_report.md` shows a clear degradation in RAG metrics (Token F1, Hit Rate) during the corrupted phase, and recovery during the repaired phase.
