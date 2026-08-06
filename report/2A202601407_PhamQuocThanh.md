# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------- |
| Họ và tên       | Phạm Quốc Thành                                                                             |
| MSSV               | 2A202601407                                                                                 |
| Khóa/Lớp         | K3 — AI20K                                                                                  |
| Tên nhóm         | Nhóm 10 — Data Pipeline & Data Observability                                                |
| Vai trò chính    | Role 1 & Role 4 Owner (Ingestion, Corruption, Observability, Orchestration & CLI)           |
| Repository         | [Muscar1a/K3_Day10_Data-Pipeline-Data-Observability](https://github.com/Muscar1a/K3_Day10_Data-Pipeline-Data-Observability.git) |
| Ngày hoàn thành | 2026-08-06                                                                                  |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Ingestion Raw Fetching | `src/ingestion/crossref.py` | Crossref REST API | `data/raw/crossref_records.json` | Hoàn thành (100%) |
| Synthetic Data Corruption | `src/ingestion/corruption.py` | `papers_clean.csv` | `papers_clean_corrupted.csv`, `corruption_log.json` | Hoàn thành (100%) |
| Observability & Quality | `src/observability/quality.py` | Clean & Corrupted DF | 6 Data Quality Rules, `freshness_report.json` | Hoàn thành (100%) |
| Visual Reporting | `src/observability/reporting.py` | Metrics & Quality JSON | `corruption_report.md`, `metrics_comparison.png` | Hoàn thành (100%) |
| Pipeline Orchestration | `src/pipelines/phase1.py`, `corruption_flow.py` | Raw/Clean/Chroma | Baseline & Self-Healing flows running end-to-end | Hoàn thành (100%) |
| Unified CLI Tool | `script/cli.py` | CLI arguments | Entrypoint commands (`run-all`, `run-phase1`, `run-corruption`) | Hoàn thành (100%) |
| Unit Test Suite | `tests/` | Pytest modules | 9/9 passed unit tests | Hoàn thành (100%) |

---

## 3. Kết quả theo vai trò

- **Xây dựng Ingestion & Resilience:** Viết logic fetch dữ liệu từ Crossref API có cơ chế retry/backoff, lưu trữ raw response không sửa đổi làm căn cứ khôi phục dữ liệu (Immutable Snapshot).
- **Thiết kế Synthetic Data Corruption Suite:** Xây dựng 8 dạng lỗi dữ liệu mô phỏng thực tế bao gồm `drop_latest_records`, `blank_summary`, `inject_noise`, `truncate_title`, `stale_date`, `add_duplicate`, `entity_swap` (thay đổi thuật ngữ để test hallucination), và `metadata_scramble` (xáo trộn tác giả).
- **Tích hợp Ragas & Visual Charts:** Nâng cấp bộ metrics đánh giá RAG bổ sung `ragas` (`faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`) và tự động xuất biểu đồ so sánh `metrics_comparison.png` nhúng trong file báo cáo Markdown.
- **Xây dựng Unified CLI & Pytest Suite:** Thiết lập `script/cli.py` cho phép chạy nhanh toàn bộ pipeline và viết bộ unit test kiểm thử 9/9 test cases đạt 100% pass rate.

---

## 4. Bảng số liệu đối chiếu thực tế

| Metric / Signal | Baseline | Corrupted | Repaired | Impact Delta | Recovery Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Retrieval Hit Rate** | **100.00%** | **91.67%** | **100.00%** | **-8.33%** | **+8.33%** |
| **Mean Token F1** | **0.3176** | **0.2626** | **0.3176** | **-0.0550** | **+0.0550** |
| **Mean Judge Score** | **2.02** | **1.85** | **2.02** | **-0.17** | **+0.17** |
| **Quality Checks Passed** | **True (Pass)** | **False (Fail)** | **True (Pass)** | **Pass -> Fail** | **Fail -> Pass** |
| **Freshness Stale Rows** | **0 rows** | **2 rows (>180d)** | **0 rows** | **+2 stale rows** | **-2 stale rows** |

---

## 5. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến Vector Index:** REST API $\rightarrow$ Raw JSON $\rightarrow$ ETL Clean CSV $\rightarrow$ Text Formatting (`Title | Summary | Authors`) $\rightarrow$ MiniLM Embeddings $\rightarrow$ ChromaDB Persistent Collections.
2. **Cơ chế Evaluation Set:** Giữ cố định 96 câu hỏi test set (`test_set.json`) đánh giá trên 3 collection ChromaDB khác nhau (`papers-baseline`, `papers-corrupted`, `papers-repaired`) để phép so sánh Hit Rate, Token F1 và Judge Score hoàn toàn khách quan.
3. **Phân biệt Quality Checks vs Freshness Monitoring:** Quality checks kiểm tra tính toàn vẹn tĩnh (Null check, Unique ID, Row count, Short summary), còn Freshness monitoring đo tuổi dữ liệu động (`age_days > 180`) để cảnh báo dữ liệu lỗi thời.
4. **Bản chất Self-Healing Data Recovery:** Không cố sửa trực tiếp trên file đã hỏng (`papers_clean_corrupted.csv`), mà thực hiện **Rollback Re-ETL** đọc lại từ file Raw Snapshot nguyên bản (`crossref_records.json`).

---

## 6. Cam kết cá nhân

- [x] Nội dung báo cáo phản ánh đúng 100% phần việc đã thực hiện.
- [x] Đã đối chiếu số liệu thực tế từ các file trong `data/results/` và `data/reports/`.
- [x] Báo cáo không chứa `.env`, API key hay bất kỳ thông tin nhạy cảm nào.

**Họ và tên:** Phạm Quốc Thành  
**Ngày xác nhận:** 2026-08-06
