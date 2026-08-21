# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------- |
| Họ và tên          | Phạm Quốc Thanh                                                                             |
| MSSV               | 2A202601407                                                                                 |
| Khóa/Lớp           | K3 — AI20K                                                                                  |
| Tên nhóm           | A1                                                                                          |
| Vai trò chính      | Role 1 (Pipeline Integrator) & Role 4 (Evaluation & Observability Owner)                   |
| Repository         | [Muscar1a/K3_Day10_Data-Pipeline-Data-Observability](https://github.com/Muscar1a/K3_Day10_Data-Pipeline-Data-Observability.git) |
| Ngày hoàn thành    | 2026-08-06                                                                                  |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline ETL & Orchestration** | `src/pipelines/phase1.py`<br>`main()` | Crossref API / Raw JSON records | `clean.csv`, `clean.json`, Vector Index, `phase1_report.md` | Hoàn thành |
| **Synthetic Fault Injection & Corruption Flow** | `src/ingestion/corruption.py`<br>`src/pipelines/corruption_flow.py` | Clean DataFrame | `corrupted_clean.csv`, `corruption_log.json`, `repaired_clean.csv` | Hoàn thành |
| **Data Quality & Freshness Observability** | `src/observability/quality.py`<br>`run_data_quality_checks()`, `build_freshness_report()` | Clean / Corrupted / Repaired DataFrames | Quality JSON reports (`baseline_quality.json`, `corrupted_quality.json`, `repaired_quality.json`) | Hoàn thành |
| **Multi-layer Evaluation & Ragas** | `src/evaluation/metrics.py`<br>`src/evaluation/testset.py` | Vector Index, Evaluation Testset | Hit Rate, Token F1, LLM Judge Score, Ragas Metrics JSON (`baseline_metrics.json`, etc.) | Hoàn thành |
| **Visual & Markdown Reporting** | `src/observability/reporting.py`<br>`generate_corruption_report()` | Evaluation & Observability metrics | `corruption_report.md`, `metrics_comparison.png` | Hoàn thành |
| **Unified CLI Tool & Unit Tests** | `script/cli.py`<br>`tests/` | CLI options / Pytest | Unified CLI entrypoint (`cli.py`), 9/9 passed unit tests | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| **Embedding & Vector Index Integration** | Role 2 & 3 (`src/retrieval/index.py`, `cleaning.py`) | Đồng bộ cấu trúc lưu trữ `LocalEmbeddingIndex` với ChromaDB và định dạng metadata phục vụ truy xuất RAG. |
| **LangChain & VertexAI Compatibility Shim** | Hệ thống Ragas / LangChain | Xử lý triệt để lỗi import module `langchain_community.chat_models.vertexai` và vô hiệu hóa LangSmith tracing rác. |
| **Unit Test Suite Authoring** | Toàn bộ nhóm (`tests/`) | Xây dựng bộ unit test kiểm thử tự động cho Quality Rules, Freshness SLA, Evaluation Engine và Report Generator (Passed 9/9). |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Tích hợp Pipeline Baseline Phase 1 | `src/pipelines/phase1.py` | Chạy thành công luồng ETL từ Crossref API -> Vector DB -> Phase1 Report | `uv run python script/cli.py run-phase1` |
| Triển khai 8 kịch bản tiêm lỗi dữ liệu | `src/ingestion/corruption.py` | Tạo file dữ liệu lỗi `corrupted_clean.csv` và nhật ký `corruption_log.json` | Đánh giá qua `corruption_log.json` |
| Xây dựng Data Quality & Freshness Rules | `src/observability/quality.py` | 6 quy tắc kiểm tra tự động và báo cáo SLA độ tươi của dữ liệu | `uv run pytest tests/` |
| Thiết lập Engine đánh giá đa tầng (Ragas + Judge) | `src/evaluation/metrics.py` | Bộ đo Hit Rate, Token F1, LLM Judge Verdict (Pydantic), Ragas metrics | `evaluate_pipeline()` trả về full metrics bundle |
| Xây dựng Luồng Corruption & Self-Repair | `src/pipelines/corruption_flow.py` | Báo cáo đối sánh 3 trạng thái Baseline vs Corrupted vs Repaired | `uv run python script/cli.py run-corruption` |

**Artifact cụ thể được tạo ra:**
- `data/reports/corruption_report.md`: Báo cáo tổng hợp đối sánh chỉ số hiệu năng và tín hiệu Data Observability giữa 3 trạng thái dữ liệu.
- `data/reports/metrics_comparison.png`: Biểu đồ cột trực quan hóa ảnh hưởng của Data Corruption và hiệu quả của khôi phục dữ liệu.

---

## 4. Bảng số liệu đối chiếu thực tế

| Metric / Signal | Baseline | Corrupted | Repaired | Impact Delta | Recovery Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Retrieval Hit Rate** | **100.00%** | **91.67%** | **100.00%** | **-8.33%** | **+8.33%** |
| **Mean Token F1** | **0.3176** | **0.2626** | **0.3176** | **-0.0550** | **+0.0550** |
| **Mean Judge Score** | **2.02 / 5** | **1.85 / 5** | **2.02 / 5** | **-0.17** | **+0.17** |
| **Quality Checks Passed** | **True (Pass)** | **False (Fail)** | **True (Pass)** | **Pass -> Fail** | **Fail -> Pass** |
| **Freshness Stale Rows** | **0 rows** | **2 rows (>180d)** | **0 rows** | **+2 stale rows** | **-2 stale rows** |

---

## 5. Hiểu biết về luồng end-to-end

1. **Dữ liệu đi từ Crossref đến vector index:**  
   API Crossref trả về danh sách bản ghi bài báo thô dạng JSON (`raw_records.json`). Hàm `build_clean_dataframe()` xử lý loại bỏ HTML, lọc bản ghi thiếu title/summary, xóa trùng lặp và tạo trường `text_for_embedding`. Chuỗi này được đưa qua mô hình Embedding (`LocalEmbeddingIndex` / ChromaDB) để chuyển thành vector không gian và lưu trữ kèm metadata.

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality:**  
   Evaluation set chứa các cặp `(question, ground_truth_answer, ground_truth_doc_ids)`.  
   - **Retrieval Quality:** Hệ thống lấy câu hỏi query vào Vector Index thu được `retrieved_doc_ids`. Nếu có ít nhất 1 ID nằm trong `ground_truth_doc_ids`, `retrieval_hit` = True (tính ra `retrieval_hit_rate`).  
   - **Answer Quality:** Câu trả lời sinh ra từ Agent được so sánh với `ground_truth_answer` bằng Token F1, LLM Judge (chấm điểm 1-5) và chỉ số Ragas (`faithfulness`, `answer_relevancy`).

3. **Quality checks khác freshness monitoring ở điểm nào:**  
   - **Quality checks:** Kiểm tra tính toàn vẹn cấu trúc và quy tắc tĩnh của dữ liệu (ví dụ: không được NULL ID, không trùng lặp primary key, độ dài summary tối thiểu > 20 ký tự, số lượng dòng tối thiểu >= 5).  
   - **Freshness monitoring:** Giám sát tính thời sự/độ tươi của dữ liệu theo thời gian thực (tính số ngày `age_days = run_date - published_date`). Nếu số dòng có `age_days > 180` vượt ngưỡng SLA, báo cáo sẽ gắn cờ `is_fresh = False`.

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired:**  
   Để đảm bảo nguyên tắc biến kiểm soát (*controlled experiment*). Bằng cách giữ nguyên tập câu hỏi kiểm thử (Test set), sự thay đổi của các chỉ số (Hit Rate, Token F1, Ragas Score) giữa 3 trạng thái phản ảnh duy nhất tác động của **chất lượng dữ liệu (Data Quality)** chứ không bị nhiễu do độ khó khác nhau của câu hỏi.

5. **Repair được xem là thành công dựa trên artifact và metric nào:**  
   Repair thành công khi và chỉ khi:
   - **Artifact Data Quality:** `repaired_quality.json` ghi nhận `passed = True`, `duplicate_paper_ids = 0`, `short_summaries = 0`.
   - **Artifact Freshness:** `repaired_freshness_report.json` ghi nhận `is_fresh = True` (`stale_rows = 0`).
   - **Metrics:** Trong `corruption_report.md`, các chỉ số `retrieval_hit_rate` phục hồi về **100.00%**, `mean_token_f1` và `mean_judge_score` phục hồi hoàn toàn về mức Baseline.

---

## 6. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng 100% phần việc đã thực hiện.
- [x] Đã đối chiếu số liệu thực tế từ các file trong `data/results/` và `data/reports/`.
- [x] Báo cáo không chứa `.env`, API key hay bất kỳ thông tin nhạy cảm nào.

**Họ và tên:** Phạm Quốc Thanh  
**Ngày xác nhận:** 2026-08-06
