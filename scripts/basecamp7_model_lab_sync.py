#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE6 = REPO / ".run" / "basecamp6" / "basecamp6_real_benchmark_manifest.json"
OUT = REPO / "apps" / "web" / "src" / "data" / "model_benchmark.json"
DOC = REPO / "docs" / "BASECAMP7_MODEL_LAB_SYNC.md"

def now():
    return datetime.now(timezone.utc).isoformat()

def load_base6():
    if BASE6.exists():
        return json.loads(BASE6.read_text(encoding="utf-8"))
    return {
        "run_id": "basecamp6_missing_local_manifest",
        "created_at_utc": None,
        "dataset_used": None,
        "target_used": None,
        "benchmark_results": [],
        "planned_deep_models": ["MLP", "LSTM", "GRU", "TCN", "FT-Transformer", "Temporal Transformer"],
        "guardrails": ["No PHI", "No CDS", "No patient-level prediction"],
    }

def try_mlp(dataset_rel, target):
    if not dataset_rel or not target:
        return {"model": "mlp_classifier", "status": "not_ready", "metrics": {}, "notes": "No dataset/target available from Basecamp6 manifest."}
    path = REPO / dataset_rel
    if not path.exists():
        return {"model": "mlp_classifier", "status": "skipped", "metrics": {}, "notes": f"Dataset not found locally: {dataset_rel}"}
    try:
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.neural_network import MLPClassifier
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import balanced_accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, average_precision_score, brier_score_loss
    except Exception as e:
        return {"model": "mlp_classifier", "status": "skipped", "metrics": {}, "notes": "Optional sklearn/pandas dependencies unavailable: " + repr(e)}
    try:
        df = pd.read_csv(path)
        if len(df) > 50000:
            df = df.sample(50000, random_state=42)
        y = df[target]
        X = df.drop(columns=[target])
        cols = {}
        for c in X.columns:
            s = X[c]
            if str(s.dtype).startswith(("int", "float", "bool")):
                cols[c] = s
            else:
                if s.astype(str).nunique(dropna=True) <= 50:
                    cols[c] = s.astype(str).astype("category").cat.codes
        if not cols:
            raise ValueError("No usable numeric/low-cardinality features found.")
        X2 = pd.DataFrame(cols).replace([np.inf, -np.inf], np.nan).fillna(0)
        vals = list(y.dropna().unique())
        if len(vals) != 2:
            raise ValueError(f"Target must be binary; found {len(vals)} classes.")
        y2 = y.map({vals[0]: 0, vals[1]: 1}).fillna(0).astype(int)
        Xtr, Xte, ytr, yte = train_test_split(X2, y2, test_size=0.25, random_state=7, stratify=y2)
        model = make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(128, 64), activation="relu", solver="adam",
                          max_iter=500, early_stopping=True, n_iter_no_change=25,
                          random_state=7, learning_rate_init=0.001)
        )
        model.fit(Xtr, ytr)
        pred = model.predict(Xte)
        proba = model.predict_proba(Xte)[:, 1]
        metrics = {
            "balanced_accuracy": float(balanced_accuracy_score(yte, pred)),
            "f1": float(f1_score(yte, pred, zero_division=0)),
            "precision": float(precision_score(yte, pred, zero_division=0)),
            "recall": float(recall_score(yte, pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(yte, proba)),
            "pr_auc": float(average_precision_score(yte, proba)),
            "brier_score": float(brier_score_loss(yte, proba)),
        }
        return {"model": "mlp_classifier", "status": "completed", "metrics": metrics, "notes": "Real sklearn MLP baseline with early stopping; one seed only, not final DL claim."}
    except Exception as e:
        return {"model": "mlp_classifier", "status": "failed", "metrics": {}, "notes": repr(e)}

def main():
    base6 = load_base6()
    mlp = try_mlp(base6.get("dataset_used"), base6.get("target_used"))
    payload = {
        "run_id": "basecamp7_model_lab_sync",
        "generated_at_utc": now(),
        "source_manifest": "basecamp6_real_benchmark_manifest.json" if BASE6.exists() else "missing local .run manifest",
        "dataset_used": base6.get("dataset_used"),
        "target_used": base6.get("target_used"),
        "benchmark_results": base6.get("benchmark_results", []),
        "deep_results": [mlp],
        "planned_deep_models": ["MLP", "LSTM", "GRU", "Temporal CNN / TCN", "FT-Transformer / TabTransformer", "Temporal Transformer", "Temporal Fusion Transformer", "Evidence transformer retrieval layer"],
        "next_run_requirements": ["Build explicit temporal tensors", "Run 7-seed MLP/LSTM/GRU/TCN/Transformer comparisons", "Track early stopping and best checkpoints", "Report calibration/Brier score", "Add feature-family and source-family ablations", "Write failure-mode notes"],
        "claim_boundary": "Research benchmark only. No PHI. Not clinical decision support. No patient-level prediction.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = ["# Basecamp7 Model Lab Sync", "", f"Generated: {payload['generated_at_utc']}", "", "Basecamp7 syncs real Basecamp6 baseline outputs into frontend-readable JSON and attempts a real MLP baseline with early stopping.", "", f"- Dataset: {payload['dataset_used'] or 'not available'}", f"- Target: {payload['target_used'] or 'not available'}", "", "## Results", "", "| Model | Status | ROC-AUC | PR-AUC | Balanced accuracy | F1 | Notes |", "|---|---|---:|---:|---:|---:|---|"]
    for r in payload["benchmark_results"] + payload["deep_results"]:
        m = r.get("metrics", {})
        lines.append(f"| {r.get('model')} | {r.get('status')} | {m.get('roc_auc','-')} | {m.get('pr_auc','-')} | {m.get('balanced_accuracy','-')} | {m.get('f1','-')} | {r.get('notes','')} |")
    lines += ["", "## Boundary", "", payload["claim_boundary"]]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Wrote {DOC}")
    print(f"MLP status: {mlp['status']} -- {mlp['notes']}")

if __name__ == "__main__":
    main()
