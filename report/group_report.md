# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------- |
| Khóa/Lớp         | K3 — AI20K                                                                                  |
| Tên nhóm         | A1                                                                                          |
| Repository         | [Muscar1a/K3_Day10_Data-Pipeline-Data-Observability](https://github.com/Muscar1a/K3_Day10_Data-Pipeline-Data-Observability.git) |
| Ngày hoàn thành | 2026-08-06                                                                                  |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Phạm Quốc Thanh | 2A202601407 | Role 1 & Role 4 Owner (Ingestion, Corruption, Observability, Orchestration & CLI) | `src/ingestion/crossref.py`, `src/ingestion/corruption.py`, `src/observability/quality.py`, `src/observability/reporting.py`, `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `script/cli.py`, `tests/` |
| 2 | Nguyễn Thành An | 2A202601017 | Role 2 Owner (Data Cleaning & Preprocessing) | `src/ingestion/cleaning.py` |
| 3 | Vũ Quang Nhật | 2A202602038 | Role 3 Owner (Vector Store & Retrieval Engine) | `src/retrieval/embeddings.py`, `src/retrieval/index.py`, `src/retrieval/agent.py` |

---

## 2. Tóm tắt kết quả

Nhóm đã hoàn thành 100% các yêu cầu của bài lab bao gồm 4 khối vai trò chính:
- **Baseline Pipeline (Pha 1):** Thu thập dữ liệu bài báo học thuật từ Crossref REST API (`data/raw/crossref_records.json`), thực hiện làm sạch dữ liệu thành `papers_clean.csv`, tạo embedding và lưu trữ trong ChromaDB collection (`papers-baseline`). Chạy đánh giá chất lượng RAG trên tập test set chuẩn (`data/eval/test_set.json`) đạt **Retrieval Hit Rate = 100.00%**, **Mean Token F1 = 0.3176**, **Mean Judge Score = 2.02**.
- **Data Corruption (Pha 2):** Mô phỏng 8 kịch bản nhiễu/lỗi dữ liệu thực tế (bản ghi rỗng, summary rỗng, nhiễu văn bản, ngày quá hạn, trùng lặp, tráo đổi thực thể `entity_swap`, và đảo tác giả `metadata_scramble`).
- **Tác động của Corruption:** Tỉ lệ tìm kiếm đúng (**Hit Rate**) giảm từ **100% xuống 91.67%**, **Token F1** giảm từ **0.3176 xuống 0.2626**, **LLM Judge Score** giảm từ **2.02 xuống 1.85**. Bộ quan sát dữ liệu (**Data Observability**) bắt được các vi phạm Data Quality (`summary_length_check`, `freshness_check` đều báo lỗi FAIL).
- **Self-Healing Data Recovery:** Kích hoạt luồng phục hồi tự động, tái tạo lại dataset từ bản **Raw JSON Snapshot (Immutable)**. Kết quả sau phục hồi khôi phục hoàn toàn chỉ số về mức Baseline (**Hit Rate = 100.00%**, **Token F1 = 0.3176**, **Judge Score = 2.02**), 100% Quality Checks đạt PASS.

---

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref REST API
    -> Raw JSON Snapshot (data/raw/crossref_records.json) [Immutable]
    -> Data Cleaning & Formatting (data/clean/papers_clean.csv)
    -> ChromaDB Vector Indexing (papers-baseline)
    -> Baseline Evaluation (data/results/baseline_metrics.json)
    -> Quality & Freshness Observability (data/quality/)
    -> Controlled Data Corruption (papers_clean_corrupted.csv)
    -> Corrupted Index & Re-evaluation (corrupted_metrics.json)
    -> Observability Alert & Automated Self-Healing Trigger
    -> Re-ETL from Raw JSON Snapshot (papers_clean_repaired.csv)
    -> Repaired Index & Re-evaluation (repaired_metrics.json)
    -> Comparison Report & Visual Charts (data/reports/corruption_report.md)
```

### Trách nhiệm của từng khối

| Khối | Input | Xử lý chính | Output/artifact | Owner |
| --- | --- | --- | --- | --- |
| Ingestion & Raw | Crossref API | Fetch REST, retry backoff, parse payload | `data/raw/crossref_records.json` | Phạm Quốc Thanh |
| Data Cleaning | Raw records | Clean HTML, build `text_for_embedding`, `age_days` | `data/clean/papers_clean.csv` | Nguyễn Thành An |
| Vector Index & Retrieval | Clean CSV | `MiniLMEmbeddings`, ChromaDB, LangGraph Agent | `data/chroma/`, `embeddings.json` | Vũ Quang Nhật |
| Evaluation Set & Metrics | Clean CSV | Q&A generation, Token F1, LLM Judge, Ragas | `data/eval/test_set.json`, `baseline_metrics.json` | Phạm Quốc Thanh |
| Data Observability | Clean/Corrupt DF | 6 Data Quality rules, Freshness Monitoring | `data/quality/`, `freshness_report.json` | Phạm Quốc Thanh |
| Corruption & Self-Healing | Clean CSV & Raw JSON | Inject synthetic errors, re-run ETL from Raw | `corruption_log.json`, `repaired_clean.csv` | Phạm Quốc Thanh |
| Pipeline Orchestration & CLI | All modules | End-to-end CLI (`cli.py`), chart generation | `script/cli.py`, `corruption_report.md` | Phạm Quốc Thanh |

---

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình | Giá trị sử dụng |
| --- | --- |
| `LLM_PROVIDER` | `openrouter` / `custom` (Cerebras/Gemini) |
| `LLM_MODEL` | `meta-llama/llama-3.3-70b-instruct` / `gemini-2.5-flash` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng Crossref records | 24 records |
| Retrieval `top_k` | 3 |
| Freshness threshold | 180 days |

### Lệnh cài đặt

```bash
uv sync
```

### Lệnh chạy unified CLI

Chạy toàn bộ pipeline tích hợp (Baseline, Corruption, Self-Healing, Metrics & Charting):
```bash
uv run python script/cli.py run-all
```

Chạy từng pha riêng biệt:
```bash
uv run python script/cli.py run-phase1
uv run python script/cli.py run-corruption
```

Chạy kiểm thử tự động (Unit Test Suite):
```bash
uv run pytest tests/
```

### Kết quả tái hiện

| Lệnh | Trạng thái | Thời điểm chạy gần nhất | Bằng chứng |
| --- | --- | --- | --- |
| Baseline pipeline | Thành công (100%) | 2026-08-06 11:45:00 UTC | `data/reports/phase1_report.md`, `baseline_metrics.json` |
| Corruption & Recovery flow | Thành công (100%) | 2026-08-06 11:46:00 UTC | `data/reports/corruption_report.md`, `metrics_comparison.png` |
| Unit Test Suite | Thành công (9/9 passed) | 2026-08-06 11:53:26 UTC | `9 passed in 9.74s` |

---

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu
- **Source:** Crossref REST API (`https://api.crossref.org/works`)
- **Query/Filter:** `query=artificial intelligence`, `filter=from-pub-date:2025-02-07`
- **Số record nhận được:** 24 bản ghi học thuật chuẩn.
- **Cere chế Retry:** Backoff exponential với HTTP request session header tùy biến (`User-Agent: AI20K-Observability-Lab/1.0`).

### Raw và clean schema

| Trường | Kiểu dữ liệu | Bắt buộc? | Ý nghĩa | Xử lý khi thiếu/sai |
| --- | --- | --- | --- | --- |
| `paper_id` | `str` | Có | Định danh bài báo (DOI hoặc generated ID) | Gán hash từ DOI/Title nếu thiếu |
| `title` | `str` | Có | Tiêu đề bài báo | Loại bỏ nếu rỗng |
| `summary` | `str` | Có | Tóm tắt nội dung | Trả về chuỗi rỗng và đánh dấu Quality Check Fail |
| `authors_joined` | `str` | Không | Danh sách tác giả ghép chuỗi | Đổi thành "Unknown" nếu thiếu |
| `published` | `str` | Không | Ngày xuất bản ISO (YYYY-MM-DD) | Mặc định ngày hiện tại |
| `age_days` | `int` | Có | Tuổi của bài báo tính theo ngày | Số ngày chênh lệch với thời điểm hiện tại |
| `text_for_embedding` | `str` | Có | Văn bản ghép tiêu chuẩn hóa để tạo vector | Format: `Title: ... | Summary: ... | Authors: ...` |

---

## 6. Evaluation setup

| Thành phần | Cấu hình thực tế |
| --- | --- |
| Số câu hỏi test set | 96 câu hỏi (4 loại câu hỏi per paper) |
| Các `question_type` | `summary`, `authors`, `date`, `categories` |
| Ground-truth document ID | List chứa exact `paper_id` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store / collections | ChromaDB (`papers-baseline`, `papers-corrupted`, `papers-repaired`) |
| Retrieval `top_k` | 3 |
| LLM provider/model | Llama 3.3 70B / Gemini 2.5 Flash / OpenRouter |
| Test set dùng chung | `data/eval/test_set.json` (giữ cố định cho 3 trạng thái) |

---

## 7. So sánh kết quả Baseline, Corrupted và Repaired

| Metric / Observability Signal | Baseline | Corrupted | Repaired | Impact Delta (Baseline -> Corrupted) | Recovery Delta (Corrupted -> Repaired) |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Retrieval Hit Rate** | **100.00%** | **91.67%** | **100.00%** | **-8.33%** | **+8.33%** |
| **Mean Token F1** | **0.3176** | **0.2626** | **0.3176** | **-0.0550** | **+0.0550** |
| **Judge Accuracy** | **26.04%** | **21.88%** | **26.04%** | **-4.16%** | **+4.16%** |
| **Mean Judge Score** | **2.02** | **1.85** | **2.02** | **-0.17** | **+0.17** |
| **Quality Checks Passed** | **True (Pass)** | **False (Fail)** | **True (Pass)** | **Pass -> Fail** | **Fail -> Pass** |
| **Freshness Stale Rows** | **0 rows** | **2 rows (>180d)** | **0 rows** | **+2 stale rows** | **-2 stale rows** |

---

## 8. Quyết định kỹ thuật & Bài học kinh nghiệm

1. **Phân tách Vector Database:** Không dùng chung hay update ghi đè trên cùng 1 collection ChromaDB. Tạo 3 collection riêng biệt (`papers-baseline`, `papers-corrupted`, `papers-repaired`) để phép so sánh mang tính kiểm chứng độc lập.
2. **Khôi phục từ Immutable Raw Source:** Khi phát hiện lỗi dữ liệu (Data Corruption), hệ thống không cố gắng "un-corrupt" trên file Clean CSV, mà kích hoạt Re-ETL từ file Raw JSON gốc (`crossref_records.json`). Điều này đảm bảo tính toàn vẹn (Data Integrity) tối đa cho Data Pipeline.

---

## 9. Cam kết của nhóm

- [x] Thông tin nhóm và repository hoàn toàn chính xác.
- [x] Phân công khớp với vai trò thực tế của từng thành viên.
- [x] Đã verify chạy lại toàn bộ pipeline và bộ test suite 9/9 passed.
- [x] Báo cáo không chứa bất kỳ API key, token hay secret nào.

**Đại diện nhóm:** Phạm Quốc Thanh — 2A202601407  
**Ngày xác nhận:** 2026-08-06
