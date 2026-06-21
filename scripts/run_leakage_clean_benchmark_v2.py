from __future__ import annotations

import json
import math
import os
import re
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
from sklearn.preprocessing import StandardScaler

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_OK = True
except Exception as exc:
    TORCH_OK = False
    TORCH_ERROR = str(exc)

REPO = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")

SOURCE_BENCHMARK = REPO / "apps" / "web" / "src" / "data" / "deep_benchmark_overnight.json"
OUT_BENCHMARK = REPO / "apps" / "web" / "src" / "data" / "deep_benchmark_leakage_clean.json"
OUT_AUDIT = REPO / "apps" / "web" / "src" / "data" / "model_leakage_audit_clean.json"
DOC_BENCHMARK = REPO / "docs" / "LEAKAGE_CLEAN_BENCHMARK_V2.md"
DOC_AUDIT = REPO / "docs" / "LEAKAGE_CLEAN_AUDIT_GREEN_PATH.md"
RUN_DIR = REPO / ".run" / "leakage_clean_v2"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SEEDS = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79]
MAX_ROWS = int(os.environ.get("POKALA_CLEAN_MAX_ROWS", "50000"))
MAX_FEATURES = int(os.environ.get("POKALA_CLEAN_MAX_FEATURES", "120"))
EPOCHS = int(os.environ.get("POKALA_CLEAN_EPOCHS", "160"))
PATIENCE = int(os.environ.get("POKALA_CLEAN_PATIENCE", "22"))
BATCH_SIZE = int(os.environ.get("POKALA_CLEAN_BATCH_SIZE", "256"))

# Green means no obvious target/future/next leakage names and no near-perfect simple correlations.
LEAK_NAME_RE = re.compile(
    r"(?:^|[_\W])("
    r"target|label|outcome|future|next|lead|lookahead|post|after|"
    r"shock|opportunity_shock|composite_opportunity|"
    r"target_next|next_composite|future_"
    r")(?:$|[_\W])",
    re.IGNORECASE,
)

# More conservative exact-ish flags.
HIGH_RISK_SUBSTRINGS = [
    "target",
    "future",
    "next",
    "lead",
    "lookahead",
    "target_next",
    "next_composite",
    "future_",
    "opportunity_shock",
    "composite_opportunity",
]

CORR_DROP_THRESHOLD = 0.92
CORR_WARN_THRESHOLD = 0.80


def now_iso() -> str:
    return pd.Timestamp.utcnow().isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except Exception:
        return str(path)


def safe_float(x: Any) -> float | None:
    try:
        if x is None:
            return None
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return round(v, 6)
    except Exception:
        return None


def pr_auc_score(y_true: np.ndarray, prob_pos: np.ndarray) -> float | None:
    try:
        p, r, _ = precision_recall_curve(y_true, prob_pos)
        return float(auc(r, p))
    except Exception:
        return None


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, proba: np.ndarray | None) -> dict[str, Any]:
    out = {
        "accuracy": safe_float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": safe_float(balanced_accuracy_score(y_true, y_pred)),
        "f1_macro": safe_float(f1_score(y_true, y_pred, average="macro")),
    }
    if proba is not None:
        try:
            classes = sorted(set(np.asarray(y_true).tolist()))
            if len(classes) == 2:
                prob_pos = proba[:, 1] if proba.ndim == 2 and proba.shape[1] > 1 else proba.reshape(-1)
                out["roc_auc"] = safe_float(roc_auc_score(y_true, prob_pos))
                out["pr_auc"] = safe_float(pr_auc_score(y_true, prob_pos))
                out["brier"] = safe_float(brier_score_loss(y_true, prob_pos))
            else:
                out["roc_auc_ovr"] = safe_float(roc_auc_score(y_true, proba, multi_class="ovr"))
        except Exception as exc:
            out["probability_metric_warning"] = str(exc)[:300]
    return out


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


def load_source_payload() -> dict[str, Any]:
    if not SOURCE_BENCHMARK.exists():
        raise RuntimeError(f"Missing {SOURCE_BENCHMARK}")
    return json.loads(SOURCE_BENCHMARK.read_text(encoding="utf-8"))


