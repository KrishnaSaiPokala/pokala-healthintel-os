from __future__ import annotations

import ctypes
import json
import math
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "data" / "features" / "enterprise_temporal_sequences.csv"
CMS_MART = ROOT / "data" / "processed" / "public_api_marts" / "cms_physician_supplier_utilization_mart.csv"
SOURCE_MANIFEST = ROOT / "data" / "source_manifest.real_api_v1.json"

RUN_ID = datetime.now(timezone.utc).strftime("basecamp4_shock_%Y%m%d_%H%M%S")
OUT_ROOT = ROOT / "data" / "models" / "run_history_v4"
RUN_DIR = OUT_ROOT / RUN_ID
RUN_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_OUT = ROOT / "data" / "models" / "enterprise_model_card_v4.json"
HISTORY_OUT = ROOT / "data" / "models" / "enterprise_run_history_v4.json"
METRICS_JSONL = RUN_DIR / "metrics.jsonl"

WINDOW = 24
HORIZON = 3
EPOCHS = 720
BATCH_SIZE = 64
SEEDS = [7, 17, 29, 42, 71, 101, 131]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

TARGET = "target_v4_opportunity_shock"

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def keep_windows_awake() -> None:
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
        print("Sleep prevention: active for this training process.")
    except Exception as exc:
        print(f"Sleep prevention unavailable: {exc}")

def release_windows_awake() -> None:
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    except Exception:
        pass

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def read_metrics() -> list[dict]:
    if not METRICS_JSONL.exists():
        return []
    rows = []
    for line in METRICS_JSONL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows

def completed_keys() -> set[tuple[str, int | str]]:
    keys = set()
    for row in read_metrics():
        keys.add((str(row.get("model")), row.get("seed", "none")))
    return keys

def cms_pressure_features() -> dict:
    if not CMS_MART.exists():
        return {
            "cms_rows": 0,
            "cms_payment_pressure": 0.0,
            "cms_utilization_pressure": 0.0,
            "cms_numeric_signal": 0.0,
            "cms_tail_pressure": 0.0,
        }

    cms = pd.read_csv(CMS_MART)
    vals = pd.to_numeric(cms.get("numeric_value", pd.Series(dtype=float)), errors="coerce").dropna()
    vals = vals[(vals.abs() > 0) & ~(vals.between(1900, 2100))]
    if vals.empty:
        return {
            "cms_rows": int(len(cms)),
            "cms_payment_pressure": 0.0,
            "cms_utilization_pressure": 0.0,
            "cms_numeric_signal": 0.0,
            "cms_tail_pressure": 0.0,
        }

    q75 = vals.quantile(0.75)
    q90 = vals.quantile(0.90)
    tail = vals[vals >= q90]
    return {
        "cms_rows": int(len(cms)),
        "cms_payment_pressure": float(np.log1p(vals[vals >= q75].abs().mean())),
        "cms_utilization_pressure": float(np.log1p(vals.abs().median())),
        "cms_numeric_signal": float(np.log1p(vals.abs().quantile(0.90))),
        "cms_tail_pressure": float(np.log1p(tail.abs().mean())) if not tail.empty else 0.0,
    }

def safe_rate(numer: pd.Series, denom: pd.Series) -> pd.Series:
    denom = denom.replace(0, np.nan)
    return (numer / denom).replace([np.inf, -np.inf], np.nan).fillna(0.0)

