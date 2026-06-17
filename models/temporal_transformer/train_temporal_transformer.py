from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "data" / "features" / "temporal_market_sequences.csv"
OUT_DIR = ROOT / "data" / "models"
OUT_JSON = OUT_DIR / "temporal_transformer_results.json"
OUT_PT = OUT_DIR / "temporal_transformer.pt"

FEATURE_COLS = [
    "market",
    "safety",
    "reimbursement",
    "provider_density",
    "market_delta",
    "safety_delta",
    "reimbursement_delta",
]

class TemporalTransformer(nn.Module):
    def __init__(self, input_dim: int, d_model: int = 32, nhead: int = 4, layers: int = 2):
        super().__init__()
        self.proj = nn.Linear(input_dim, d_model)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=96,
            dropout=0.05,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=layers)
        self.head = nn.Sequential(nn.LayerNorm(d_model), nn.Linear(d_model, 1))

    def forward(self, x):
        z = self.proj(x)
        h = self.encoder(z)
        return self.head(h[:, -1, :]).squeeze(-1)

def make_windows(df: pd.DataFrame, window: int = 3):
    X_raw = df[FEATURE_COLS].to_numpy(dtype=np.float32)
    y_raw = df["target_next_market"].to_numpy(dtype=np.float32)

    X, y = [], []
    for i in range(0, len(df) - window + 1):
        X.append(X_raw[i:i + window])
        y.append(y_raw[i + window - 1])

    return np.stack(X), np.asarray(y, dtype=np.float32)

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(FEATURES).sort_values("t")

    if len(df) < 5:
        raise SystemExit("Need at least 5 temporal rows for transformer training.")

    window = min(4, max(3, len(df) // 2))
    X, y = make_windows(df, window=window)

    split = max(1, int(len(X) * 0.70))
    if split >= len(X):
        split = len(X) - 1

    X_train = torch.tensor(X[:split], dtype=torch.float32)
    y_train = torch.tensor(y[:split], dtype=torch.float32)
    X_test = torch.tensor(X[split:], dtype=torch.float32)
    y_test = torch.tensor(y[split:], dtype=torch.float32)

    model = TemporalTransformer(input_dim=len(FEATURE_COLS))
    opt = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=0.01)
    loss_fn = nn.L1Loss()

    model.train()
    losses = []
    for epoch in range(220):
        opt.zero_grad()
        pred = model(X_train)
        loss = loss_fn(pred, y_train)
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))

    model.eval()
    with torch.no_grad():
        test_pred = model(X_test)
        mae = torch.mean(torch.abs(test_pred - y_test)).item()
        rmse = torch.sqrt(torch.mean((test_pred - y_test) ** 2)).item()

    torch.save(model.state_dict(), OUT_PT)

    payload = {
        "status": "temporal_transformer_trained",
        "boundary": "Prototype transformer trained on static demo temporal features. Requires raw-source generated sequences before paper-grade claims.",
        "rows": int(len(df)),
        "windows": int(len(X)),
        "train_windows": int(len(X_train)),
        "test_windows": int(len(X_test)),
        "window": int(window),
        "feature_columns": FEATURE_COLS,
        "target": "target_next_market",
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
            "final_train_l1": float(losses[-1]),
        },
        "artifacts": {
            "weights": str(OUT_PT.relative_to(ROOT)),
            "results": str(OUT_JSON.relative_to(ROOT)),
        },
        "next_steps": [
            "Generate region-specialty-month feature sequences from real source marts.",
            "Add GRU/LSTM baselines.",
            "Add temporal holdout evaluation.",
            "Export attention/feature attribution for Model Lab.",
        ],
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