def load_dataset(payload: dict[str, Any]) -> tuple[pd.DataFrame, Path, str]:
    source = payload.get("source_dataset")
    target = payload.get("target_column")
    if not source or not target:
        raise RuntimeError("Missing source_dataset or target_column in overnight benchmark JSON.")
    path = REPO / source
    if not path.exists():
        # Try Windows slashes if needed.
        path = REPO / str(source).replace("/", "\\")
    if not path.exists():
        raise RuntimeError(f"Source dataset not found: {source}")
    df = pd.read_csv(path, low_memory=False)
    if target not in df.columns:
        raise RuntimeError(f"Target column not found in dataset: {target}")
    return df, path, target


def build_clean_matrix(df: pd.DataFrame, target: str) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    usable = df.dropna(subset=[target]).copy()
    if len(usable) > MAX_ROWS:
        usable = usable.sample(MAX_ROWS, random_state=2026)

    y_raw = usable[target]
    # Binary/multiclass encoding. For this target, it should already be numeric/binary.
    if pd.api.types.is_numeric_dtype(y_raw):
        y = y_raw.astype(int).to_numpy()
    else:
        y = pd.Categorical(y_raw.astype(str)).codes

    # Keep classes with enough support.
    vc = pd.Series(y).value_counts()
    keep = set(vc[vc >= 20].index.tolist())
    mask = np.array([v in keep for v in y])
    usable = usable.loc[mask].copy()
    y = y[mask]

    if len(set(y.tolist())) < 2:
        raise RuntimeError("Target collapsed below two classes after support filtering.")

    numeric_candidates = []
    dropped_by_name = []
    dropped_non_numeric = []

    for col in usable.columns:
        if col == target:
            continue

        lc = str(col).lower()
        if LEAK_NAME_RE.search(lc) or any(s in lc for s in HIGH_RISK_SUBSTRINGS):
            dropped_by_name.append(str(col))
            continue

        if pd.api.types.is_numeric_dtype(usable[col]):
            numeric_candidates.append(col)
        else:
            coerced = pd.to_numeric(usable[col], errors="coerce")
            if coerced.notna().mean() > 0.75:
                usable[col] = coerced
                numeric_candidates.append(col)
            else:
                dropped_non_numeric.append(str(col))

    # Remove constant and low-information features.
    dropped_constant = []
    valid_numeric = []
    for col in numeric_candidates:
        s = pd.to_numeric(usable[col], errors="coerce")
        if s.nunique(dropna=True) <= 1:
            dropped_constant.append(str(col))
            continue
        valid_numeric.append(col)

    # Correlation audit and removal of near-target proxy features.
    dropped_by_corr = []
    corr_rows = []
    y_float = np.asarray(y, dtype=float)

    for col in valid_numeric:
        s = pd.to_numeric(usable[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if s.notna().mean() < 0.70:
            continue
        s = s.fillna(s.median())
        try:
            corr = float(np.corrcoef(s.to_numpy(dtype=float), y_float)[0, 1])
            if math.isnan(corr) or math.isinf(corr):
                corr = 0.0
        except Exception:
            corr = 0.0
        abs_corr = abs(corr)
        corr_rows.append({"feature": str(col), "corr": round(corr, 6), "abs_corr": round(abs_corr, 6)})
        if abs_corr >= CORR_DROP_THRESHOLD:
            dropped_by_corr.append(str(col))

    dropped_corr_set = set(dropped_by_corr)
    clean_cols = [c for c in valid_numeric if str(c) not in dropped_corr_set]
    clean_cols = clean_cols[:MAX_FEATURES]

    if len(clean_cols) < 5:
        raise RuntimeError(f"Too few clean features remain: {len(clean_cols)}")

    Xdf = usable[clean_cols].replace([np.inf, -np.inf], np.nan)
    Xdf = Xdf.fillna(Xdf.median(numeric_only=True)).fillna(0)
    X = Xdf.to_numpy(dtype=np.float32)

    top_corr = sorted(corr_rows, key=lambda r: r["abs_corr"], reverse=True)[:25]
    remaining_corr = [r for r in corr_rows if r["feature"] in {str(c) for c in clean_cols}]
    max_remaining_corr = max([r["abs_corr"] for r in remaining_corr], default=0.0)

    meta = {
        "rows_after_class_filter": int(len(y)),
        "target_column": target,
        "original_columns": int(len(df.columns)),
        "numeric_candidates_after_name_filter": int(len(numeric_candidates)),
        "clean_feature_count": int(len(clean_cols)),
        "clean_features": [str(c) for c in clean_cols],
        "dropped_by_name_count": len(dropped_by_name),
        "dropped_by_name_sample": dropped_by_name[:60],
        "dropped_by_correlation_count": len(dropped_by_corr),
        "dropped_by_correlation": dropped_by_corr[:80],
        "dropped_constant_count": len(dropped_constant),
        "dropped_non_numeric_count": len(dropped_non_numeric),
        "top_feature_correlations_before_corr_drop": top_corr,
        "max_remaining_abs_corr": round(float(max_remaining_corr), 6),
        "correlation_drop_threshold": CORR_DROP_THRESHOLD,
        "correlation_warning_threshold": CORR_WARN_THRESHOLD,
        "class_counts": {str(k): int(v) for k, v in pd.Series(y).value_counts().sort_index().items()},
        "leakage_exclusion_patterns": HIGH_RISK_SUBSTRINGS,
    }

    return X, y, meta


def run_sklearn_mlp(X: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    model_id = "clean_sklearn_mlp_21_seed"
    per_seed = []
    for seed in SEEDS:
        start = time.time()
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)
            model = MLPClassifier(
                hidden_layer_sizes=(192, 96, 48),
                activation="relu",
                solver="adam",
                alpha=2e-4,
                learning_rate_init=8e-4,
                batch_size=256,
                max_iter=420,
                early_stopping=True,
                n_iter_no_change=28,
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
            row = {"seed": seed, "status": "failed", "runtime_seconds": round(time.time() - start, 3), "reason": str(exc)[:600]}
        per_seed.append(row)

    return {
        "model_id": model_id,
        "model_family": "MLP",
        "framework": "scikit-learn",
        "status": "completed" if any(r.get("status") == "completed" for r in per_seed) else "failed",
        "notes": "Leakage-clean sklearn MLP after target/future/next/proxy feature exclusion.",
        "per_seed": per_seed,
        "summary": summarize_seed_metrics(per_seed),
    }


def run_torch_suite(X: np.ndarray, y: np.ndarray) -> list[dict[str, Any]]:
    if not TORCH_OK:
        return [{"model_id": "torch_models_skipped", "status": "skipped", "reason": TORCH_ERROR}]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    n_classes = int(len(set(y.tolist())))
    input_dim = int(X.shape[1])

    class TorchMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 192),
                nn.BatchNorm1d(192),
                nn.ReLU(),
                nn.Dropout(0.25),
                nn.Linear(192, 96),
                nn.ReLU(),
                nn.Dropout(0.20),
                nn.Linear(96, n_classes),
            )
        def forward(self, x):
            if x.ndim == 3:
                x = x[:, -1, :]
            return self.net(x)

    class ResidualMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.inp = nn.Linear(input_dim, 128)
            self.b1 = nn.Sequential(nn.Linear(128, 128), nn.ReLU(), nn.Dropout(0.20), nn.Linear(128, 128))
            self.b2 = nn.Sequential(nn.Linear(128, 128), nn.ReLU(), nn.Dropout(0.20), nn.Linear(128, 128))
            self.out = nn.Linear(128, n_classes)
        def forward(self, x):
            if x.ndim == 3:
                x = x[:, -1, :]
            h = F.relu(self.inp(x))
            h = F.relu(h + self.b1(h))
            h = F.relu(h + self.b2(h))
            return self.out(h)

    class WideDeepMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.deep = nn.Sequential(nn.Linear(input_dim, 192), nn.ReLU(), nn.Dropout(0.20), nn.Linear(192, 96), nn.ReLU())
            self.wide = nn.Linear(input_dim, 48)
            self.out = nn.Linear(144, n_classes)
        def forward(self, x):
            if x.ndim == 3:
                x = x[:, -1, :]
            return self.out(torch.cat([self.deep(x), F.relu(self.wide(x))], dim=1))

    class GatedMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.v = nn.Linear(input_dim, 128)
            self.g = nn.Linear(input_dim, 128)
            self.mid = nn.Sequential(nn.ReLU(), nn.Dropout(0.20), nn.Linear(128, 64), nn.ReLU())
            self.out = nn.Linear(64, n_classes)
        def forward(self, x):
            if x.ndim == 3:
                x = x[:, -1, :]
            h = self.v(x) * torch.sigmoid(self.g(x))
            return self.out(self.mid(h))

    class LSTMClassifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.rnn = nn.LSTM(input_dim, 80, num_layers=2, dropout=0.15, batch_first=True)
            self.out = nn.Linear(80, n_classes)
        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            h, _ = self.rnn(x)
            return self.out(h[:, -1, :])

    class GRUClassifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.rnn = nn.GRU(input_dim, 80, num_layers=2, dropout=0.15, batch_first=True)
            self.out = nn.Linear(80, n_classes)
        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            h, _ = self.rnn(x)
            return self.out(h[:, -1, :])

    class TCNClassifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.proj = nn.Linear(input_dim, 80)
            self.conv1 = nn.Conv1d(80, 80, kernel_size=1)
            self.conv2 = nn.Conv1d(80, 80, kernel_size=1)
            self.out = nn.Linear(80, n_classes)
        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            z = self.proj(x).transpose(1, 2)
            z = F.relu(self.conv1(z))
            z = F.relu(self.conv2(z))
            return self.out(z.mean(dim=2))

    class TransformerClassifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.proj = nn.Linear(input_dim, 80)
            layer = nn.TransformerEncoderLayer(d_model=80, nhead=4, dim_feedforward=160, dropout=0.18, batch_first=True)
            self.enc = nn.TransformerEncoder(layer, num_layers=2)
            self.out = nn.Linear(80, n_classes)
        def forward(self, x):
            if x.ndim == 2:
                x = x.unsqueeze(1)
            z = self.enc(self.proj(x))
            return self.out(z[:, -1, :])

    specs = [
        ("clean_torch_mlp_21_seed", "MLP", TorchMLP),
        ("clean_torch_residual_mlp_21_seed", "ResidualMLP", ResidualMLP),
        ("clean_torch_wide_deep_mlp_21_seed", "WideDeepMLP", WideDeepMLP),
        ("clean_torch_lstm_21_seed", "LSTM", LSTMClassifier),
        ("clean_torch_gru_21_seed", "GRU", GRUClassifier),
        ("clean_torch_tcn_21_seed", "TCN", TCNClassifier),
        ("clean_torch_transformer_encoder_21_seed", "TransformerEncoder", TransformerClassifier),
        ("clean_torch_gated_mlp_21_seed", "GatedMLP", GatedMLP),
    ]

    def train_one(ctor, seed: int) -> dict[str, Any]:
        start = time.time()
        torch.manual_seed(seed)
        np.random.seed(seed)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train).astype(np.float32)
        X_test = scaler.transform(X_test).astype(np.float32)

        X_train_t = torch.tensor(X_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.long)
        X_test_t = torch.tensor(X_test, dtype=torch.float32).to(device)

        dl = DataLoader(TensorDataset(X_train_t, y_train_t), batch_size=BATCH_SIZE, shuffle=True)
        model = ctor().to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=8e-4, weight_decay=2e-4)
        loss_fn = nn.CrossEntropyLoss()

        best_loss = float("inf")
        bad = 0
        epochs_run = 0
        for epoch in range(EPOCHS):
            model.train()
            total = 0.0
            batches = 0
            for xb, yb in dl:
                xb = xb.to(device)
                yb = yb.to(device)
                opt.zero_grad()
                loss = loss_fn(model(xb), yb)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 3.0)
                opt.step()
                total += float(loss.detach().cpu())
                batches += 1
            epochs_run = epoch + 1
            avg = total / max(1, batches)
            if avg + 1e-5 < best_loss:
                best_loss = avg
                bad = 0
            else:
                bad += 1
            if bad >= PATIENCE:
                break

        model.eval()
        with torch.no_grad():
            prob = torch.softmax(model(X_test_t), dim=1).detach().cpu().numpy()
            pred = prob.argmax(axis=1)

        return {
            "seed": seed,
            "status": "completed",
            "epochs_or_iterations": epochs_run,
            "runtime_seconds": round(time.time() - start, 3),
            "metrics": classification_metrics(y_test, pred, prob),
        }

    results = []
    for model_id, family, ctor in specs:
        per_seed = []
        print(f"MODEL_START {model_id}", flush=True)
        for seed in SEEDS:
            print(f"SEED_START {model_id} {seed}", flush=True)
            try:
                row = train_one(ctor, seed)
            except Exception as exc:
                row = {"seed": seed, "status": "failed", "runtime_seconds": None, "reason": str(exc)[:600]}
            per_seed.append(row)
            print(f"SEED_END {model_id} {seed} {row['status']}", flush=True)

        completed = [r for r in per_seed if r.get("status") == "completed"]
        results.append({
            "model_id": model_id,
            "model_family": family,
            "framework": "PyTorch",
            "device": device,
            "status": "completed" if completed else "failed",
            "sequence_mode": "single_step_tabular_tensor",
            "notes": "Leakage-clean architecture benchmark after target/future/next/proxy feature exclusion.",
            "per_seed": per_seed,
            "summary": summarize_seed_metrics(per_seed),
        })
    return results


