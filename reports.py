"""CSV report generation."""
import csv
from pathlib import Path

FIELDS = ["id", "customer", "amount", "country", "hour", "channel", "score", "level", "reasons"]


def export_csv(records: list[dict], destination: str | Path):
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for record in records:
            row = {key: record.get(key, "") for key in FIELDS}
            row["reasons"] = "; ".join(record.get("reasons", []))
            writer.writerow(row)
    return path
