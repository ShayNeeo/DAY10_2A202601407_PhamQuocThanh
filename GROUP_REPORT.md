# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin         | Nội dung                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------- |
| Khóa/Lớp         | K3 — AI20K                                                                                  |
| Tên nhóm         | Nhóm 10 — Data Pipeline & Data Observability                                                |
| Repository         | [Muscar1a/K3_Day10_Data-Pipeline-Data-Observability](https://github.com/Muscar1a/K3_Day10_Data-Pipeline-Data-Observability.git) |
| Ngày hoàn thành | 2026-08-06                                                                                  |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Phạm Quốc Thành | 2A202601407 | Role 1 & Role 4 Owner (Ingestion, Corruption, Observability, Orchestration & CLI) | `src/ingestion/crossref.py`, `src/ingestion/corruption.py`, `src/observability/quality.py`, `src/observability/reporting.py`, `src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`, `script/cli.py`, `tests/` |
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

## 3. Bảng số liệu đối chiếu thực tế

| Metric / Observability Signal | Baseline | Corrupted | Repaired | Impact Delta (Baseline -> Corrupted) | Recovery Delta (Corrupted -> Repaired) |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Retrieval Hit Rate** | **100.00%** | **91.67%** | **100.00%** | **-8.33%** | **+8.33%** |
| **Mean Token F1** | **0.3176** | **0.2626** | **0.3176** | **-0.0550** | **+0.0550** |
| **Judge Accuracy** | **26.04%** | **21.88%** | **26.04%** | **-4.16%** | **+4.16%** |
| **Mean Judge Score** | **2.02** | **1.85** | **2.02** | **-0.17** | **+0.17** |
| **Quality Checks Passed** | **True (Pass)** | **False (Fail)** | **True (Pass)** | **Pass -> Fail** | **Fail -> Pass** |
| **Freshness Stale Rows** | **0 rows** | **2 rows (>180d)** | **0 rows** | **+2 stale rows** | **-2 stale rows** |

---

## 4. Cách tái hiện kết quả (CLI & Tests)

Chạy toàn bộ pipeline tích hợp (Baseline, Corruption, Self-Healing, Metrics & Charting):
```bash
uv run python script/cli.py run-all
```

Chạy toàn bộ unit test suite:
```bash
uv run pytest tests/
# Output: 9 passed in 9.74s
```
