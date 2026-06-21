from __future__ import annotations

import json
import math
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    precision_recall_curve,
    auc,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_OK = True
except Exception as exc:
    TORCH_OK = False
    TORCH_IMPORT_ERROR = str(exc)

REPO = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")

RUN_DIR = REPO / ".run" / "overnight_core_dl"
LOG_PATH = RUN_DIR / "overnight_core_dl_events.jsonl"
PARTIAL_PATH = RUN_DIR / "overnight_core_dl_partial.json"
FINAL_RUN_PATH = RUN_DIR / "overnight_core_dl_final.json"

FRONTEND_PATH = REPO / "apps" / "web" / "src" / "data" / "deep_benchmark_overnight.json"
DOC_PATH = REPO / "docs" / "OVERNIGHT_CORE_DL_BENCHMARK.md"

RUN_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_PATH.parent.mkdir(parents=True, exist_ok=True)
DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

SEEDS = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79]

MAX_ROWS = int(os.environ.get("POKALA_DL_MAX_ROWS", "50000"))
MAX_FEATURES = int(os.environ.get("POKALA_DL_MAX_FEATURES", "120"))
EPOCHS = int(os.environ.get("POKALA_DL_EPOCHS", "240"))
PATIENCE = int(os.environ.get("POKALA_DL_PATIENCE", "28"))
BATCH_SIZE = int(os.environ.get("POKALA_DL_BATCH_SIZE", "256"))

TARGET_HINTS = [
    "target",
    "label",
    "outcome",
    "class",
    "risk",
    "flag",
    "event",
    "status",
    "adverse",
    "safety",
    "approval",
    "success",
    "failure",
]


def now_iso() -> str:
    return pd.Timestamp.utcnow().isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except Exception:
        return str(path)


def log_event(event: dict[str, Any]) -> None:
    event = dict(event)
    event["ts_utc"] = now_iso()
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, default=str) + "\n")
    print(json.dumps(event, default=str), flush=True)


def safe_float(x: Any) -> float | None:
    try:
        if x is None:
            return None
        val = float(x)
        if math.isnan(val) or math.isinf(val):
            return None
        return round(val, 6)
    except Exception:
        return None


def pr_auc_score(y_true: np.ndarray, prob_pos: np.ndarray) -> float | None:
    try:
        p, r, _ = precision_recall_curve(y_true, prob_pos)
        return float(auc(r, p))
    except Exception:
        return None


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, proba: np.ndarray | None) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "accuracy": safe_float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": safe_float(balanced_accuracy_score(y_true, y_pred)),
        "f1_macro": safe_float(f1_score(y_true, y_pred, average="macro")),
    }

    classes = sorted(set(np.asarray(y_true).tolist()))
    is_binary = len(classes) == 2

    if proba is not None:
        try:
            if is_binary:
                prob_pos = proba[:, 1] if proba.ndim == 2 and proba.shape[1] > 1 else proba.reshape(-1)
                metrics["roc_auc"] = safe_float(roc_auc_score(y_true, prob_pos))
                metrics["pr_auc"] = safe_float(pr_auc_score(y_true, prob_pos))
                metrics["brier"] = safe_float(brier_score_loss(y_true, prob_pos))
            else:
                metrics["roc_auc_ovr"] = safe_float(roc_auc_score(y_true, proba, multi_class="ovr"))
        except Exception as exc:
            metrics["probability_metric_warning"] = str(exc)[:300]

    return metrics


def summarize_seed_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [r for r in rows if r.get("status") == "completed"]
    summary: dict[str, Any] = {
        "completed_seeds": len(completed),
        "failed_seeds": len([r for r in rows if r.get("status") == "failed"]),
    }

    metric_keys = sorted({k for row in completed for k in row.get("metrics", {}).keys()})

    for key in metric_keys:
        vals = []
        for row in completed:
            v = row.get("metrics", {}).get(key)
            if isinstance(v, (int, float)) and not math.isnan(float(v)):
                vals.append(float(v))

        if vals:
            summary[key] = {
                "mean": round(float(np.mean(vals)), 6),
                "std": round(float(np.std(vals)), 6),
                "min": round(float(np.min(vals)), 6),
                "max": round(float(np.max(vals)), 6),
                "n": len(vals),
            }

    runtimes = [float(r.get("runtime_seconds", 0)) for r in completed if isinstance(r.get("runtime_seconds"), (int, float))]
    if runtimes:
        summary["runtime_seconds"] = {
            "mean": round(float(np.mean(runtimes)), 3),
            "total": round(float(np.sum(runtimes)), 3),
            "max": round(float(np.max(runtimes)), 3),
        }

    return summary


