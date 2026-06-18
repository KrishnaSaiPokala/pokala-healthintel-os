from __future__ import annotations

import json
import math
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "data" / "features" / "enterprise_temporal_sequences.csv"
CMS_MART = ROOT / "data" / "processed" / "public_api_marts" / "cms_physician_supplier_utilization_mart.csv"
SOURCE_MANIFEST = ROOT / "data" / "source_manifest.real_api_v1.json"
OUT_DIR = ROOT / "data" / "models" / "run_history"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RUN_ID = datetime.now(timezone.utc).strftime("basecamp3_v3_%Y%m%d_%H%M%S")
RUN_DIR = OUT_DIR / RUN_ID
RUN_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_OUT = ROOT / "data" / "models" / "enterprise_model_card_v3.json"
HISTORY_OUT = ROOT / "data" / "models" / "enterprise_run_history.json"

WINDOW = 18
EPOCHS = 650
BATCH_SIZE = 64
SEEDS = [7, 17, 29, 42, 71]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def metric_pack(y_true: np.ndarray, y_pred: np.ndarray, last_values: np.ndarray) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    actual_direction = np.sign(y_true - last_values)
    pred_direction = np.sign(y_pred - last_values)
    direction = float(np.mean(actual_direction == pred_direction))
    return {"mae": round(float(mae), 8), "rmse": round(float(rmse), 8), "directional_accuracy": round(direction, 8)}


def cms_pressure_features() -> dict:
    if not CMS_MART.exists():
        return {"cms_rows": 0, "cms_payment_pressure": 0.0, "cms_utilization_pressure": 0.0, "cms_numeric_signal": 0.0}
    cms = pd.read_csv(CMS_MART)
    vals = pd.to_numeric(cms.get("numeric_value", pd.Series(dtype=float)), errors="coerce").dropna()
    if vals.empty:
        return {"cms_rows": int(len(cms)), "cms_payment_pressure": 0.0, "cms_utilization_pressure": 0.0, "cms_numeric_signal": 0.0}
    large_vals = vals[vals > vals.quantile(0.75)]
    payment_pressure = float(np.log1p(large_vals.mean())) if not large_vals.empty else float(np.log1p(vals.mean()))
    utilization_pressure = float(np.log1p(vals.median()))
    numeric_signal = float(np.log1p(vals.quantile(0.90)))
    return {"cms_rows": int(len(cms)), "cms_payment_pressure": payment_pressure, "cms_utilization_pressure": utilization_pressure, "cms_numeric_signal": numeric_signal}