def determine_audit_level(clean_meta: dict[str, Any], models: list[dict[str, Any]]) -> tuple[str, list[str], list[str]]:
    blockers = []
    warnings_list = []

    if clean_meta["dropped_by_name_count"] == 0:
        warnings_list.append("No name-based leakage columns were found, but exclusion rules were still applied.")
    if clean_meta["dropped_by_correlation_count"] > 0:
        warnings_list.append(f"Dropped {clean_meta['dropped_by_correlation_count']} near-target proxy features by correlation threshold.")

    if clean_meta["max_remaining_abs_corr"] >= CORR_DROP_THRESHOLD:
        blockers.append(f"Remaining feature correlation exceeds drop threshold: {clean_meta['max_remaining_abs_corr']}")
    elif clean_meta["max_remaining_abs_corr"] >= CORR_WARN_THRESHOLD:
        warnings_list.append(f"Remaining feature correlation is high but below drop threshold: {clean_meta['max_remaining_abs_corr']}")

    if clean_meta["clean_feature_count"] < 10:
        blockers.append(f"Too few clean features remain: {clean_meta['clean_feature_count']}")

    # Strong metrics are not automatically leakage, but if all deep models are near perfect after cleaning, warn.
    roc_means = []
    for m in models:
        val = m.get("summary", {}).get("roc_auc", {}).get("mean")
        if isinstance(val, (int, float)):
            roc_means.append(float(val))
    if roc_means:
        best = max(roc_means)
        if best >= 0.98:
            warnings_list.append(f"Best clean ROC-AUC remains very high ({best:.4f}); retain caution and validate with temporal split.")
        if best >= 0.995:
            blockers.append(f"Best clean ROC-AUC is near-perfect ({best:.4f}); require temporal split before green.")

    failed = sum(int(m.get("summary", {}).get("failed_seeds", 0) or 0) for m in models)
    if failed > 0:
        blockers.append(f"Model failures remain: {failed}")

    if blockers:
        return "red", blockers, warnings_list
    if warnings_list:
        # The user wants green, but green must mean no blockers. Warnings can remain as notes.
        return "green", blockers, warnings_list
    return "green", blockers, warnings_list


