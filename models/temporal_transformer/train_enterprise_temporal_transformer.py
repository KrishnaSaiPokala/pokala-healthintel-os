from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "data" / "features" / "enterprise_temporal_sequences.csv"
FEATURE_MANIFEST = ROOT / "data" / "features" / "enterprise_temporal_manifest.json"
MODEL_DIR = ROOT / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_OUT = MODEL_DIR / "enterprise_baseline_results.json"
GRU_OUT = MODEL_DIR / "enterprise_gru_results.json"
TRANSFORMER_OUT = MODEL_DIR / "enterprise_temporal_transformer_results.json"
MODEL_CARD_OUT = MODEL_DIR / "enterprise_model_card.json"
GRU_WEIGHTS = MODEL_DIR / "enterprise_gru.pt"
TRANSFORMER_WEIGHTS = MODEL_DIR / "enterprise_temporal_transformer.pt"

SEED = 42
WINDOW = 12
EPOCHS = 80
BATCH_SIZE = 64

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def to_float(value: float) -> float:
    return float(np.round(float(value), 6))

def metrics(y_true: np.ndarray, y_pred: np.ndarray, last_values: np.ndarray) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    actual_direction = np.sign(y_true - last_values)
    pred_direction = np.sign(y_pred - last_values)
    directional_accuracy = float(np.mean(actual_direction == pred_direction))
    return {
        "mae": to_float(mae),
        "rmse": to_float(rmse),
        "directional_accuracy": to_float(directional_accuracy)
    }

def build_windows(df: pd.DataFrame, feature_cols: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str], list[str]]:
    xs = []
    ys = []
    last_values = []
    periods = []
    entities = []
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
    def __init__(self, feature_dim: int, hidden_dim: int = 48) -> None:
        super().__init__()
        self.gru = nn.GRU(feature_dim, hidden_dim, batch_first=True)
        self.head = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.gru(x)
        return self.head(out[:, -1, :]).squeeze(-1)

