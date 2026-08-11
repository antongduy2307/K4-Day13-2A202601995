# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`:
- Tổng số traces:
- Số PII leak còn lại:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- **Kết quả `validate_dashboard.py`:** HỢP LỆ: 6/6 panel
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

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
