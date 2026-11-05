# FraudShield 2.0 — Transaction Monitoring Prototype

Desktop educational prototype for exploring transaction monitoring, explainable rule-based alerts, local persistence, reporting, analytics, and an optional unsupervised anomaly experiment.

## Features
- Dark Tkinter desktop dashboard with transaction metrics.
- SQLite database: records remain available after closing the application.
- Explainable rules: configurable high-amount threshold, unusual transaction hour, and country code flagged for review.
- Risk levels LOW / MEDIUM / HIGH with reasons and a simple score.
- Search by transaction or customer ID; filter by risk level.
- Register transactions with basic validation.
- Export analyzed records to CSV.
- Optional Isolation Forest anomaly experiment via scikit-learn.
- Analytics summary including total volume, alert rate and risk counts.

## Requirements
- Python 3.10+
- Tkinter (normally included with Windows Python)
- matplotlib, pandas and scikit-learn may be installed for future extensions; the current dashboard does not require matplotlib or pandas. scikit-learn is required only for the optional ML button.

Install optional ML dependency:
```powershell
python -m pip install scikit-learn
```

Run:
```powershell
python fraudshield.py
```

## Files
- `fraudshield.py`: desktop interface and application controller.
- `database.py`: SQLite persistence.
- `risk_engine.py`: explainable rule-based scoring.
- `analytics.py`: summary calculations.
- `reports.py`: CSV export.
- `fraud_model.py`: optional Isolation Forest experiment.

The SQLite file `fraudshield.db` is created automatically next to the Python files. Initial sample transactions are inserted only when the database is empty.

## Important limitations
All included data is fictional. The rules and optional anomaly model are demonstrations, not validated financial risk models. An alert or anomaly is not proof of fraud. Do not use this prototype to approve/decline credit, block payments, or make real financial decisions. Do not enter real customer or personal data.
