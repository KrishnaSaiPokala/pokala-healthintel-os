#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
RUN_DIR = REPO / ".run" / "basecamp6"
RUN_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = ["target","label","y","outcome","target_v4_opportunity_shock","opportunity_shock","shock"]
SEARCH_DIRS = ["data","datasets","marts","exports","pipelines",".run"]

@dataclass
class Candidate:
    path: str
    rows: int
    columns: int
    target_candidates: list[str]
    supervised_ready: bool

def count_csv(path: Path, max_rows: int = 250000):
    try:
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            r = csv.reader(f)
            header = next(r, [])
            n = 0
            for _ in r:
                n += 1
                if n >= max_rows:
                    break
            return n, header
    except Exception:
        return 0, []

def discover():
    out = []
    for d in SEARCH_DIRS:
        base = REPO / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in [".csv", ".tsv"]:
                rows, header = count_csv(p)
                if not header:
                    continue
                targets = [h for h in header if h in TARGETS]
                out.append(Candidate(str(p.relative_to(REPO)), rows, len(header), targets, bool(targets and rows >= 50)))
    return sorted(out, key=lambda x: (not x.supervised_ready, -x.rows, x.path))

def try_ml():
    try:
        import pandas as pd
        import numpy as np
        from sklearn.dummy import DummyClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, average_precision_score, brier_score_loss
        return locals() | {"ok": True}
    except Exception as e:
        return {"ok": False, "error": repr(e)}

def prep(df, target, np):
    y = df[target]
    X = df.drop(columns=[target])
    cols = {}
    for c in X.columns:
        s = X[c]
        if str(s.dtype).startswith(("int","float","bool")):
            cols[c] = s
        else:
            if s.astype(str).nunique(dropna=True) <= 50:
                cols[c] = s.astype(str).astype("category").cat.codes
    if not cols:
        raise ValueError("no usable numeric or low-cardinality features")
    X2 = df.__class__(cols).replace([np.inf, -np.inf], np.nan).fillna(0)
    vals = list(y.dropna().unique())
    if len(vals) != 2:
        raise ValueError(f"target must be binary; found {len(vals)} classes")
    y2 = y.map({vals[0]: 0, vals[1]: 1}).fillna(0).astype(int)
    return X2, y2

def score(model, X, y, m):
    pred = model.predict(X)
    out = {
        "accuracy": float(m["accuracy_score"](y, pred)),
        "balanced_accuracy": float(m["balanced_accuracy_score"](y, pred)),
        "f1": float(m["f1_score"](y, pred, zero_division=0)),
        "precision": float(m["precision_score"](y, pred, zero_division=0)),
        "recall": float(m["recall_score"](y, pred, zero_division=0)),
    }
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[:,1]
        for name, fn in [("roc_auc", m["roc_auc_score"]), ("pr_auc", m["average_precision_score"]), ("brier_score", m["brier_score_loss"])]:
            try: out[name] = float(fn(y, proba))
            except Exception: out[name] = None
    return out

def run_dataset(path: Path, target: str):
    ml = try_ml()
    if not ml["ok"]:
        return [{"model": "baseline_suite", "status": "skipped", "metrics": {}, "notes": "optional ML deps unavailable: " + ml["error"]}]
    pd, np = ml["pd"], ml["np"]
    df = pd.read_csv(path)
    if len(df) > 50000:
        df = df.sample(50000, random_state=42)
    X, y = prep(df, target, np)
    split = ml["train_test_split"](X, y, test_size=0.25, random_state=42, stratify=y)
    Xtr, Xte, ytr, yte = split
    models = [
        ("majority_baseline", ml["DummyClassifier"](strategy="most_frequent"), "floor"),
        ("logistic_regression", ml["make_pipeline"](ml["StandardScaler"](), ml["LogisticRegression"](max_iter=1000, class_weight="balanced")), "linear"),
        ("random_forest", ml["RandomForestClassifier"](n_estimators=250, random_state=42, class_weight="balanced_subsample", n_jobs=-1), "nonlinear"),
        ("hist_gradient_boosting", ml["HistGradientBoostingClassifier"](random_state=42, max_iter=250), "boosting"),
    ]
    metrics = {k: ml[k] for k in ["accuracy_score","balanced_accuracy_score","f1_score","precision_score","recall_score","roc_auc_score","average_precision_score","brier_score_loss"]}
    res = []
    for name, model, note in models:
        try:
            model.fit(Xtr, ytr)
            res.append({"model": name, "status": "completed", "metrics": score(model, Xte, yte, metrics), "notes": note})
        except Exception as e:
            res.append({"model": name, "status": "failed", "metrics": {}, "notes": repr(e)})
    return res

def write_report(manifest):
    lines = ["# Basecamp6 Real Benchmark Harness Report", "", f"Generated: {manifest['created_at_utc']}", "", "## Dataset discovery", "", "| Dataset | Rows | Columns | Targets | Ready |", "|---|---:|---:|---|---:|"]
    for d in manifest["dataset_candidates"]:
        lines.append(f"| {d['path']} | {d['rows']} | {d['columns']} | {', '.join(d['target_candidates']) or '-'} | {d['supervised_ready']} |")
    lines += ["", "## Benchmark results", "", "| Model | Status | ROC-AUC | PR-AUC | Balanced accuracy | F1 | Notes |", "|---|---|---:|---:|---:|---:|---|"]
    for r in manifest["benchmark_results"]:
        m = r.get("metrics", {})
        lines.append(f"| {r['model']} | {r['status']} | {m.get('roc_auc','-')} | {m.get('pr_auc','-')} | {m.get('balanced_accuracy','-')} | {m.get('f1','-')} | {r['notes']} |")
    lines += ["", "## Next DL step", "", "- Build explicit temporal tensors.", "- Run MLP, LSTM, GRU, TCN, FT-Transformer, Temporal Transformer, and Temporal Fusion Transformer.", "- Use early stopping, 7 seeds, calibration, ablations, and failure notes.", "", "## Boundary", "", "Research benchmark only. No CDS. No patient-level prediction. No causal/incidence claims."]
    (REPO / "docs" / "BASECAMP6_REAL_BENCHMARK_REPORT.md").write_text("\n".join(lines), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset")
    ap.add_argument("--target")
    args = ap.parse_args()
    cands = discover()
    dataset, target = args.dataset, args.target
    if not dataset or not target:
        for c in cands:
            if c.supervised_ready and c.target_candidates:
                dataset = dataset or c.path
                target = target or c.target_candidates[0]
                break
    results = []
    used = None
    if dataset and target and (REPO / dataset).exists():
        used = dataset
        results = run_dataset(REPO / dataset, target)
    else:
        results = [{"model":"baseline_suite","status":"not_ready","metrics":{},"notes":"No binary target-ready dataset discovered. Harness installed and ready."}]
    manifest = {
        "run_id": "basecamp6_real_benchmark_harness",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_used": used,
        "target_used": target,
        "dataset_candidates": [asdict(c) for c in cands[:40]],
        "benchmark_results": results,
        "planned_deep_models": ["MLP","LSTM","GRU","TCN","FT-Transformer","Temporal Transformer","Temporal Fusion Transformer"],
        "guardrails": ["No PHI","No CDS","No patient-level prediction","No passive-report causality/incidence claims"]
    }
    p = RUN_DIR / "basecamp6_real_benchmark_manifest.json"
    p.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_report(manifest)
    print(f"Wrote {p}")
    print("Wrote docs/BASECAMP6_REAL_BENCHMARK_REPORT.md")
    for r in results: print(f"- {r['model']}: {r['status']} — {r['notes']}")
if __name__ == "__main__":
    main()