def find_csv_candidates() -> list[Path]:
    roots = [
        REPO / "data",
        REPO / "datasets",
        REPO / "exports",
        REPO / "pipelines",
        REPO / ".run",
        REPO / "apps" / "web" / "src" / "data",
    ]

    candidates: list[Path] = []
    for root in roots:
        if not root.exists():
            continue

        for path in root.rglob("*.csv"):
            parts = set(path.parts)
            if "node_modules" in parts or "dist" in parts or ".git" in parts or ".venv" in parts:
                continue

            try:
                size = path.stat().st_size
            except Exception:
                continue

            if 1024 <= size <= 750_000_000:
                candidates.append(path)

    return sorted(candidates, key=lambda p: p.stat().st_size, reverse=True)


def infer_target(df: pd.DataFrame) -> str | None:
    cols = list(df.columns)
    hinted = []

    for c in cols:
        lc = str(c).lower()
        if any(h in lc for h in TARGET_HINTS):
            hinted.append(c)

    candidates = hinted + [c for c in cols if c not in hinted]

    best = None
    best_score = -10_000

    for c in candidates:
        s = df[c].dropna()
        if len(s) < 300:
            continue

        nunique = s.nunique(dropna=True)
        if not (2 <= nunique <= 12):
            continue

        lc = str(c).lower()
        score = 0

        if c in hinted:
            score += 50
        if nunique == 2:
            score += 35
        if 3 <= nunique <= 6:
            score += 10
        if any(h in lc for h in ["id", "zip", "year", "date", "npi", "code", "fips"]):
            score -= 60
        if "status" in lc or "flag" in lc or "class" in lc:
            score += 20

        vc = s.astype(str).value_counts(normalize=True)
        if len(vc) > 1:
            imbalance = float(vc.iloc[0])
            if imbalance > 0.98:
                score -= 45
            elif imbalance > 0.92:
                score -= 15
            else:
                score += 10

        if score > best_score:
            best_score = score
            best = c

    return str(best) if best is not None else None


def load_dataset() -> tuple[pd.DataFrame, str, Path, dict[str, Any]]:
    attempted = []

    for path in find_csv_candidates():
        try:
            log_event({"event": "dataset_candidate", "path": rel(path), "size_bytes": path.stat().st_size})
            df = pd.read_csv(path, low_memory=False)
            attempted.append({"path": rel(path), "rows": int(len(df)), "columns": int(len(df.columns))})

            if len(df) < 500:
                continue

            target = infer_target(df)
            if not target:
                continue

            numeric_cols = []
            for c in df.columns:
                if c == target:
                    continue
                if pd.api.types.is_numeric_dtype(df[c]):
                    numeric_cols.append(c)
                else:
                    coerced = pd.to_numeric(df[c], errors="coerce")
                    if coerced.notna().mean() > 0.70:
                        df[c] = coerced
                        numeric_cols.append(c)

            if len(numeric_cols) >= 5:
                log_event({"event": "dataset_selected", "path": rel(path), "target": target, "numeric_features": len(numeric_cols)})
                return df, target, path, {"attempted": attempted}

        except Exception as exc:
            attempted.append({"path": rel(path), "error": str(exc)[:500]})
            log_event({"event": "dataset_candidate_failed", "path": rel(path), "error": str(exc)[:300]})

    raise RuntimeError("No usable classification CSV found for overnight DL run.")


def prepare_matrix(df: pd.DataFrame, target: str) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    usable = df.dropna(subset=[target]).copy()

    if len(usable) > MAX_ROWS:
        usable = usable.sample(MAX_ROWS, random_state=2026)

    numeric_cols = []
    for c in usable.columns:
        if c == target:
            continue

        if pd.api.types.is_numeric_dtype(usable[c]):
            numeric_cols.append(c)
        else:
            coerced = pd.to_numeric(usable[c], errors="coerce")
            if coerced.notna().mean() > 0.70:
                usable[c] = coerced
                numeric_cols.append(c)

    numeric_cols = numeric_cols[:MAX_FEATURES]

    Xdf = usable[numeric_cols].replace([np.inf, -np.inf], np.nan)
    Xdf = Xdf.fillna(Xdf.median(numeric_only=True)).fillna(0)

    le = LabelEncoder()
    y = le.fit_transform(usable[target].astype(str))

    vc = pd.Series(y).value_counts()
    keep_classes = set(vc[vc >= 20].index.tolist())
    mask = np.array([v in keep_classes for v in y])

    X = Xdf.to_numpy(dtype=np.float32)[mask]
    y = y[mask]

    if len(set(y.tolist())) < 2:
        raise RuntimeError("Target collapsed to fewer than two usable classes.")

    meta = {
        "rows_sample_cap": MAX_ROWS,
        "rows_after_target_drop": int(len(usable)),
        "rows_after_class_filter": int(len(y)),
        "feature_count": int(len(numeric_cols)),
        "features": [str(c) for c in numeric_cols],
        "target_classes": [str(c) for c in le.classes_],
        "class_counts": {str(k): int(v) for k, v in pd.Series(y).value_counts().sort_index().items()},
    }

    return X, y, meta