def build_v3_frame() -> tuple[pd.DataFrame, list[str], dict]:
    if not FEATURES.exists():
        raise SystemExit(f"Missing feature matrix: {FEATURES}")
    df = pd.read_csv(FEATURES)
    df["period_dt"] = pd.to_datetime(df["period"], errors="coerce")
    df = df.dropna(subset=["period_dt", "target_next_composite_opportunity"]).copy()
    df = df.sort_values(["entity_id", "period_dt"]).reset_index(drop=True)
    cms = cms_pressure_features()
    df["cms_rows"] = cms["cms_rows"]
    df["cms_payment_pressure"] = cms["cms_payment_pressure"]
    df["cms_utilization_pressure"] = cms["cms_utilization_pressure"]
    df["cms_numeric_signal"] = cms["cms_numeric_signal"]
    df["period_index"] = df.groupby("entity_id").cumcount()
    df["month"] = df["period_dt"].dt.month
    df["year"] = df["period_dt"].dt.year
    df["sin_month"] = np.sin(2 * np.pi * df["month"] / 12.0)
    df["cos_month"] = np.cos(2 * np.pi * df["month"] / 12.0)
    df["market_x_cms_payment"] = df["market_signal"] * df["cms_payment_pressure"]
    df["provider_x_cms_utilization"] = df["provider_share"] * df["cms_utilization_pressure"]
    df["safety_adjusted_payment_pressure"] = df["cms_payment_pressure"] / (1.0 + df["safety_signal"])
    for col in ["composite_opportunity", "market_signal", "safety_signal", "trial_starts_6mo", "device_events_6mo"]:
        df[f"{col}_lag1"] = df.groupby("entity_id")[col].shift(1)
        df[f"{col}_lag3"] = df.groupby("entity_id")[col].shift(3)
        df[f"{col}_roll6_mean"] = df.groupby("entity_id")[col].transform(lambda x: x.rolling(6, min_periods=1).mean())
        df[f"{col}_roll12_mean"] = df.groupby("entity_id")[col].transform(lambda x: x.rolling(12, min_periods=1).mean())
        df[f"{col}_velocity"] = df.groupby("entity_id")[col].diff().fillna(0.0)
    df = df.fillna(0.0)
    non_features = {"entity_id", "region", "specialty", "city", "period", "period_dt", "target_next_composite_opportunity"}
    feature_cols = [c for c in df.columns if c not in non_features and pd.api.types.is_numeric_dtype(df[c])]
    v3_manifest = {"generated_at": now(), "status": "enterprise_temporal_matrix_v3_runtime", "boundary": "Runtime-expanded v3 feature frame using bounded public-source marts plus CMS utilization/payment pressure. Not paper-scale claims.", "base_feature_matrix": str(FEATURES.relative_to(ROOT)), "cms_mart": str(CMS_MART.relative_to(ROOT)) if CMS_MART.exists() else None, "rows": int(len(df)), "entities": int(df["entity_id"].nunique()), "periods": int(df["period"].nunique()), "feature_columns": feature_cols, "target": "target_next_composite_opportunity", "cms_features": cms}
    (RUN_DIR / "enterprise_temporal_manifest_v3.json").write_text(json.dumps(v3_manifest, indent=2) + "\n", encoding="utf-8")
    df.to_csv(RUN_DIR / "enterprise_temporal_sequences_v3.csv", index=False)
    return df, feature_cols, v3_manifest


def build_windows(df: pd.DataFrame, feature_cols: list[str]):
    xs, ys, last_values, periods, entities = [], [], [], [], []
    for entity_id, group in df.groupby("entity_id"):
        group = group.sort_values("period_dt").reset_index(drop=True)
        values = group[feature_cols].to_numpy(dtype=np.float32)
        target = group["target_next_composite_opportunity"].to_numpy(dtype=np.float32)
        composite = group["composite_opportunity"].to_numpy(dtype=np.float32)
        period_values = group["period"].astype(str).tolist()
        for idx in range(WINDOW - 1, len(group)):
            xs.append(values[idx - WINDOW + 1: idx + 1])
            ys.append(target[idx])
            last_values.append(composite[idx])
            periods.append(period_values[idx])
            entities.append(str(entity_id))
    return np.asarray(xs, dtype=np.float32), np.asarray(ys, dtype=np.float32), np.asarray(last_values, dtype=np.float32), periods, entities


class GRURegressor(nn.Module):
    def __init__(self, feature_dim: int, hidden_dim: int = 96, layers: int = 2):
        super().__init__()
        self.gru = nn.GRU(feature_dim, hidden_dim, num_layers=layers, dropout=0.10, batch_first=True)
        self.head = nn.Sequential(nn.LayerNorm(hidden_dim), nn.Linear(hidden_dim, 64), nn.GELU(), nn.Dropout(0.05), nn.Linear(64, 1))
    def forward(self, x):
        out, _ = self.gru(x)
        return self.head(out[:, -1, :]).squeeze(-1)