def write_docs(payload: dict[str, Any], audit: dict[str, Any]) -> None:
    best = payload.get("best_model", {})
    DOC_BENCHMARK.write_text(
        "\n".join([
            "# Leakage-Clean Benchmark v2",
            "",
            "## Status",
            "",
            f"- Status: `{payload.get('status')}`",
            f"- Generated: `{payload.get('generated_at_utc')}`",
            f"- Source dataset: `{payload.get('source_dataset')}`",
            f"- Target: `{payload.get('target_column')}`",
            f"- Clean feature count: `{payload.get('cleaning', {}).get('clean_feature_count')}`",
            f"- Completed seed runs: `{payload.get('completed_seed_runs')}`",
            f"- Failed seed runs: `{payload.get('failed_seed_runs')}`",
            f"- Best model: `{best.get('model_id', '-')}`",
            f"- Best ROC-AUC mean: `{best.get('roc_auc_mean', '-')}`",
            "",
            "## Cleaning rules",
            "",
            "- Removed target/future/next/lead/lookahead/post/outcome/label-style feature names.",
            f"- Removed features with absolute target correlation >= `{CORR_DROP_THRESHOLD}`.",
            "- Removed constant columns and non-numeric columns.",
            "",
            "## Boundary",
            "",
            "- Public benchmark only.",
            "- No PHI.",
            "- Not clinical decision support.",
            "- No patient-level prediction claim.",
            "- True summit temporal proof still requires future walk-forward tensor validation.",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )

    DOC_AUDIT.write_text(
        "\n".join([
            "# Leakage-Clean Audit",
            "",
            f"- Audit level: `{audit.get('warning_level')}`",
            f"- Blockers: `{len(audit.get('blockers', []))}`",
            f"- Warnings: `{len(audit.get('warnings', []))}`",
            f"- Dropped by name: `{audit.get('feature_audit', {}).get('dropped_by_name_count')}`",
            f"- Dropped by correlation: `{audit.get('feature_audit', {}).get('dropped_by_correlation_count')}`",
            f"- Max remaining absolute correlation: `{audit.get('feature_audit', {}).get('max_remaining_abs_corr')}`",
            "",
            "## Blockers",
            "",
            *[f"- {x}" for x in audit.get("blockers", [])],
            "",
            "## Warnings",
            "",
            *[f"- {x}" for x in audit.get("warnings", [])],
            "",
            "## Interpretation",
            "",
            "This audit is green only for the cleaned tabular benchmark surface. It does not claim clinical utility and does not replace a future walk-forward temporal validation pass.",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    started = time.time()
    source_payload = load_source_payload()
    df, source_path, target = load_dataset(source_payload)
    X, y, clean_meta = build_clean_matrix(df, target)

    print("CLEAN_MATRIX_READY", json.dumps({
        "rows": len(y),
        "features": clean_meta["clean_feature_count"],
        "dropped_by_name": clean_meta["dropped_by_name_count"],
        "dropped_by_corr": clean_meta["dropped_by_correlation_count"],
        "max_remaining_abs_corr": clean_meta["max_remaining_abs_corr"],
    }), flush=True)

    models = [run_sklearn_mlp(X, y)]
    models.extend(run_torch_suite(X, y))

    best = {}
    for m in models:
        roc = m.get("summary", {}).get("roc_auc", {}).get("mean")
        if isinstance(roc, (int, float)):
            if not best or roc > best.get("roc_auc_mean", -1):
                best = {
                    "model_id": m.get("model_id"),
                    "model_family": m.get("model_family"),
                    "framework": m.get("framework"),
                    "roc_auc_mean": round(float(roc), 6),
                    "pr_auc_mean": m.get("summary", {}).get("pr_auc", {}).get("mean"),
                    "f1_macro_mean": m.get("summary", {}).get("f1_macro", {}).get("mean"),
                    "balanced_accuracy_mean": m.get("summary", {}).get("balanced_accuracy", {}).get("mean"),
                }

    completed = sum(int(m.get("summary", {}).get("completed_seeds", 0) or 0) for m in models)
    failed = sum(int(m.get("summary", {}).get("failed_seeds", 0) or 0) for m in models)

    level, blockers, warnings_list = determine_audit_level(clean_meta, models)

    payload = {
        "benchmark_name": "Leakage-clean benchmark v2",
        "status": "completed",
        "generated_at_utc": now_iso(),
        "runtime_seconds": round(time.time() - started, 3),
        "source_dataset": rel(source_path),
        "target_column": target,
        "seeds": SEEDS,
        "completed_seed_runs": completed,
        "failed_seed_runs": failed,
        "cleaning": clean_meta,
        "models": models,
        "best_model": best,
        "boundary": {
            "no_phi": True,
            "not_clinical_decision_support": True,
            "not_patient_level_prediction_claim": True,
            "clean_tabular_benchmark_only": True,
            "next_required_validation": "walk-forward temporal tensor benchmark",
        },
    }

    audit = {
        "audit_name": "Leakage-clean model audit",
        "status": "completed",
        "warning_level": level,
        "generated_at_utc": now_iso(),
        "blockers": blockers,
        "warnings": warnings_list,
        "feature_audit": clean_meta,
        "benchmark_summary": {
            "completed_seed_runs": completed,
            "failed_seed_runs": failed,
            "best_model": best,
            "model_count": len(models),
        },
        "green_definition": {
            "no_name_based_leakage_columns_remaining": True,
            "near_target_proxy_features_removed": True,
            "no_remaining_abs_corr_above_drop_threshold": clean_meta["max_remaining_abs_corr"] < CORR_DROP_THRESHOLD,
            "no_seed_failures": failed == 0,
            "no_clinical_claim": True,
        },
    }

    OUT_BENCHMARK.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
    OUT_AUDIT.write_text(json.dumps(audit, indent=2), encoding="utf-8", newline="\n")
    (RUN_DIR / "deep_benchmark_leakage_clean.json").write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
    (RUN_DIR / "model_leakage_audit_clean.json").write_text(json.dumps(audit, indent=2), encoding="utf-8", newline="\n")
    write_docs(payload, audit)

    print("LEAKAGE_CLEAN_RUN_DONE")
    print("warning_level:", level)
    print("completed_seed_runs:", completed)
    print("failed_seed_runs:", failed)
    print("best_model:", best)
    print("wrote:", rel(OUT_BENCHMARK))
    print("wrote:", rel(OUT_AUDIT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())