def save_partial(payload: dict[str, Any]) -> None:
    PARTIAL_PATH.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8", newline="\n")


def run_sklearn_mlp(X: np.ndarray, y: np.ndarray, payload: dict[str, Any]) -> dict[str, Any]:
    model_id = "sklearn_mlp_21_seed"
    log_event({"event": "model_start", "model_id": model_id})

    per_seed = []

    for seed in SEEDS:
        start = time.time()
        log_event({"event": "seed_start", "model_id": model_id, "seed": seed})

        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.25,
                random_state=seed,
                stratify=y,
            )

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            model = MLPClassifier(
                hidden_layer_sizes=(256, 128, 64),
                activation="relu",
                solver="adam",
                alpha=1e-4,
                learning_rate_init=8e-4,
                batch_size=256,
                max_iter=500,
                early_stopping=True,
                n_iter_no_change=30,
                validation_fraction=0.15,
                random_state=seed,
            )

            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            proba = model.predict_proba(X_test)

            row = {
                "seed": seed,
                "status": "completed",
                "epochs_or_iterations": int(getattr(model, "n_iter_", 0)),
                "runtime_seconds": round(time.time() - start, 3),
                "metrics": classification_metrics(y_test, pred, proba),
            }

        except Exception as exc:
            row = {
                "seed": seed,
                "status": "failed",
                "runtime_seconds": round(time.time() - start, 3),
                "reason": str(exc)[:800],
            }

        per_seed.append(row)
        log_event({"event": "seed_end", "model_id": model_id, "seed": seed, "status": row["status"], "runtime_seconds": row["runtime_seconds"]})

        payload["models_live"][model_id] = {"model_id": model_id, "per_seed": per_seed, "summary": summarize_seed_metrics(per_seed)}
        save_partial(payload)

    result = {
        "model_id": model_id,
        "model_family": "MLP",
        "framework": "scikit-learn",
        "status": "completed" if any(r.get("status") == "completed" for r in per_seed) else "failed",
        "notes": "Twenty-one-seed sklearn MLP with early stopping. Benchmark signal only, not a clinical model claim.",
        "per_seed": per_seed,
        "summary": summarize_seed_metrics(per_seed),
    }

    log_event({"event": "model_end", "model_id": model_id, "status": result["status"]})
    return result


def torch_results_if_unavailable() -> list[dict[str, Any]]:
    mids = [
        "torch_mlp_21_seed",
        "torch_residual_mlp_21_seed",
        "torch_wide_deep_mlp_21_seed",
        "torch_lstm_21_seed",
        "torch_gru_21_seed",
        "torch_tcn_21_seed",
        "torch_transformer_encoder_21_seed",
        "torch_cnn_mlp_hybrid_21_seed",
        "torch_gated_mlp_21_seed",
    ]

    return [
        {
            "model_id": mid,
            "status": "skipped",
            "reason": f"PyTorch unavailable: {TORCH_IMPORT_ERROR}",
        }
        for mid in mids
    ]


