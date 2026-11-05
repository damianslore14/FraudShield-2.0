"""Explainable, rule-based transaction risk scoring for synthetic/demo data."""
from dataclasses import dataclass
from typing import Any

@dataclass
class RiskResult:
    score: int
    level: str
    reasons: list[str]


def assess_transaction(tx: dict[str, Any], amount_threshold: float = 5000,
                       review_country_codes: set[str] | None = None) -> RiskResult:
    """Return indicators and a simple score. Alerts are not proof of fraud."""
    review_country_codes = review_country_codes or {"XX"}
    reasons: list[str] = []
    amount = float(tx["amount"])
    hour = int(tx["hour"])
    country = str(tx["country"]).upper()

    if amount >= amount_threshold:
        reasons.append(f"Amount at/above threshold (S/ {amount_threshold:,.2f})")
    if hour <= 4 or hour >= 23:
        reasons.append("Unusual hour (00:00–04:59 or 23:00)")
    if country in review_country_codes:
        reasons.append(f"Country code flagged for review ({country})")

    score = len(reasons)
    level = "HIGH" if score >= 2 else "MEDIUM" if score == 1 else "LOW"
    return RiskResult(score=score, level=level, reasons=reasons)