class TemporalTransformerRegressor(nn.Module):
    def __init__(self, feature_dim: int, window: int, model_dim: int = 128, heads: int = 4, layers: int = 3):
        super().__init__()
        self.proj = nn.Linear(feature_dim, model_dim)
        self.pos = nn.Parameter(torch.zeros(1, window, model_dim))
        encoder_layer = nn.TransformerEncoderLayer(d_model=model_dim, nhead=heads, dim_feedforward=256, dropout=0.10, activation="gelu", batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=layers)
        self.head = nn.Sequential(nn.LayerNorm(model_dim), nn.Linear(model_dim, 64), nn.GELU(), nn.Dropout(0.05), nn.Linear(64, 1))
    def forward(self, x):
        z = self.proj(x) + self.pos[:, :x.shape[1], :]
        z = self.encoder(z)
        return self.head(z[:, -1, :]).squeeze(-1)


class TCNRegressor(nn.Module):
    def __init__(self, feature_dim: int, hidden: int = 96):
        super().__init__()
        self.net = nn.Sequential(nn.Conv1d(feature_dim, hidden, kernel_size=3, padding=2, dilation=1), nn.GELU(), nn.Conv1d(hidden, hidden, kernel_size=3, padding=4, dilation=2), nn.GELU(), nn.Conv1d(hidden, hidden, kernel_size=3, padding=8, dilation=4), nn.GELU())
        self.head = nn.Sequential(nn.LayerNorm(hidden), nn.Linear(hidden, 64), nn.GELU(), nn.Linear(64, 1))
    def forward(self, x):
        z = x.transpose(1, 2)
        z = self.net(z)
        z = z[:, :, -x.shape[1]:]
        z = z[:, :, -1]
        return self.head(z).squeeze(-1)


def train_torch_model(model, x_train, y_train, x_test, seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    model = model.to(DEVICE)
    ds = TensorDataset(torch.tensor(x_train), torch.tensor(y_train))
    loader = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True)
    opt = torch.optim.AdamW(model.parameters(), lr=0.0015, weight_decay=0.0002)
    loss_fn = nn.SmoothL1Loss()
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=EPOCHS)
    losses = []
    start = time.time()
    for epoch in range(EPOCHS):
        model.train()
        epoch_losses = []
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            epoch_losses.append(float(loss.detach().cpu()))
        scheduler.step()
        losses.append(float(np.mean(epoch_losses)) if epoch_losses else 0.0)
        if epoch in {0, 49, 99, 199, 399, EPOCHS - 1}:
            print(f"seed={seed} model={model.__class__.__name__} epoch={epoch+1}/{EPOCHS} loss={losses[-1]:.8f}")
    model.eval()
    with torch.no_grad():
        preds = model(torch.tensor(x_test).to(DEVICE)).detach().cpu().numpy()
    return model.cpu(), preds, losses, time.time() - start


