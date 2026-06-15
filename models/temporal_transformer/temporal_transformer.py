"""Lightweight temporal transformer skeleton.

Use this as a model-lab artifact. The SaaS app should not depend on this model to work.
It trains/inferences offline and exports compact scores to JSON/Parquet.
"""
from __future__ import annotations
try:
    import torch
    from torch import nn
except Exception:  # allows repo to import without torch installed
    torch = None
    nn = object

if torch:
    class TemporalSignalTransformer(nn.Module):
        def __init__(self, feature_dim: int, hidden_dim: int = 96, heads: int = 4, layers: int = 2, out_dim: int = 4):
            super().__init__()
            self.input = nn.Linear(feature_dim, hidden_dim)
            enc_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=heads, dim_feedforward=hidden_dim*4, batch_first=True, dropout=0.1)
            self.encoder = nn.TransformerEncoder(enc_layer, num_layers=layers)
            self.head = nn.Sequential(nn.LayerNorm(hidden_dim), nn.Linear(hidden_dim, out_dim))
        def forward(self, x):
            h = self.input(x)
            h = self.encoder(h)
            return self.head(h[:, -1])
else:
    class TemporalSignalTransformer:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise RuntimeError('Install torch to use the temporal transformer model lab.')
