# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4-Day13-2A202601995
- Repository URL: https://github.com/antongduy2307/K4-Day13-2A202601995
- Commit SHA cuối: (điền sau khi commit)
- Thành viên và vai trò: Người 1 — Logging & PII + Tracing & Prompt Version; Người 2 — Dashboard, SLO & Alert; Người 3 — Incident, Report & Demo

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (xem `submission/evidence/validate_logs_output.txt`)
- Tổng số traces: 33 correlation ID duy nhất trong log, trong đó 25 trace có `response_sent` (xem `submission/evidence/trace_list.txt`)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `submission/evidence/dashboard_summary.json` + `submission/evidence/validate_dashboard_result.txt` (Người 2); Langfuse traces tại project đã cấu hình trong `.env` (không commit key)

## 3. Logging và tracing

- Evidence correlation ID: mỗi request có header `x-request-id` dạng `req-<8hex>`, ví dụ `req-5fa93c50` (xem `submission/evidence/logs_sample.jsonl`)
- Evidence PII redaction: gửi message chứa email/SĐT/thẻ giả — log ghi `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]` thay vì giá trị gốc, xác nhận tại trace `req-5fa93c50`
- Evidence trace waterfall: mở trace `req-dc5efa0f` trên Langfuse (generation span của `LabAgent.run`), span kéo dài ~2650ms do bước retrieve khi `rag_slow` bật
- Giải thích một span đáng chú ý: generation span của trace `req-dc5efa0f` có `metadata.doc_count`, `prompt_name=day13-chat`, `prompt_version=3`; gần như toàn bộ latency nằm ở bước retrieve (RAG), không phải LLM call (LLM luôn `sleep(0.15)` cố định)

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 3, label `baseline` (+ `production` sau rollback)
- Version/label candidate: version 4, label `candidate` (thêm dòng "Answer in at most 3 short sentences.")
- Trace ID của mỗi version:
  - baseline (v3): `req-6339f398` (tokens_in=26)
  - candidate (v4): `req-e5bf853c` (tokens_in=35)
- Bằng chứng đổi label hoặc rollback:
  - Chuyển `production` → v4: `req-f0fd83e7` (tokens_in=35, khớp v4)
  - Rollback `production` → v3: `req-10377886` (tokens_in=26, khớp v3, sau khi restart để bỏ cache 60s)

## 5. Dashboard, SLO và alerts

- **Kết quả `validate_dashboard.py`:** HỢP LỆ: 6/6 panel (xác nhận lại lần chạy này, xem `submission/evidence/validate_dashboard_result.txt`)
- **Evidence dashboard:**
  - [dashboard_summary.json](submission/evidence/dashboard_summary.json) - Metrics từ logs.jsonl
  - [validate_dashboard_result.txt](submission/evidence/validate_dashboard_result.txt) - Validator output
  - [alert_rules_config.yaml](submission/evidence/alert_rules_config.yaml) - Alert configuration

- **SLO đã chọn và lý do:**
  | SLI | Objective | Target | Lý do |
  |-----|-----------|--------|-------|
  | latency_p95_ms | 3000ms | 99.5% | Đảm bảo 99.5% requests hoàn thành trong 3s |
  | error_rate_pct | 2% | 99.0% | Giới hạn 2% requests thất bại |
  | quality_score_avg | 0.75 | 95.0% | Đảm bảo 95% responses đạt quality tối thiểu |

- **Alert rules và runbook:**
  | Alert | Severity | Condition | Owner | Runbook |
  |-------|----------|-----------|-------|---------|
  | HighLatency | critical | P95 > 3000ms for 5m | platform-team | [alerts.md#high-latency](docs/alerts.md#high-latency) |
  | HighErrorRate | critical | Rate > 2% for 3m | platform-team | [alerts.md#high-error-rate](docs/alerts.md#high-error-rate) |
  | LowQualityScore | warning | Mean < 0.75 for 10m | ml-team | [alerts.md#low-quality-score](docs/alerts.md#low-quality-score) |

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1` (cohort K4, incident `rag_slow`, `latency_threshold_ms=2000`)
- Triệu chứng từ metrics: `/metrics` trước challenge báo `latency_p95: 1104ms`; sau khi chạy 5 query challenge chính thức, `latency_p95` tăng lên **2651ms**, vượt `latency_threshold_ms=2000` quy định trong `config/challenge.json`
- Trace ID liên quan: `req-dc5efa0f`, `req-bbdb67ed`, `req-436bb985`, `req-3cda4920`, `req-8638cf30` (5 trace của 5 query challenge, mỗi trace log latency ~2650-2651ms)
- Log line/correlation ID liên quan: log `response_sent` của `req-dc5efa0f` ghi `"latency_ms": 2650`, `"feature": "monitoring"` — khớp `affected_feature` trong challenge.json
- Root cause: `app/mock_rag.py:retrieve()` gọi `time.sleep(2.5)` khi `STATE["rag_slow"]` bật. Ngoài ra route `/chat` xử lý đồng bộ (blocking) trong async handler, nên dưới concurrency=5 các request bị serialize trên cùng event loop — wall-time client đo được từ 5.3s đến 13.3s (tăng dần theo thứ tự request), dù mỗi request chỉ log 2650ms — chứng tỏ lỗi bị khuếch đại thêm bởi cách xử lý đồng thời, không chỉ do RAG chậm
- Fix action: đã tắt incident bằng `python scripts/inject_incident.py --disable`, latency về lại 150ms (`req-8e786bbe`), xác nhận đúng nguyên nhân. Fix lâu dài đề xuất: chạy bước retrieve trong threadpool riêng (`run_in_threadpool`) thay vì block event loop chính, để một request chậm không kéo chậm toàn bộ hàng đợi; đồng thời khắc phục nguyên nhân RAG chậm thực tế (timeout/index) thay vì chỉ tắt flag
- Preventive measure: alert `HighLatency` (P95 > 3000ms trong 5 phút, `config/alert_rules.yaml`) để phát hiện sớm; thêm timeout cứng cho bước retrieve kèm circuit breaker để một dependency chậm không kéo sập toàn bộ throughput

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Tống Duy An - 01995 | Logging & PII (correlation ID, enrichment, redaction) + Tracing & Prompt Version (prompt v1/v2, label, rollback) | `a068d6f` | JSON structured logging, structlog contextvars, regex PII redaction, Langfuse prompt management |
| Nguyễn Việt Đăng Khoa - 01794 | Dashboard, SLO & Alert (6 panel, threshold, SLO, alert rules, runbook) | `f572a80` | percentile/aggregation theo contract, symptom-based alerting |
| Ngô Mạnh Minh Huy - 01926| Incident, Report & Demo: chạy challenge chính thức, nối Metrics → Traces → Logs, xác định root cause, viết report, chuẩn bị demo | (điền commit SHA sau khi commit) | luồng điều tra incident thực tế, phân biệt symptom (metrics) và root cause (log/trace), ảnh hưởng của xử lý đồng bộ trong async handler tới latency dưới tải đồng thời |