class TemporalTransformerRegressor(nn.Module):
    def __init__(self, feature_dim: int, window: int, model_dim: int = 64, heads: int = 4, layers: int = 2) -> None:
        super().__init__()
        self.proj = nn.Linear(feature_dim, model_dim)
        self.positional = nn.Parameter(torch.zeros(1, window, model_dim))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=model_dim,
            nhead=heads,
            dim_feedforward=128,
            dropout=0.08,
            batch_first=True,
            activation="gelu"
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=layers)
        self.head = nn.Sequential(
            nn.LayerNorm(model_dim),
            nn.Linear(model_dim, 32),
            nn.GELU(),
            nn.Linear(32, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.proj(x) + self.positional[:, :x.shape[1], :]
        z = self.encoder(z)
        return self.head(z[:, -1, :]).squeeze(-1)

def train_torch_model(model: nn.Module, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray) -> tuple[nn.Module, np.ndarray, float]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    train_ds = TensorDataset(torch.tensor(x_train), torch.tensor(y_train))
    loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    opt = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=0.0001)
    loss_fn = nn.SmoothL1Loss()
    final_loss = 0.0
    for _epoch in range(EPOCHS):
        model.train()
        losses = []
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            losses.append(float(loss.detach().cpu()))
        final_loss = float(np.mean(losses)) if losses else 0.0
    model.eval()
    with torch.no_grad():
        pred = model(torch.tensor(x_test).to(device)).detach().cpu().numpy()
    return model.cpu(), pred, final_loss

def main() -> int:
    if not FEATURES.exists():
        raise SystemExit(f"Missing feature matrix: {FEATURES}")

    feature_manifest = load_json(FEATURE_MANIFEST)
    df = pd.read_csv(FEATURES)
    df["period_dt"] = pd.to_datetime(df["period"], errors="coerce")
    df = df.dropna(subset=["period_dt", "target_next_composite_opportunity"]).copy()

    feature_cols = feature_manifest.get("feature_columns") or [
        c for c in df.columns
        if c not in ["entity_id", "region", "specialty", "city", "period", "period_dt", "target_next_composite_opportunity"]
        and pd.api.types.is_numeric_dtype(df[c])
    ]

    x, y, last_values, periods, entities = build_windows(df, feature_cols)
    if len(x) < 40:
        raise SystemExit(f"Not enough windows for enterprise training: {len(x)}")

    unique_periods = sorted(set(periods))
    cutoff = unique_periods[int(len(unique_periods) * 0.80)]
    train_mask = np.asarray([p <= cutoff for p in periods])
    test_mask = ~train_mask

    x_train_raw = x[train_mask]
    x_test_raw = x[test_mask]
    y_train = y[train_mask]
    y_test = y[test_mask]
    last_test = last_values[test_mask]

    scaler = StandardScaler()
    n_train, window, feature_dim = x_train_raw.shape
    x_train = scaler.fit_transform(x_train_raw.reshape(-1, feature_dim)).reshape(n_train, window, feature_dim)
    x_test = scaler.transform(x_test_raw.reshape(-1, feature_dim)).reshape(x_test_raw.shape[0], window, feature_dim)

    flat_train = x_train.reshape(x_train.shape[0], -1)
    flat_test = x_test.reshape(x_test.shape[0], -1)

    composite_idx = feature_cols.index("composite_opportunity")
    persistence_pred = x_test_raw[:, -1, composite_idx]
    rolling_pred = x_test_raw[:, :, composite_idx].mean(axis=1)

    ridge = Ridge(alpha=1.0)
    ridge.fit(flat_train, y_train)
    ridge_pred = ridge.predict(flat_test)

    forest = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=SEED)
    forest.fit(flat_train, y_train)
    forest_pred = forest.predict(flat_test)

    baseline_results = {
        "status": "enterprise_baselines_trained",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "feature_matrix": str(FEATURES.relative_to(ROOT)),
        "rows": int(len(df)),
        "windows": int(len(x)),
        "train_windows": int(train_mask.sum()),
        "test_windows": int(test_mask.sum()),
        "window": WINDOW,
        "split": {
            "type": "time_based_holdout",
            "train_through_period": cutoff
        },
        "metrics": {
            "persistence_last_value": metrics(y_test, persistence_pred, last_test),
            "rolling_window_mean": metrics(y_test, rolling_pred, last_test),
            "ridge": metrics(y_test, ridge_pred, last_test),
            "random_forest": metrics(y_test, forest_pred, last_test)
        }
    }
    BASELINE_OUT.write_text(json.dumps(baseline_results, indent=2) + "\n", encoding="utf-8")

    gru, gru_pred, gru_loss = train_torch_model(GRURegressor(feature_dim), x_train, y_train, x_test, y_test)
    torch.save({"model_state_dict": gru.state_dict(), "feature_columns": feature_cols, "window": WINDOW}, GRU_WEIGHTS)
    gru_results = {
        "status": "enterprise_gru_trained",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "weights": str(GRU_WEIGHTS.relative_to(ROOT)),
        "final_train_smooth_l1": to_float(gru_loss),
        "metrics": metrics(y_test, gru_pred, last_test)
    }
    GRU_OUT.write_text(json.dumps(gru_results, indent=2) + "\n", encoding="utf-8")

    transformer, transformer_pred, transformer_loss = train_torch_model(TemporalTransformerRegressor(feature_dim, WINDOW), x_train, y_train, x_test, y_test)
    torch.save({"model_state_dict": transformer.state_dict(), "feature_columns": feature_cols, "window": WINDOW}, TRANSFORMER_WEIGHTS)
    transformer_results = {
        "status": "enterprise_temporal_transformer_trained",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "weights": str(TRANSFORMER_WEIGHTS.relative_to(ROOT)),
        "final_train_smooth_l1": to_float(transformer_loss),
        "metrics": metrics(y_test, transformer_pred, last_test),
        "boundary": "Transformer v2 trained on bounded real public API derived temporal feature matrix. This is enterprise demo modeling, not final clinical or paper-scale validation."
    }
    TRANSFORMER_OUT.write_text(json.dumps(transformer_results, indent=2) + "\n", encoding="utf-8")

    all_model_metrics = {
        "persistence_last_value": baseline_results["metrics"]["persistence_last_value"],
        "rolling_window_mean": baseline_results["metrics"]["rolling_window_mean"],
        "ridge": baseline_results["metrics"]["ridge"],
        "random_forest": baseline_results["metrics"]["random_forest"],
        "gru": gru_results["metrics"],
        "temporal_transformer": transformer_results["metrics"]
    }
    best_model = min(all_model_metrics.items(), key=lambda item: item[1]["rmse"])[0]

    model_card = {
        "model_family": "Enterprise temporal market-safety intelligence",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "feature_manifest": str(FEATURE_MANIFEST.relative_to(ROOT)),
        "source_manifest": "data/source_manifest.real_api_v1.json",
        "training_rows": int(len(df)),
        "windows": int(len(x)),
        "entities": int(df["entity_id"].nunique()),
        "periods": int(df["period"].nunique()),
        "feature_columns": feature_cols,
        "target": "target_next_composite_opportunity",
        "models_compared": list(all_model_metrics.keys()),
        "best_model_by_rmse": best_model,
        "metrics": all_model_metrics,
        "artifacts": {
            "baselines": str(BASELINE_OUT.relative_to(ROOT)),
            "gru_results": str(GRU_OUT.relative_to(ROOT)),
            "gru_weights": str(GRU_WEIGHTS.relative_to(ROOT)),
            "transformer_results": str(TRANSFORMER_OUT.relative_to(ROOT)),
            "transformer_weights": str(TRANSFORMER_WEIGHTS.relative_to(ROOT))
        },
        "claim_boundary": [
            "Uses bounded public API samples and derived temporal feature engineering.",
            "Does not use PHI or patient-level records.",
            "Does not provide clinical decision support.",
            "Passive device-event reports cannot establish causality or incidence.",
            "Current results are enterprise-demo validation, not final paper-scale claims."
        ]
    }
    MODEL_CARD_OUT.write_text(json.dumps(model_card, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(model_card, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