def build_v4_frame() -> tuple[pd.DataFrame, list[str], dict]:
    if not FEATURES.exists():
        raise SystemExit(f"Missing base feature matrix: {FEATURES}")

    df = pd.read_csv(FEATURES)
    df["period_dt"] = pd.to_datetime(df["period"], errors="coerce")
    df = df.dropna(subset=["period_dt"]).copy()
    df = df.sort_values(["entity_id", "period_dt"]).reset_index(drop=True)

    cms = cms_pressure_features()
    for key, value in cms.items():
        df[key] = value

    df["period_index"] = df.groupby("entity_id").cumcount()
    df["month"] = df["period_dt"].dt.month
    df["year"] = df["period_dt"].dt.year
    df["sin_month"] = np.sin(2 * np.pi * df["month"] / 12.0)
    df["cos_month"] = np.cos(2 * np.pi * df["month"] / 12.0)

    df["market_x_cms_payment"] = df["market_signal"] * df["cms_payment_pressure"]
    df["provider_x_cms_utilization"] = df["provider_share"] * df["cms_utilization_pressure"]
    df["safety_x_cms_tail"] = df["safety_signal"] * df["cms_tail_pressure"]
    df["reimbursement_x_market"] = df["reimbursement_proxy_norm"] * df["market_signal"]
    df["market_minus_safety"] = df["market_signal"] - df["safety_signal"]
    df["opportunity_pressure_ratio"] = safe_rate(df["market_signal"] + df["reimbursement_proxy_norm"], 1.0 + df["safety_signal"])

    base_cols = [
        "composite_opportunity",
        "market_signal",
        "safety_signal",
        "provider_share",
        "provider_density_norm",
        "trial_starts_month",
        "trial_starts_3mo",
        "trial_starts_6mo",
        "trial_velocity",
        "device_events_month",
        "device_events_3mo",
        "device_events_6mo",
        "safety_velocity",
        "reimbursement_proxy_norm",
        "market_x_cms_payment",
        "provider_x_cms_utilization",
        "safety_x_cms_tail",
        "reimbursement_x_market",
        "market_minus_safety",
        "opportunity_pressure_ratio",
    ]

    for col in base_cols:
        if col not in df.columns:
            continue
        g = df.groupby("entity_id")[col]
        df[f"{col}_lag1"] = g.shift(1)
        df[f"{col}_lag3"] = g.shift(3)
        df[f"{col}_lag6"] = g.shift(6)
        df[f"{col}_roll3_mean"] = g.transform(lambda x: x.rolling(3, min_periods=1).mean())
        df[f"{col}_roll6_mean"] = g.transform(lambda x: x.rolling(6, min_periods=1).mean())
        df[f"{col}_roll12_mean"] = g.transform(lambda x: x.rolling(12, min_periods=1).mean())
        df[f"{col}_roll6_std"] = g.transform(lambda x: x.rolling(6, min_periods=2).std())
        df[f"{col}_velocity1"] = g.diff(1)
        df[f"{col}_velocity3"] = g.diff(3)

    df["future_composite_h3"] = df.groupby("entity_id")["composite_opportunity"].shift(-HORIZON)
    df["future_market_h3"] = df.groupby("entity_id")["market_signal"].shift(-HORIZON)
    df["future_safety_h3"] = df.groupby("entity_id")["safety_signal"].shift(-HORIZON)
    df["future_reimbursement_h3"] = df.groupby("entity_id")["reimbursement_proxy_norm"].shift(-HORIZON)
    df["future_device_h3"] = df.groupby("entity_id")["device_events_6mo"].shift(-HORIZON)
    df["future_trial_h3"] = df.groupby("entity_id")["trial_starts_6mo"].shift(-HORIZON)

    df["delta_composite_h3"] = df["future_composite_h3"] - df["composite_opportunity"]
    df["delta_market_h3"] = df["future_market_h3"] - df["market_signal"]
    df["delta_safety_h3"] = df["future_safety_h3"] - df["safety_signal"]
    df["delta_reimbursement_h3"] = df["future_reimbursement_h3"] - df["reimbursement_proxy_norm"]
    df["delta_device_h3"] = df["future_device_h3"] - df["device_events_6mo"]
    df["delta_trial_h3"] = df["future_trial_h3"] - df["trial_starts_6mo"]

    df["shock_score_raw"] = (
        1.00 * df["delta_composite_h3"]
        + 0.45 * df["delta_market_h3"]
        + 0.40 * df["delta_reimbursement_h3"]
        + 0.35 * df["delta_trial_h3"]
        - 0.35 * df["delta_safety_h3"].clip(lower=0)
        - 0.20 * df["delta_device_h3"].clip(lower=0)
    )

    valid = df["shock_score_raw"].dropna()
    if valid.empty:
        raise SystemExit("No valid v4 shock targets produced.")

    threshold = float(valid.quantile(0.75))
    df[TARGET] = (df["shock_score_raw"] >= threshold).astype(float)
    df.loc[df["shock_score_raw"].isna(), TARGET] = np.nan

    df = df.fillna(0.0)

    excluded = {
        "entity_id",
        "region",
        "specialty",
        "city",
        "period",
        "period_dt",
        "target_next_composite_opportunity",
        TARGET,
        "shock_score_raw",
        "future_composite_h3",
        "future_market_h3",
        "future_safety_h3",
        "future_reimbursement_h3",
        "future_device_h3",
        "future_trial_h3",
        "delta_composite_h3",
        "delta_market_h3",
        "delta_safety_h3",
        "delta_reimbursement_h3",
        "delta_device_h3",
        "delta_trial_h3",
    }

    feature_cols = [
        c for c in df.columns
        if c not in excluded and pd.api.types.is_numeric_dtype(df[c])
    ]

    positive_rate = float(df[TARGET].mean())
    manifest = {
        "generated_at": now(),
        "status": "enterprise_temporal_matrix_v4_shock_runtime",
        "boundary": "Harder v4 target: future 3-period opportunity shock/regime-change classification. Uses bounded public-source features and CMS aggregate pressure. Not paper-scale or clinical validation.",
        "base_feature_matrix": str(FEATURES.relative_to(ROOT)),
        "cms_mart": str(CMS_MART.relative_to(ROOT)) if CMS_MART.exists() else None,
        "rows": int(len(df)),
        "entities": int(df["entity_id"].nunique()),
        "periods": int(df["period"].nunique()),
        "feature_count": int(len(feature_cols)),
        "feature_columns": feature_cols,
        "target": TARGET,
        "target_definition": "Top-quartile future 3-period opportunity shock after penalizing safety/device-event acceleration.",
        "target_threshold": threshold,
        "target_positive_rate": positive_rate,
        "horizon_periods": HORIZON,
        "cms_features": cms,
    }

    df.to_csv(RUN_DIR / "enterprise_temporal_sequences_v4_shock.csv", index=False)
    (RUN_DIR / "enterprise_temporal_manifest_v4_shock.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return df, feature_cols, manifest

def build_windows(df: pd.DataFrame, feature_cols: list[str]) -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    xs, ys, periods, entities = [], [], [], []
    for entity_id, group in df.groupby("entity_id"):
        group = group.sort_values("period_dt").reset_index(drop=True)
        values = group[feature_cols].to_numpy(dtype=np.float32)
        target = group[TARGET].to_numpy(dtype=np.float32)
        period_values = group["period"].astype(str).tolist()
        for idx in range(WINDOW - 1, len(group) - HORIZON):
            if not np.isfinite(target[idx]):
                continue
            xs.append(values[idx - WINDOW + 1: idx + 1])
            ys.append(target[idx])
            periods.append(period_values[idx])
            entities.append(str(entity_id))
    return (
        np.asarray(xs, dtype=np.float32),
        np.asarray(ys, dtype=np.float32),
        periods,
        entities,
    )

def safe_classification_metrics(y_true: np.ndarray, prob: np.ndarray) -> dict:
    y_true = np.asarray(y_true).astype(int)
    prob = np.asarray(prob).astype(float)
    pred = (prob >= 0.5).astype(int)

    out = {
        "accuracy": round(float(accuracy_score(y_true, pred)), 8),
        "balanced_accuracy": round(float(balanced_accuracy_score(y_true, pred)), 8),
        "f1": round(float(f1_score(y_true, pred, zero_division=0)), 8),
        "precision": round(float(precision_score(y_true, pred, zero_division=0)), 8),
        "recall": round(float(recall_score(y_true, pred, zero_division=0)), 8),
        "positive_rate_pred": round(float(pred.mean()), 8),
        "positive_rate_true": round(float(y_true.mean()), 8),
    }

    try:
        out["roc_auc"] = round(float(roc_auc_score(y_true, prob)), 8)
    except Exception:
        out["roc_auc"] = None

    try:
        out["pr_auc"] = round(float(average_precision_score(y_true, prob)), 8)
    except Exception:
        out["pr_auc"] = None

    return out

class GRUClassifier(nn.Module):
    def __init__(self, feature_dim: int, hidden_dim: int = 128, layers: int = 2):
        super().__init__()
        self.gru = nn.GRU(feature_dim, hidden_dim, num_layers=layers, dropout=0.12, batch_first=True)
        self.head = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, 96),
            nn.GELU(),
            nn.Dropout(0.10),
            nn.Linear(96, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.gru(x)
        return self.head(out[:, -1, :]).squeeze(-1)

class TCNClassifier(nn.Module):
    def __init__(self, feature_dim: int, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(feature_dim, hidden, kernel_size=3, padding=2, dilation=1),
            nn.GELU(),
            nn.Dropout(0.08),
            nn.Conv1d(hidden, hidden, kernel_size=3, padding=4, dilation=2),
            nn.GELU(),
            nn.Dropout(0.08),
            nn.Conv1d(hidden, hidden, kernel_size=3, padding=8, dilation=4),
            nn.GELU(),
        )
        self.head = nn.Sequential(
            nn.LayerNorm(hidden),
            nn.Linear(hidden, 96),
            nn.GELU(),
            nn.Dropout(0.08),
            nn.Linear(96, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = x.transpose(1, 2)
        z = self.net(z)
        z = z[:, :, -x.shape[1]:]
        z = z[:, :, -1]
        return self.head(z).squeeze(-1)

class TransformerClassifier(nn.Module):
    def __init__(self, feature_dim: int, window: int, model_dim: int = 160, heads: int = 4, layers: int = 3):
        super().__init__()
        self.proj = nn.Linear(feature_dim, model_dim)
        self.pos = nn.Parameter(torch.zeros(1, window, model_dim))
        layer = nn.TransformerEncoderLayer(
            d_model=model_dim,
            nhead=heads,
            dim_feedforward=320,
            dropout=0.12,
            activation="gelu",
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=layers)
        self.head = nn.Sequential(
            nn.LayerNorm(model_dim),
            nn.Linear(model_dim, 96),
            nn.GELU(),
            nn.Dropout(0.10),
            nn.Linear(96, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.proj(x) + self.pos[:, : x.shape[1], :]
        z = self.encoder(z)
        return self.head(z[:, -1, :]).squeeze(-1)

def train_torch_classifier(model: nn.Module, x_train: np.ndarray, y_train: np.ndarray, x_val: np.ndarray, y_val: np.ndarray, x_test: np.ndarray, seed: int, model_name: str):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    model = model.to(DEVICE)
    ds = TensorDataset(torch.tensor(x_train), torch.tensor(y_train))
    loader = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True)

    pos = max(float(y_train.sum()), 1.0)
    neg = max(float(len(y_train) - y_train.sum()), 1.0)
    pos_weight = torch.tensor([neg / pos], dtype=torch.float32, device=DEVICE)

    opt = torch.optim.AdamW(model.parameters(), lr=0.0012, weight_decay=0.00025)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)

    x_val_t = torch.tensor(x_val).to(DEVICE)
    y_val_t = torch.tensor(y_val).to(DEVICE)

    best_val = float("inf")
    best_state = None
    patience = 140
    stale = 0
    losses = []

    start = time.time()
    for epoch in range(EPOCHS):
        model.train()
        epoch_losses = []
        for xb, yb in loader:
            xb = xb.to(DEVICE)
            yb = yb.to(DEVICE)
            logits = model(xb)
            loss = loss_fn(logits, yb)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            epoch_losses.append(float(loss.detach().cpu()))

        scheduler.step()
        train_loss = float(np.mean(epoch_losses)) if epoch_losses else 0.0

        model.eval()
        with torch.no_grad():
            val_logits = model(x_val_t)
            val_loss = float(loss_fn(val_logits, y_val_t).detach().cpu())

        losses.append({"epoch": epoch + 1, "train_loss": train_loss, "val_loss": val_loss})

        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1

        if epoch in {0, 49, 99, 199, 399, EPOCHS - 1} or stale == patience:
            print(f"seed={seed} model={model_name} epoch={epoch+1}/{EPOCHS} train_loss={train_loss:.8f} val_loss={val_loss:.8f} stale={stale}", flush=True)

        if stale >= patience and epoch >= 220:
            print(f"seed={seed} model={model_name} early_stop_epoch={epoch+1} best_val={best_val:.8f}", flush=True)
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        probs = torch.sigmoid(model(torch.tensor(x_test).to(DEVICE))).detach().cpu().numpy()

    elapsed = time.time() - start
    return model.cpu(), probs, losses, elapsed, best_val

def run() -> int:
    keep_windows_awake()
    print(f"RUN_ID={RUN_ID}", flush=True)
    print(f"DEVICE={DEVICE}", flush=True)
    print(f"CUDA_AVAILABLE={torch.cuda.is_available()}", flush=True)
    if torch.cuda.is_available():
        print(f"CUDA_DEVICE={torch.cuda.get_device_name(0)}", flush=True)

    df, feature_cols, manifest = build_v4_frame()
    x, y, periods, entities = build_windows(df, feature_cols)

    unique_periods = sorted(set(periods))
    train_cutoff = unique_periods[int(len(unique_periods) * 0.68)]
    val_cutoff = unique_periods[int(len(unique_periods) * 0.84)]

    train_mask = np.asarray([p <= train_cutoff for p in periods])
    val_mask = np.asarray([(p > train_cutoff) and (p <= val_cutoff) for p in periods])
    test_mask = np.asarray([p > val_cutoff for p in periods])

    x_train_raw, x_val_raw, x_test_raw = x[train_mask], x[val_mask], x[test_mask]
    y_train, y_val, y_test = y[train_mask], y[val_mask], y[test_mask]

    if len(np.unique(y_test)) < 2:
        print("WARNING: test split has a single class. Metrics will be limited.", flush=True)

    scaler = StandardScaler()
    feature_dim = x.shape[-1]
    x_train = scaler.fit_transform(x_train_raw.reshape(-1, feature_dim)).reshape(x_train_raw.shape)
    x_val = scaler.transform(x_val_raw.reshape(-1, feature_dim)).reshape(x_val_raw.shape)
    x_test = scaler.transform(x_test_raw.reshape(-1, feature_dim)).reshape(x_test_raw.shape)

    flat_train = x_train.reshape(x_train.shape[0], -1)
    flat_val = x_val.reshape(x_val.shape[0], -1)
    flat_test = x_test.reshape(x_test.shape[0], -1)

    completed = completed_keys()

    classical = {
        "logistic_regression_balanced": LogisticRegression(max_iter=20000, class_weight="balanced", n_jobs=-1),
        "random_forest_classifier": RandomForestClassifier(n_estimators=700, min_samples_leaf=2, class_weight="balanced_subsample", random_state=42, n_jobs=-1),
        "extra_trees_classifier": ExtraTreesClassifier(n_estimators=700, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=-1),
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=350, learning_rate=0.045, l2_regularization=0.02, random_state=42),
    }

    for name, model in classical.items():
        key = (name, "none")
        if key in completed:
            print(f"SKIP completed classical={name}", flush=True)
            continue
        t0 = time.time()
        model.fit(flat_train, y_train)
        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(flat_test)[:, 1]
        else:
            score = model.decision_function(flat_test)
            prob = 1.0 / (1.0 + np.exp(-score))
        metrics = safe_classification_metrics(y_test, prob)
        metrics.update({
            "run_id": RUN_ID,
            "generated_at": now(),
            "model": name,
            "seed": "none",
            "kind": "classical",
            "seconds": round(time.time() - t0, 3),
        })
        append_jsonl(METRICS_JSONL, metrics)
        print(f"classical={name} metrics={metrics}", flush=True)

    deep_factories = [
        ("gru_classifier", lambda: GRUClassifier(feature_dim)),
        ("tcn_classifier", lambda: TCNClassifier(feature_dim)),
        ("temporal_transformer_classifier", lambda: TransformerClassifier(feature_dim, WINDOW)),
    ]

    for seed in SEEDS:
        for model_name, factory in deep_factories:
            key = (model_name, seed)
            if key in completed_keys():
                print(f"SKIP completed deep={model_name} seed={seed}", flush=True)
                continue

            model = factory()
            trained, prob, losses, elapsed, best_val = train_torch_classifier(
                model=model,
                x_train=x_train,
                y_train=y_train,
                x_val=x_val,
                y_val=y_val,
                x_test=x_test,
                seed=seed,
                model_name=model_name,
            )
            metrics = safe_classification_metrics(y_test, prob)
            weights_path = RUN_DIR / f"{model_name}_seed_{seed}.pt"
            loss_path = RUN_DIR / f"{model_name}_seed_{seed}_losses.json"
            pred_path = RUN_DIR / f"{model_name}_seed_{seed}_test_predictions.csv"

            torch.save(
                {
                    "model_state_dict": trained.state_dict(),
                    "feature_columns": feature_cols,
                    "window": WINDOW,
                    "horizon": HORIZON,
                    "seed": seed,
                    "target": TARGET,
                    "threshold": manifest["target_threshold"],
                },
                weights_path,
            )

            loss_path.write_text(json.dumps({"losses": losses, "best_val_loss": best_val}, indent=2) + "\n", encoding="utf-8")
            pd.DataFrame({"y_true": y_test.astype(int), "probability": prob}).to_csv(pred_path, index=False)

            metrics.update({
                "run_id": RUN_ID,
                "generated_at": now(),
                "model": model_name,
                "seed": seed,
                "kind": "deep",
                "seconds": round(elapsed, 3),
                "best_val_loss": round(float(best_val), 10),
                "weights": str(weights_path.relative_to(ROOT)),
                "losses": str(loss_path.relative_to(ROOT)),
                "predictions": str(pred_path.relative_to(ROOT)),
            })
            append_jsonl(METRICS_JSONL, metrics)
            print(f"deep={model_name} seed={seed} metrics={metrics}", flush=True)

    rows = read_metrics()
    def sort_key(row: dict):
        roc = row.get("roc_auc")
        pr = row.get("pr_auc")
        f1 = row.get("f1")
        return (
            -1 if roc is None else -float(roc),
            -1 if pr is None else -float(pr),
            -float(f1 or 0),
        )

    leaderboard = sorted(rows, key=sort_key)
    summary = {
        "run_id": RUN_ID,
        "generated_at": now(),
        "device": str(DEVICE),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "status": "basecamp4_v4_shock_target_run_complete",
        "boundary": "Long CPU/GPU-aware multi-seed classification run on a harder future shock/regime-change target. Still bounded public-source data; not paper-grade validation.",
        "source_manifest": str(SOURCE_MANIFEST.relative_to(ROOT)),
        "feature_manifest_v4": str((RUN_DIR / "enterprise_temporal_manifest_v4_shock.json").relative_to(ROOT)),
        "training_rows": int(len(df)),
        "windows": int(len(x)),
        "train_windows": int(train_mask.sum()),
        "val_windows": int(val_mask.sum()),
        "test_windows": int(test_mask.sum()),
        "entities": int(df["entity_id"].nunique()),
        "periods": int(df["period"].nunique()),
        "feature_count": int(len(feature_cols)),
        "window": WINDOW,
        "horizon": HORIZON,
        "epochs": EPOCHS,
        "seeds": SEEDS,
        "target": TARGET,
        "target_definition": manifest["target_definition"],
        "target_threshold": manifest["target_threshold"],
        "target_positive_rate": manifest["target_positive_rate"],
        "split": {
            "type": "time_based_train_val_test",
            "train_through_period": train_cutoff,
            "validation_through_period": val_cutoff,
        },
        "leaderboard": leaderboard,
        "best_model_by_roc_auc": leaderboard[0]["model"] if leaderboard else None,
        "best_seed": leaderboard[0].get("seed") if leaderboard else None,
        "claim_boundary": [
            "No PHI or patient-level records.",
            "Public-source bounded marts only.",
            "CMS workbook signal is aggregate utilization/payment context.",
            "Passive openFDA/MAUDE reports cannot establish causality or incidence.",
            "V4 target is a harder engineered shock/regime-change benchmark, not clinical or causal prediction.",
        ],
    }

    (RUN_DIR / "model_card_v4_shock.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    history = []
    if HISTORY_OUT.exists():
        try:
            history = json.loads(HISTORY_OUT.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append(summary)
    HISTORY_OUT.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2), flush=True)
    release_windows_awake()
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(run())
    finally:
        release_windows_awake()
