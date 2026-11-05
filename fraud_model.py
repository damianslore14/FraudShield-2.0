"""Optional experimental anomaly model. Requires scikit-learn.

Isolation Forest is unsupervised: it finds unusual patterns, not confirmed fraud.
It is trained only on the synthetic/demo records in this prototype.
"""

def detect_anomalies(records: list[dict]) -> list[dict]:
    if len(records) < 5:
        raise ValueError("Se necesitan al menos 5 transacciones para la demo del modelo.")
    try:
        from sklearn.ensemble import IsolationForest
    except ImportError as exc:
        raise RuntimeError("Instala scikit-learn con: pip install scikit-learn") from exc

    # Numeric features only; country/channel are intentionally not encoded here.
    features = [[float(r["amount"]), int(r["hour"])] for r in records]
    model = IsolationForest(contamination=0.20, random_state=42)
    predictions = model.fit_predict(features)
    scores = model.decision_function(features)
    output = []
    for record, prediction, score in zip(records, predictions, scores):
        output.append({
            "id": record["id"],
            "model_result": "ANOMALY - REVIEW" if prediction == -1 else "NORMAL PATTERN",
            "anomaly_score": round(float(score), 4),
        })
    return output