def main() -> int:
    print(f"RUN_ID={RUN_ID}")
    print(f"DEVICE={DEVICE}")
    print(f"CUDA_AVAILABLE={torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA_DEVICE={torch.cuda.get_device_name(0)}")
    df, feature_cols, _ = build_v3_frame()
    x, y, last_values, periods, _entities = build_windows(df, feature_cols)
    unique_periods = sorted(set(periods))
    cutoff = unique_periods[int(len(unique_periods) * 0.80)]
    train_mask = np.asarray([p <= cutoff for p in periods])
    test_mask = ~train_mask
    x_train_raw, x_test_raw = x[train_mask], x[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]
    last_test = last_values[test_mask]
    scaler = StandardScaler()
    feature_dim = x.shape[-1]
    x_train = scaler.fit_transform(x_train_raw.reshape(-1, feature_dim)).reshape(x_train_raw.shape)
    x_test = scaler.transform(x_test_raw.reshape(-1, feature_dim)).reshape(x_test_raw.shape)
    flat_train = x_train.reshape(x_train.shape[0], -1)
    flat_test = x_test.reshape(x_test.shape[0], -1)
    composite_idx = feature_cols.index("composite_opportunity")
    persistence_pred = x_test_raw[:, -1, composite_idx]
    rolling_pred = x_test_raw[:, :, composite_idx].mean(axis=1)
    baseline_results = {"persistence_last_value": metric_pack(y_test, persistence_pred, last_test), "rolling_window_mean": metric_pack(y_test, rolling_pred, last_test)}
    classical = {"ridge": Ridge(alpha=1.0), "elastic_net": ElasticNet(alpha=0.0005, l1_ratio=0.25, max_iter=20000, random_state=42), "random_forest": RandomForestRegressor(n_estimators=500, min_samples_leaf=2, random_state=42, n_jobs=-1), "extra_trees": ExtraTreesRegressor(n_estimators=500, min_samples_leaf=2, random_state=42, n_jobs=-1)}
    for name, model in classical.items():
        t0 = time.time()
        model.fit(flat_train, y_train)
        pred = model.predict(flat_test)
        baseline_results[name] = metric_pack(y_test, pred, last_test)
        baseline_results[name]["seconds"] = round(time.time() - t0, 3)
        print(f"classical={name} metrics={baseline_results[name]}")
    deep_runs = []
    for seed in SEEDS:
        for model_name, model in [("gru", GRURegressor(feature_dim)), ("tcn", TCNRegressor(feature_dim)), ("temporal_transformer", TemporalTransformerRegressor(feature_dim, WINDOW))]:
            trained, pred, losses, elapsed = train_torch_model(model, x_train, y_train, x_test, seed)
            run_metrics = metric_pack(y_test, pred, last_test)
            run_metrics["seconds"] = round(elapsed, 3)
            run_metrics["seed"] = seed
            run_metrics["model"] = model_name
            run_metrics["final_train_smooth_l1"] = round(float(losses[-1]), 10)
            weights_path = RUN_DIR / f"{model_name}_seed_{seed}.pt"
            torch.save({"model_state_dict": trained.state_dict(), "feature_columns": feature_cols, "window": WINDOW, "seed": seed}, weights_path)
            run_metrics["weights"] = str(weights_path.relative_to(ROOT))
            (RUN_DIR / f"{model_name}_seed_{seed}_losses.json").write_text(json.dumps({"losses": losses}, indent=2) + "\n", encoding="utf-8")
            deep_runs.append(run_metrics)
            print(f"deep={model_name} seed={seed} metrics={run_metrics}")
    all_rows = []
    for name, vals in baseline_results.items():
        all_rows.append({"model": name, "seed": None, **vals})
    all_rows.extend(deep_runs)
    leaderboard = sorted(all_rows, key=lambda r: r["rmse"])
    summary = {"run_id": RUN_ID, "generated_at": now(), "device": str(DEVICE), "cuda_available": bool(torch.cuda.is_available()), "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None, "status": "basecamp3_v3_full_power_cpu_gpu_aware_run_complete", "boundary": "Longer multi-seed model comparison over bounded public-source temporal features. Still not paper-grade or enterprise production.", "source_manifest": str(SOURCE_MANIFEST.relative_to(ROOT)), "feature_manifest_v3": str((RUN_DIR / "enterprise_temporal_manifest_v3.json").relative_to(ROOT)), "training_rows": int(len(df)), "windows": int(len(x)), "train_windows": int(train_mask.sum()), "test_windows": int(test_mask.sum()), "entities": int(df["entity_id"].nunique()), "periods": int(df["period"].nunique()), "feature_count": int(len(feature_cols)), "window": WINDOW, "epochs": EPOCHS, "seeds": SEEDS, "split": {"type": "time_based_holdout", "train_through_period": cutoff}, "leaderboard": leaderboard, "best_model_by_rmse": leaderboard[0]["model"], "claim_boundary": ["No PHI or patient-level records.", "Public-source bounded marts only.", "CMS workbook signal is aggregate utilization/payment context.", "Passive openFDA/MAUDE reports cannot establish causality or incidence.", "Current v3 run is stronger than the previous quick run but still not paper-scale validation."]}
    (RUN_DIR / "model_card_v3.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    history = []
    if HISTORY_OUT.exists():
        try:
            history = json.loads(HISTORY_OUT.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.append(summary)
    HISTORY_OUT.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
