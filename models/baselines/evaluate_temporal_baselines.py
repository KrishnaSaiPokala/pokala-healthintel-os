from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "data" / "features" / "temporal_market_sequences.csv"
OUT_DIR = ROOT / "data" / "models"
OUT = OUT_DIR / "baseline_temporal_results.json"

FEATURE_COLS = [
    "market",
    "safety",
    "reimbursement",
    "provider_density",
    "market_delta",
    "safety_delta",
    "reimbursement_delta",
]

def metric_pack(name: str, y_true, y_pred):
    return {
        "model": name,
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
    }

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(FEATURES).sort_values("t")

    if len(df) < 4:
        raise SystemExit("Need at least 4 temporal rows for baseline evaluation.")

    X = df[FEATURE_COLS].to_numpy(dtype=np.float32)
    y = df["target_next_market"].to_numpy(dtype=np.float32)

    split = max(2, int(len(df) * 0.70))
    if split >= len(df):
      split = len(df) - 1

    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    models = [
        ("persistence_mean", DummyRegressor(strategy="mean")),
        ("ridge", Ridge(alpha=1.0)),
        ("random_forest", RandomForestRegressor(n_estimators=80, random_state=42)),
    ]

    results = []
    for name, model in models:
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        results.append(metric_pack(name, y_test, pred))

    payload = {
        "status": "baseline_evaluation_complete",
        "boundary": "Prototype temporal benchmark on static demo feature sequence; not final paper-grade model yet.",
        "rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "target": "target_next_market",
        "feature_columns": FEATURE_COLS,
        "results": results,
    }

    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
