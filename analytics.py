"""Aggregations for the dashboard and charts."""
from collections import Counter


def summarize(records: list[dict]) -> dict:
    total = len(records)
    levels = Counter(r["level"] for r in records)
    alerts = sum(1 for r in records if r["score"] > 0)
    amount_total = sum(float(r["amount"]) for r in records)
    return {
        "total": total,
        "alerts": alerts,
        "high": levels["HIGH"],
        "medium": levels["MEDIUM"],
        "low": levels["LOW"],
        "amount_total": amount_total,
        "alert_rate": (alerts / total * 100) if total else 0.0,
    }


def level_distribution(records: list[dict]) -> dict[str, int]:
    return {level: sum(1 for r in records if r["level"] == level) for level in ("LOW", "MEDIUM", "HIGH")}


def hourly_distribution(records: list[dict]) -> dict[int, int]:
    return {hour: sum(1 for r in records if int(r["hour"]) == hour) for hour in range(24)}
