"""
Dashboard Generator - Tạo evidence dashboard từ data/logs.jsonl
Chạy: python scripts/dashboard_generator.py
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
OUTPUT_PATH = REPO_ROOT / "submission" / "evidence" / "dashboard_summary.json"


def load_logs() -> list[dict]:
    """Load all log entries from logs.jsonl"""
    if not LOG_PATH.exists():
        print(f"Không tìm thấy {LOG_PATH}")
        return []

    logs = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return logs


def calculate_latency_stats(logs: list[dict]) -> dict:
    """Calculate P50, P95, P99 latency"""
    latencies = [
        log["latency_ms"]
        for log in logs
        if log.get("event") == "response_sent" and "latency_ms" in log
    ]

    if not latencies:
        return {"p50": 0, "p95": 0, "p99": 0}

    sorted_lat = sorted(latencies)
    n = len(sorted_lat)

    def percentile(p):
        idx = int(n * p / 100)
        idx = min(idx, n - 1)
        return sorted_lat[idx]

    return {
        "p50": round(percentile(50), 1),
        "p95": round(percentile(95), 1),
        "p99": round(percentile(99), 1),
    }


def calculate_traffic_stats(logs: list[dict]) -> dict:
    """Calculate request traffic metrics"""
    requests = [log for log in logs if log.get("event") == "request_received"]

    # Count by time window (simulated)
    count = len(requests)
    rate_per_minute = count  # Simplified: all requests in assumed 1-minute window

    return {
        "count": count,
        "rate_per_minute": rate_per_minute,
    }


def calculate_error_stats(logs: list[dict]) -> dict:
    """Calculate error rate and breakdown"""
    total_requests = len([log for log in logs if log.get("event") == "request_received"])
    failed_requests = len([log for log in logs if log.get("event") == "request_failed"])

    error_rate_pct = (failed_requests / total_requests * 100) if total_requests > 0 else 0

    # Error breakdown by type (if available in payload)
    error_breakdown = defaultdict(int)
    for log in logs:
        if log.get("event") == "request_failed":
            error_type = log.get("payload", {}).get("error_type", "unknown")
            error_breakdown[error_type] += 1

    return {
        "error_rate_pct": round(error_rate_pct, 2),
        "count_by_value": dict(error_breakdown),
        "failed_requests": failed_requests,
        "total_requests": total_requests,
    }


def calculate_cost_stats(logs: list[dict]) -> dict:
    """Calculate cost metrics"""
    costs = [
        log["cost_usd"]
        for log in logs
        if log.get("event") == "response_sent" and "cost_usd" in log
    ]

    total = sum(costs) if costs else 0
    by_minute = defaultdict(float)

    # Group by minute (simplified - all in one bucket for now)
    for log in logs:
        if log.get("event") == "response_sent" and "cost_usd" in log:
            by_minute["window_1"] += log["cost_usd"]

    return {
        "sum_by_minute": {k: round(v, 6) for k, v in by_minute.items()},
        "total": round(total, 6),
    }


def calculate_token_stats(logs: list[dict]) -> dict:
    """Calculate token usage metrics"""
    tokens_in = []
    tokens_out = []

    for log in logs:
        if log.get("event") == "response_sent":
            if "tokens_in" in log:
                tokens_in.append(log["tokens_in"])
            if "tokens_out" in log:
                tokens_out.append(log["tokens_out"])

    return {
        "sum_tokens_in": sum(tokens_in),
        "sum_tokens_out": sum(tokens_out),
        "total": sum(tokens_in) + sum(tokens_out),
    }


def calculate_quality_stats(logs: list[dict]) -> dict:
    """Calculate quality proxy metrics"""
    scores = [
        log["quality_score"]
        for log in logs
        if log.get("event") == "response_sent" and "quality_score" in log
    ]

    mean_score = statistics.mean(scores) if scores else 0

    return {
        "mean": round(mean_score, 3),
        "sample_count": len(scores),
    }


def generate_dashboard_summary() -> dict:
    """Generate complete dashboard summary"""
    logs = load_logs()

    # Time range
    if logs:
        timestamps = [log.get("ts") for log in logs if log.get("ts")]
        time_range = f"{timestamps[0]} to {timestamps[-1]}" if timestamps else "N/A"
    else:
        time_range = "N/A"

    summary = {
        "generated_at": datetime.now().isoformat(),
        "time_range": time_range,
        "total_logs": len(logs),
        "panels": {
            "latency": {
                **calculate_latency_stats(logs),
                "threshold_p95_lte_3000ms": True,
                "status": "ok" if calculate_latency_stats(logs)["p95"] <= 3000 else "warning"
            },
            "traffic": {
                **calculate_traffic_stats(logs),
                "threshold_rate_gte_1": True,
                "status": "ok"
            },
            "errors": {
                **calculate_error_stats(logs),
                "threshold_error_rate_lte_2pct": True,
                "status": "ok" if calculate_error_stats(logs)["error_rate_pct"] <= 2 else "warning"
            },
            "cost": {
                **calculate_cost_stats(logs),
                "threshold_total_lte_2.5usd": True,
                "status": "ok" if calculate_cost_stats(logs)["total"] <= 2.5 else "warning"
            },
            "tokens": {
                **calculate_token_stats(logs),
                "threshold_total_lte_50000": True,
                "status": "ok" if calculate_token_stats(logs)["total"] <= 50000 else "warning"
            },
            "quality": {
                **calculate_quality_stats(logs),
                "threshold_mean_gte_0.75": True,
                "status": "ok" if calculate_quality_stats(logs)["mean"] >= 0.75 else "warning"
            },
        },
        "slo_config": {
            "latency_p95_ms": {"objective": 3000, "target": 99.5},
            "error_rate_pct": {"objective": 2, "target": 99.0},
            "quality_score_avg": {"objective": 0.75, "target": 95.0},
        },
        "alerts": [
            {"name": "HighLatency", "severity": "critical", "condition": "p95 > 3000ms for 5m"},
            {"name": "HighErrorRate", "severity": "critical", "condition": "rate > 2% for 3m"},
            {"name": "LowQualityScore", "severity": "warning", "condition": "mean < 0.75 for 10m"},
        ]
    }

    return summary


def main():
    print("=" * 60)
    print("DASHBOARD GENERATOR - Day 13 Observability Lab")
    print("=" * 60)

    summary = generate_dashboard_summary()

    # Print summary to console
    print(f"\nGenerated at: {summary['generated_at']}")
    print(f"Time range: {summary['time_range']}")
    print(f"Total log entries: {summary['total_logs']}")

    print("\n" + "-" * 60)
    print("PANEL METRICS")
    print("-" * 60)

    panels = summary["panels"]

    print(f"\n1. LATENCY (threshold: P95 <= 3000ms)")
    lat = panels["latency"]
    print(f"   P50: {lat['p50']}ms | P95: {lat['p95']}ms | P99: {lat['p99']}ms | Status: {lat['status'].upper()}")

    print(f"\n2. TRAFFIC (threshold: rate >= 1 req/min)")
    traffic = panels["traffic"]
    print(f"   Count: {traffic['count']} | Rate: {traffic['rate_per_minute']} req/min | Status: {traffic['status'].upper()}")

    print(f"\n3. ERRORS (threshold: rate <= 2%)")
    errors = panels["errors"]
    print(f"   Error rate: {errors['error_rate_pct']}% | Failed: {errors['failed_requests']}/{errors['total_requests']} | Status: {errors['status'].upper()}")

    print(f"\n4. COST (threshold: total <= $2.50)")
    cost = panels["cost"]
    print(f"   Total: ${cost['total']} | Status: {cost['status'].upper()}")

    print(f"\n5. TOKENS (threshold: total <= 50,000)")
    tokens = panels["tokens"]
    print(f"   In: {tokens['sum_tokens_in']} | Out: {tokens['sum_tokens_out']} | Total: {tokens['total']} | Status: {tokens['status'].upper()}")

    print(f"\n6. QUALITY (threshold: mean >= 0.75)")
    quality = panels["quality"]
    print(f"   Mean: {quality['mean']} | Samples: {quality['sample_count']} | Status: {quality['status'].upper()}")

    print("\n" + "-" * 60)
    print("ALERTS CONFIGURED")
    print("-" * 60)
    for alert in summary["alerts"]:
        print(f"   [{alert['severity'].upper()}] {alert['name']}: {alert['condition']}")

    # Save to file
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Dashboard summary saved to: {OUTPUT_PATH}")

    return summary


if __name__ == "__main__":
    main()
