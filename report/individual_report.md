# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                                                                   |
| ------------------ | -------------------------------------------------------------------------- |
| Họ và tên          | Phạm Quốc Thành                                                           |
| MSSV               | 2A202601407                                                                |
| Khóa/Lớp           | K3 / AI-Lab Day 10                                                         |
| Tên nhóm           | Muscar1a                                                                   |
| Vai trò chính      | Role 1 (Pipeline Integrator) & Role 4 (Evaluation & Observability)         |
| Repository         | https://github.com/Muscar1a/K3_Day10_Data-Pipeline-Data-Observability.git |
| Ngày hoàn thành    | 2026-08-06                                                                 |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline ETL & Orchestration** | [`src/pipelines/phase1.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/pipelines/phase1.py)<br>`main()` | Crossref API / Raw JSON records | `clean.csv`, `clean.json`, Vector Index, `phase1_report.md` | Hoàn thành |
| **Synthetic Fault Injection & Corruption Flow** | [`src/ingestion/corruption.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/ingestion/corruption.py)<br>[`src/pipelines/corruption_flow.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/pipelines/corruption_flow.py) | Clean DataFrame | `corrupted_clean.csv`, `corruption_log.json`, `repaired_clean.csv` | Hoàn thành |
| **Data Quality & Freshness Observability** | [`src/observability/quality.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/observability/quality.py)<br>`run_data_quality_checks()`, `build_freshness_report()` | Clean / Corrupted / Repaired DataFrames | Quality JSON reports (`baseline_quality.json`, `corrupted_quality.json`, `repaired_quality.json`) | Hoàn thành |
| **Multi-layer Evaluation & Ragas** | [`src/evaluation/metrics.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/evaluation/metrics.py)<br>[`src/evaluation/testset.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/evaluation/testset.py) | Vector Index, Evaluation Testset | Hit Rate, Token F1, LLM Judge Score, Ragas Metrics JSON (`baseline_metrics.json`, etc.) | Hoàn thành |
| **Visual & Markdown Reporting** | [`src/observability/reporting.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/observability/reporting.py)<br>`generate_corruption_report()` | Evaluation & Observability metrics | [`corruption_report.md`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/reports/corruption_report.md), [`metrics_comparison.png`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/reports/metrics_comparison.png) | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| :--- | :--- | :--- |
| **Embedding & Vector Index Integration** | Role 2 & 3 ([`src/retrieval/index.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/retrieval/index.py)) | Đồng bộ cấu trúc lưu trữ `LocalEmbeddingIndex` với ChromaDB và định dạng metadata phục vụ truy xuất RAG. |
| **LangChain & VertexAI Compatibility Shim** | Hệ thống Ragas / LangChain | Xử lý triệt để lỗi import module `langchain_community.chat_models.vertexai` và vô hiệu hóa LangSmith tracing rác. |
| **Unit Test Suite Authoring** | Toàn bộ nhóm ([`tests/test_role4_eval_observability.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/tests/test_role4_eval_observability.py)) | Xây dựng 5 unit test kiểm thử tự động cho Quality Rules, Freshness SLA, Evaluation Engine và Report Generator (Passed 100%). |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| :--- | :--- | :--- | :--- |
| Tích hợp Pipeline Baseline Phase 1 | [`src/pipelines/phase1.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/pipelines/phase1.py) | Chạy thành công luồng ETL từ Crossref API -> Vector DB -> Phase1 Report | `uv run python -m pipelines.phase1` |
| Triển khai 8 kịch bản tiêm lỗi dữ liệu | [`src/ingestion/corruption.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/ingestion/corruption.py) | Tạo file dữ liệu lỗi `corrupted_clean.csv` và nhật ký `corruption_log.json` | Đánh giá qua `corruption_log.json` |
| Xây dựng Data Quality & Freshness Rules | [`src/observability/quality.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/observability/quality.py) | 6 quy tắc kiểm tra tự động và báo cáo SLA độ tươi của dữ liệu | `uv run pytest tests/test_role4_eval_observability.py` |
| Thiết lập Engine đánh giá đa tầng (Ragas + Judge) | [`src/evaluation/metrics.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/evaluation/metrics.py) | Bộ đo Hit Rate, Token F1, LLM Judge Verdict (Pydantic), Ragas metrics | `evaluate_pipeline()` trả về full metrics bundle |
| Xây dựng Luồng Corruption & Self-Repair | [`src/pipelines/corruption_flow.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/pipelines/corruption_flow.py) | Báo cáo đối sánh 3 trạng thái Baseline vs Corrupted vs Repaired | `uv run python -m pipelines.corruption_flow` |

**Artifact cụ thể được tạo ra:**
- [`data/reports/corruption_report.md`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/reports/corruption_report.md): Báo cáo tổng hợp đối sánh chỉ số hiệu năng và tín hiệu Data Observability giữa 3 trạng thái dữ liệu.
- [`data/reports/metrics_comparison.png`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/reports/metrics_comparison.png): Biểu đồ cột trực quan hóa ảnh hưởng của Data Corruption và hiệu quả của khôi phục dữ liệu.

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Trong các hệ thống RAG (Retrieval-Augmented Generation), dữ liệu bẩn (Data Drift, Null metadata, Stale records, Entity Swap) có thể thầm lặng làm giảm độ chính xác của Vector Retrieval và gây ra hiện tượng ảo giác (Hallucination) ở LLM mà các phương pháp kiểm thử phần mềm truyền thống không phát hiện được.

### Cách triển khai
1. **Mô hình ETL Robust:** Trích xuất từ Crossref API (`E`), làm sạch dữ liệu trong bộ nhớ Pandas (`T`) trước khi nạp vào Chroma Vector DB (`L`).
2. **Synthetic Data Corruption:** Viết hàm [`corrupt_clean_dataframe()`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/ingestion/corruption.py#L8) chủ động tiêm 8 loại lỗi: làm rỗng summary, bơm chuỗi nhiễu, cắt ngắn title, tạo trùng lặp key, tạo dữ liệu quá hạn > 180 ngày (`stale_date`), tráo đổi thực thể (`entity_swap`) và xáo trộn metadata tác giả.
3. **Data Quality & Freshness Guardrails:** Thiết lập 6 quy tắc kiểm định (`row_count_check`, `paper_id_not_null`, `paper_id_unique`, `title_not_null`, `summary_length_check`, `freshness_check`) để phát hiện dữ liệu lỗi trước khi nạp vào Vector Store.
4. **Multi-layer RAG Evaluator:** Đánh giá RAG qua 3 lớp: Lexical (Token F1), LLM-as-a-Judge (sử dụng Pydantic Structured Output `JudgeVerdict` với fallback heuristic), và Ragas Framework (*Faithfulness*, *Answer Relevancy*, *Context Precision*, *Context Recall*).

### Input, output và contract

| Thành phần | Mô tả |
| :--- | :--- |
| **Input** | Raw JSON records từ Crossref API (`raw_records.json`), `Settings` object (`core/config.py`). |
| **Output** | `clean.csv`, `corrupted_clean.csv`, `repaired_clean.csv`, Chroma Vector Store (`data/chroma`), Quality JSON Reports, `corruption_report.md`, `metrics_comparison.png`. |
| **Module phụ thuộc** | [`src/core/config.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/core/config.py), [`src/ingestion/crossref.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/ingestion/crossref.py), [`src/retrieval/index.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/retrieval/index.py). |
| **Module sử dụng output** | [`src/retrieval/agent.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/retrieval/agent.py), [`src/observability/reporting.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/observability/reporting.py). |
| **Điều kiện lỗi cần xử lý** | Mất kết nối API Crossref (tự động load từ snapshot raw JSON); Mất kết nối/hết quota LLM Evaluator (tự động fallback sang Heuristic Judge dựa trên Token F1). |

### Cách xác minh

```bash
# 1. Chạy Unit Test kiểm thử logic Observability & Evaluation
uv run pytest tests/test_role4_eval_observability.py

# 2. Chạy toàn bộ luồng Corruption & Self-Repair Pipeline
uv run python -m pipelines.corruption_flow
```

- **Kết quả mong đợi:** 5/5 unit test PASS; pipeline chạy qua 10/10 bước, phát hiện lỗi ở bước Corrupted (Passed = False), khôi phục thành công ở bước Repaired (Passed = True).
- **Kết quả thực tế:** Test suite đạt `5 passed in 7.08s`. File `corruption_report.md` và `metrics_comparison.png` được tạo tự động với đầy đủ số liệu đối sánh.
- **Artifact/log:** [`data/reports/corruption_report.md`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/reports/corruption_report.md), [`data/quality/corrupted_quality.json`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/quality/corrupted_quality.json).

---

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp đánh giá (Evaluation) cho RAG Agent và cơ chế xử lý khi LLM Evaluator bị ngắt kết nối hoặc hết quota API Key.
- **Các phương án đã cân nhắc:**
  1. *Phương án A:* Chỉ dùng metrics truyền thống (Exact Match, BLEU, Token F1).
  2. *Phương án B:* Chỉ phụ thuộc hoàn toàn vào LLM-as-a-Judge hoặc Ragas API trực tuyến.
  3. *Phương án C (Đã chọn):* Kết hợp đa tầng: Lexical F1 + Structured LLM Judge (Pydantic) + Ragas Framework, đồng thời thiết lập **Fallback Heuristic Judge**.
- **Lý do chọn Phương án C:** RAG Agent cần đánh giá cả khía cạnh truy xuất (Retrieval) lẫn ngữ nghĩa câu trả lời (Generation). Phương án C mang lại cái nhìn toàn diện nhất. Quan trọng hơn, cơ chế Fallback Heuristic dựa trên ngưỡng Token F1 đảm bảo pipeline CI/CD luôn chạy hoàn tất mà không bị treo/crash khi gặp sự cố mạng hoặc thiếu API key.
- **Bằng chứng quyết định phù hợp:** Kết quả chạy kiểm thử thể hiện rõ: khi LLM Judge hoạt động, hệ thống trả về điểm số chi tiết kèm `reasoning`. Khi ngắt kết nối, hệ thống chuyển sang Fallback Judge mượt mà, ghi nhận lại log mà không ngắt quãng pipeline execution.

---

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**
  ```text
  ModuleNotFoundError: No module named 'langchain_community.chat_models.vertexai'
  HTTPError: 403 Client Error: Forbidden for url: https://api.smith.langchain.com/runs
  ```
- **Lệnh hoặc bước tái hiện:** `uv run python -m pipelines.corruption_flow` khi thư viện Ragas tự động kích hoạt LangSmith tracing mà không có API key hợp lệ.
- **Nguyên nhân gốc:** 
  1. Thư viện `ragas` mặc định cố gắng import `ChatVertexAI` từ `langchain_community.chat_models.vertexai` ngay cả khi chỉ sử dụng OpenAI/Gemini provider.
  2. LangChain SDK tự động đọc biến môi trường rác hoặc placeholder `your_langsmith_api_key`, gửi request tới LangSmith cloud dẫn đến lỗi `403 Forbidden`.
- **Cách xử lý:**
  1. Trong [`src/core/config.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/core/config.py): Bổ sung hàm kiểm tra API Key LangSmith; nếu phát hiện key rỗng hoặc chứa từ khóa placeholder, tự động gán `os.environ["LANGCHAIN_TRACING_V2"] = "false"`.
  2. Trong [`src/evaluation/metrics.py`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/src/evaluation/metrics.py): Tạo một Dynamic Module Shim cho `langchain_community.chat_models.vertexai` trước khi gọi `import ragas`.
- **Cách xác minh sau khi sửa:** Chạy lại `uv run python -m pipelines.corruption_flow`, toàn bộ luồng đánh giá Ragas và LLM Judge chạy mượt mà 100% không bắn ra exception.
- **Điều học được:** Khi tích hợp các khung thư viện AI phức tạp (như Ragas/LangChain), không nên phụ thuộc vào cấu hình mặc định của thư viện mà cần có lớp bọc (wrapper/shim) và validation cấu hình chặt chẽ tại tầng Core Config.

---

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

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
   - **Artifact Data Quality:** [`repaired_quality.json`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/quality/repaired_quality.json) ghi nhận `passed = True`, `duplicate_paper_ids = 0`, `short_summaries = 0`.
   - **Artifact Freshness:** [`repaired_freshness_report.json`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/quality/repaired_freshness_report.json) ghi nhận `is_fresh = True` (`stale_rows = 0`).
   - **Metrics:** Trong [`corruption_report.md`](file:///e:/AI/Lab/K3_Day10_Data-Pipeline-Data-Observability/data/reports/corruption_report.md), các chỉ số `retrieval_hit_rate` phục hồi về **100.00%**, `mean_token_f1` và `mean_judge_score` phục hồi hoàn toàn về mức Baseline.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| :--- | ---: | ---: | ---: | :--- |
| `retrieval_hit_rate` | **100.00%** | **91.67%** | **100.00%** | Corruption làm sụt giảm **8.33%** khả năng truy xuất đúng tài liệu do bị xóa dòng và nhiễu tiêu đề. |
| `mean_token_f1` | **0.3176** | **0.2626** | **0.3176** | Token F1 giảm **0.0550** ở trạng thái Corrupted do thông tin tóm tắt bị nhiễu và tráo thực thể. |
| `judge_accuracy` | **38.89%** | **30.56%** | **38.89%** | Đánh giá từ LLM Judge cho thấy tỷ lệ câu trả lời đạt yêu cầu giảm khi dữ liệu bị sai lệch. |
| `mean_judge_score` | **2.02 / 5** | **1.85 / 5** | **2.02 / 5** | Điểm trung bình từ LLM Judge giảm **0.17** điểm khi gặp dữ liệu rác/nhiễu. |
| Quality checks | **Passed (True)** | **FAILED (False)** | **Passed (True)** | Phát hiện chính xác 2 dòng short summary và các lỗi bất thường ở trạng thái Corrupted. |
| Freshness status | **Fresh (0 stale)** | **Stale (2 stale)** | **Fresh (0 stale)** | Cảnh báo chính xác 2 bản ghi bị cố tình đẩy lùi ngày xuất bản về năm 2020 (`age_days > 180`). |

### Kết luận từ số liệu

**Hai chuỗi nguyên nhân – bằng chứng:**

1. **Chuỗi Data Corruption:**  
   `[Data corruption: blank summary, inject noise, stale date & entity swap]` ➡️ `[Quality checks FAILED: short_summaries=2, stale_rows=2]` ➡️ `[Retrieval Hit Rate giảm từ 100% -> 91.67%, Mean Token F1 giảm 0.055, Judge Score giảm 0.17]`.

2. **Chuỗi Repair Action:**  
   `[Repair action: re-build clean dataframe from raw JSON snapshot]` ➡️ `[Quality checks PASSED: passed=True, stale_rows=0]` ➡️ `[Retrieval Hit Rate phục hồi 100%, Token F1 & Judge Score phục hồi 100% về mức Baseline]`.

**Corruption nào ảnh hưởng rõ nhất và vì sao?**  
- Lỗi **`drop_latest_records`** và **`entity_swap`** ảnh hưởng rõ nhất. Việc xóa bản ghi trực tiếp làm `retrieval_hit_rate` rơi xuống 91.67% (do Vector Search không thể tìm thấy tài liệu đã bị xóa). Trong khi đó, `entity_swap` làm tráo đổi các thuật ngữ quan trọng trong summary khiến LLM trả về thông tin sai thực tế (*hallucination*), làm sụt giảm cả Token F1 lẫn điểm số từ LLM Judge.

**Kết quả nào khác với kỳ vọng ban đầu?**  
- Ban đầu em kỳ vọng chỉ số `Mean Token F1` ở trạng thái Baseline sẽ đạt trên 0.60. Tuy nhiên thực tế đạt 0.3176. Giả thuyết kiểm tra cho thấy: câu trả lời từ RAG Agent ngắn gọn và súc tích hơn so với văn bản `ground_truth` dài nguyên bản, dẫn đến tỉ lệ trùng khớp từ vựng (Token overlap) bị phạt. Tuy nhiên, chỉ số LLM Judge và Ragas Faithfulness vẫn phản ánh đúng chất lượng ngữ nghĩa thực sự của câu trả lời.

---

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về Data Pipeline:** Một Data Pipeline chuẩn Production không chỉ làm sạch dữ liệu thành công một lần, mà phải có tính **Idempotency** và khả năng tái lập/khôi phục (*Replayability*) từ các nguồn dữ liệu nguyên bản không thay đổi (*Immutable Raw Storage*).
2. **Về Data Quality & Observability:** Giám sát dữ liệu (*Observability*) phải được thực hiện chủ động trước khi dữ liệu được nạp vào Vector Store (*Pre-ingestion checks*). Phát hiện dữ liệu lỗi sớm giúp tiết kiệm chi phí gọi API LLM và tránh hỏng mô hình RAG.
3. **Về ảnh hưởng của dữ liệu tới RAG Agent:** Chất lượng câu trả lời của LLM phụ thuộc trực tiếp vào chất lượng của dữ liệu truy xuất (*"Garbage in, Garbage out"*). Lỗi dữ liệu thầm lặng ở tầng Data Ingestion sẽ khuếch đại thành lỗi sai sự thật nghiêm trọng ở đầu ra của AI Agent.

### Nếu có thêm thời gian

- **Cải thiện:** Tích hợp công cụ **Great Expectations** hoặc **Soda Core** vào tầng `quality.py` và thiết lập hệ thống cảnh báo tự động qua **Slack/Discord Webhook** khi có vi phạm SLA độ tươi (*Freshness SLA breach*).
- **Cách đo lường:** Đo thời gian phát hiện sự cố (*MTTD - Mean Time to Detect*) giảm từ hàng giờ xuống dưới 5 giây ngay khi chạy pipeline ETL.

---

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Phạm Quốc Thành  
**Ngày xác nhận:** 2026-08-06