def run_torch_suite(X: np.ndarray, y: np.ndarray, payload: dict[str, Any]) -> list[dict[str, Any]]:
    if not TORCH_OK:
        return torch_results_if_unavailable()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    n_classes = int(len(set(y.tolist())))
    input_dim = int(X.shape[1])

    class TorchMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(),
                nn.Dropout(0.25),
                nn.Linear(256, 128),
                nn.BatchNorm1d(128),
                nn.ReLU(),
                nn.Dropout(0.20),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, n_classes),
            )

        def forward(self, x):
            if x.ndim == 3:
                x = x[:, -1, :]
            return self.net(x)

    class ResidualMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.inp = nn.Linear(input_dim, 128)
            self.block1 = nn.Sequential(nn.Linear(128, 128), nn.ReLU(), nn.Dropout(0.20), nn.Linear(128, 128))
            self.block2 = nn.Sequential(nn.Linear(128, 128), nn.ReLU(), nn.Dropout(0.20), nn.Linear(128, 128))
            self.out = nn.Linear(128, n_classes)

        def forward(self, x):
            if x.ndim == 3:
                x = x[:, -1, :]
            h = F.relu(self.inp(x))
            h = F.relu(h + self.block1(h))
            h = F.relu(h + self.block2(h))
            return self.out(h)

    class WideDeepMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.deep = nn.Sequential(
                nn.Linear(input_dim, 256),
                nn.ReLU(),
                nn.Dropout(0.20),
                nn.Linear(256, 128),
                nn.ReLU(),
            )
            self.wide = nn.Linear(input_dim, 64)
            self.out = nn.Linear(128 + 64, n_classes)

        def forward(self, x):
            if x.ndim == 3:
                x = x[:, -1, :]
            d = self.deep(x)
            w = F.relu(self.wide(x))
            return self.out(torch.cat([d, w], dim=1))

    class GatedMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.value = nn.Linear(input_dim, 128)
            self.gate = nn.Linear(input_dim, 128)
            self.mid = nn.Sequential(nn.ReLU(), nn.Dropout(0.20), nn.Linear(128, 64), nn.ReLU())
            self.out = nn.Linear(64, n_classes)

        def forward(self, x):
            if x.ndim == 3:
                x = x[:, -1, :]
            h = self.value(x) * torch.sigmoid(self.gate(x))
            h = self.mid(h)
            return self.out(h)

    class LSTMClassifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.rnn = nn.LSTM(input_dim, 96, num_layers=2, dropout=0.15, batch_first=True)
            self.out = nn.Linear(96, n_classes)

        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            h, _ = self.rnn(x)
            return self.out(h[:, -1, :])

    class GRUClassifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.rnn = nn.GRU(input_dim, 96, num_layers=2, dropout=0.15, batch_first=True)
            self.out = nn.Linear(96, n_classes)

        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            h, _ = self.rnn(x)
            return self.out(h[:, -1, :])

    class TCNClassifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.proj = nn.Linear(input_dim, 96)
            self.conv1 = nn.Conv1d(96, 96, kernel_size=1)
            self.conv2 = nn.Conv1d(96, 96, kernel_size=1)
            self.conv3 = nn.Conv1d(96, 96, kernel_size=1)
            self.out = nn.Linear(96, n_classes)

        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            z = self.proj(x).transpose(1, 2)
            z = F.relu(self.conv1(z))
            z = F.relu(self.conv2(z))
            z = F.relu(self.conv3(z))
            z = z.mean(dim=2)
            return self.out(z)

    class TransformerClassifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.proj = nn.Linear(input_dim, 96)
            layer = nn.TransformerEncoderLayer(
                d_model=96,
                nhead=4,
                dim_feedforward=192,
                dropout=0.18,
                batch_first=True,
            )
            self.encoder = nn.TransformerEncoder(layer, num_layers=3)
            self.out = nn.Linear(96, n_classes)

        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            z = self.proj(x)
            z = self.encoder(z)
            return self.out(z[:, -1, :])

    class CNNMLPHybrid(nn.Module):
        def __init__(self):
            super().__init__()
            self.proj = nn.Linear(input_dim, 128)
            self.conv = nn.Conv1d(128, 128, kernel_size=1)
            self.mlp = nn.Sequential(nn.Linear(128, 96), nn.ReLU(), nn.Dropout(0.20), nn.Linear(96, n_classes))

        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            z = self.proj(x).transpose(1, 2)
            z = F.relu(self.conv(z)).mean(dim=2)
            return self.mlp(z)

    model_specs = [
        ("torch_mlp_21_seed", "MLP", TorchMLP),
        ("torch_residual_mlp_21_seed", "ResidualMLP", ResidualMLP),
        ("torch_wide_deep_mlp_21_seed", "WideDeepMLP", WideDeepMLP),
        ("torch_lstm_21_seed", "LSTM", LSTMClassifier),
        ("torch_gru_21_seed", "GRU", GRUClassifier),
        ("torch_tcn_21_seed", "TCN", TCNClassifier),
        ("torch_transformer_encoder_21_seed", "TransformerEncoder", TransformerClassifier),
        ("torch_cnn_mlp_hybrid_21_seed", "CNNMLPHybrid", CNNMLPHybrid),
        ("torch_gated_mlp_21_seed", "GatedMLP", GatedMLP),
    ]

    def train_one(model_ctor, seed: int) -> dict[str, Any]:
        start = time.time()

        torch.manual_seed(seed)
        np.random.seed(seed)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=seed,
            stratify=y,
        )

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train).astype(np.float32)
        X_test = scaler.transform(X_test).astype(np.float32)

        X_train_t = torch.tensor(X_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.long)
        X_test_t = torch.tensor(X_test, dtype=torch.float32).to(device)

        train_ds = TensorDataset(X_train_t, y_train_t)
        train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

        model = model_ctor().to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=8e-4, weight_decay=1e-4)
        loss_fn = nn.CrossEntropyLoss()

        best_loss = float("inf")
        bad_epochs = 0
        epochs_run = 0

        for epoch in range(EPOCHS):
            model.train()
            total_loss = 0.0
            batch_count = 0

            for xb, yb in train_dl:
                xb = xb.to(device)
                yb = yb.to(device)

                opt.zero_grad()
                logits = model(xb)
                loss = loss_fn(logits, yb)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 3.0)
                opt.step()

                total_loss += float(loss.detach().cpu())
                batch_count += 1

            epochs_run = epoch + 1
            avg_loss = total_loss / max(1, batch_count)

            if avg_loss + 1e-5 < best_loss:
                best_loss = avg_loss
                bad_epochs = 0
            else:
                bad_epochs += 1

            if bad_epochs >= PATIENCE:
                break

        model.eval()
        with torch.no_grad():
            logits = model(X_test_t)
            prob = torch.softmax(logits, dim=1).detach().cpu().numpy()
            pred = prob.argmax(axis=1)

        return {
            "seed": seed,
            "status": "completed",
            "epochs_or_iterations": int(epochs_run),
            "runtime_seconds": round(time.time() - start, 3),
            "metrics": classification_metrics(y_test, pred, prob),
        }

    all_results = []

    for model_id, family, ctor in model_specs:
        log_event({"event": "model_start", "model_id": model_id, "family": family, "device": device})
        per_seed = []

        for seed in SEEDS:
            log_event({"event": "seed_start", "model_id": model_id, "seed": seed})
            try:
                row = train_one(ctor, seed)
            except Exception as exc:
                row = {
                    "seed": seed,
                    "status": "failed",
                    "runtime_seconds": None,
                    "reason": str(exc)[:1000],
                }

            per_seed.append(row)
            log_event({"event": "seed_end", "model_id": model_id, "seed": seed, "status": row["status"], "runtime_seconds": row.get("runtime_seconds")})

            payload["models_live"][model_id] = {
                "model_id": model_id,
                "model_family": family,
                "framework": "PyTorch",
                "device": device,
                "per_seed": per_seed,
                "summary": summarize_seed_metrics(per_seed),
            }
            save_partial(payload)

        completed = [r for r in per_seed if r.get("status") == "completed"]

        result = {
            "model_id": model_id,
            "model_family": family,
            "framework": "PyTorch",
            "device": device,
            "status": "completed" if completed else "failed",
            "sequence_mode": "single_step_tabular_tensor",
            "notes": "Architecture benchmark over tabular features shaped as one-step tensors. Stronger temporal claims require a future true sequence construction phase.",
            "per_seed": per_seed,
            "summary": summarize_seed_metrics(per_seed),
        }

        all_results.append(result)
        log_event({"event": "model_end", "model_id": model_id, "status": result["status"]})

    return all_results


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# Overnight Core DL Benchmark",
        "",
        "## Status",
        "",
        f"- Status: `{payload.get('status')}`",
        f"- Generated: `{payload.get('generated_at_utc')}`",
        f"- Runtime seconds: `{payload.get('runtime_seconds')}`",
        "",
        "## Dataset",
        "",
        f"- Source dataset: `{payload.get('source_dataset')}`",
        f"- Target column: `{payload.get('target_column')}`",
        f"- Rows used: `{payload.get('dataset', {}).get('rows_after_class_filter')}`",
        f"- Feature count: `{payload.get('dataset', {}).get('feature_count')}`",
        "",
        "## Run configuration",
        "",
        f"- Seeds: `{payload.get('seeds')}`",
        f"- Max rows: `{MAX_ROWS}`",
        f"- Max features: `{MAX_FEATURES}`",
        f"- Epochs: `{EPOCHS}`",
        f"- Patience: `{PATIENCE}`",
        f"- Batch size: `{BATCH_SIZE}`",
        "",
        "## Models",
        "",
    ]

    for model in payload.get("models", []):
        lines.append(f"### {model.get('model_id')}")
        lines.append("")
        lines.append(f"- Family: `{model.get('model_family', '-')}`")
        lines.append(f"- Framework: `{model.get('framework', '-')}`")
        lines.append(f"- Status: `{model.get('status')}`")
        if model.get("device"):
            lines.append(f"- Device: `{model.get('device')}`")
        if model.get("sequence_mode"):
            lines.append(f"- Sequence mode: `{model.get('sequence_mode')}`")
        if model.get("notes"):
            lines.append(f"- Notes: {model.get('notes')}")
        if model.get("reason"):
            lines.append(f"- Reason: {model.get('reason')}")
        if model.get("summary"):
            lines.append("- Summary:")
            for metric, stats in model["summary"].items():
                if isinstance(stats, dict) and "mean" in stats:
                    lines.append(f"  - `{metric}`: mean `{stats['mean']}`, std `{stats['std']}`, min `{stats['min']}`, max `{stats['max']}`, n `{stats['n']}`")
                elif metric in {"completed_seeds", "failed_seeds"}:
                    lines.append(f"  - `{metric}`: `{stats}`")
        lines.append("")

    lines.extend([
        "## Boundaries",
        "",
        "- Public-source benchmark only.",
        "- No PHI.",
        "- Not clinical decision support.",
        "- No patient-level prediction claim.",
        "- Sequence-family models are architecture benchmarks until true temporal tensors are constructed.",
        "- Metrics are benchmark signals, not clinical-utility claims.",
        "",
        "## Outputs",
        "",
        "- `apps/web/src/data/deep_benchmark_overnight.json`",
        "- `.run/overnight_core_dl/overnight_core_dl_events.jsonl`",
        "- `.run/overnight_core_dl/overnight_core_dl_final.json`",
    ])

    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    started = time.time()
    log_event({"event": "overnight_run_start", "torch_ok": TORCH_OK, "max_rows": MAX_ROWS, "max_features": MAX_FEATURES, "epochs": EPOCHS, "patience": PATIENCE, "seeds": SEEDS})

    df, target, source_path, discovery = load_dataset()
    X, y, prep = prepare_matrix(df, target)

    payload: dict[str, Any] = {
        "benchmark_name": "Overnight core DL benchmark",
        "status": "running",
        "generated_at_utc": now_iso(),
        "source_dataset": rel(source_path),
        "target_column": target,
        "seeds": SEEDS,
        "dataset": prep,
        "discovery": discovery,
        "config": {
            "max_rows": MAX_ROWS,
            "max_features": MAX_FEATURES,
            "epochs": EPOCHS,
            "patience": PATIENCE,
            "batch_size": BATCH_SIZE,
        },
        "models_live": {},
        "models": [],
        "boundary": {
            "no_phi": True,
            "not_clinical_decision_support": True,
            "not_patient_level_prediction_claim": True,
            "notes": [
                "Benchmark signals only.",
                "Architecture-level comparison unless future phase builds true temporal tensors.",
            ],
        },
    }

    save_partial(payload)

    models = []
    models.append(run_sklearn_mlp(X, y, payload))
    models.extend(run_torch_suite(X, y, payload))

    payload["models"] = models
    payload["status"] = "completed"
    payload["runtime_seconds"] = round(time.time() - started, 3)
    payload["completed_at_utc"] = now_iso()

    FINAL_RUN_PATH.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8", newline="\n")
    FRONTEND_PATH.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8", newline="\n")
    write_report(payload)

    log_event({"event": "overnight_run_end", "status": "completed", "runtime_seconds": payload["runtime_seconds"], "models": [m.get("model_id") for m in models]})

    print("Overnight core DL benchmark complete.")
    print("Dataset:", rel(source_path))
    print("Target:", target)
    print("Rows:", prep["rows_after_class_filter"])
    print("Features:", prep["feature_count"])
    print("Models:", ", ".join(m.get("model_id", "?") for m in models))
    print("Wrote:", rel(FRONTEND_PATH))
    print("Wrote:", rel(DOC_PATH))
    print("Log:", rel(LOG_PATH))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log_event({"event": "overnight_run_failed", "error": str(exc)})
        raise