# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## High Latency

- **Tên:** HighLatency
- **Severity:** critical
- **SLI/SLO liên quan:** latency_p95_ms > 3000ms (target 99.5%)
- **Điều kiện và thời gian duy trì:** P95 latency > 3000ms trong 5 phút liên tục
- **Ảnh hưởng tới người dùng:** Requests chậm, timeout, trải nghiệm kém
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra dashboard latency panel → xác nhận P95 > 3000ms
  2. Mở Langfuse trace gần nhất → tìm span có latency cao bất thường
  3. Kiểm tra log với correlation ID của trace đó → tìm root cause
- **Mitigation tạm thời:** Restart API service hoặc tắt incident đang chạy
- **Owner:** platform-team

## High Error Rate

- **Tên:** HighErrorRate
- **Severity:** critical
- **SLI/SLO liên quan:** error_rate_pct > 2% (target 99.0%)
- **Điều kiện và thời gian duy trì:** Error rate > 2% trong 3 phút liên tục
- **Ảnh hưởng tới người dùng:** Requests thất bại, không nhận được response
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra dashboard errors panel → xác nhận error rate > 2%
  2. Xem error breakdown → xác định loại lỗi phổ biến nhất
  3. Tìm trace có error → kiểm tra log với correlation ID
- **Mitigation tạm thời:** Kiểm tra service health, restart nếu cần
- **Owner:** platform-team

## Low Quality Score

- **Tên:** LowQualityScore
- **Severity:** warning
- **SLI/SLO liên quan:** quality_score_avg < 0.75 (target 95.0%)
- **Điều kiện và thời gian duy trì:** Quality score trung bình < 0.75 trong 10 phút liên tục
- **Ảnh hưởng tới người dùng:** Responses không đạt chất lượng mong đợi
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra dashboard quality panel → xác nhận mean < 0.75
  2. Xem các requests gần đây → tìm pattern gây quality thấp
  3. Kiểm tra prompt version → có thể cần rollback hoặc improve
- **Mitigation tạm thời:** Rollback prompt về version ổn định
- **Owner:** ml-team
