from __future__ import annotations
try:
    import torch
    from torch import nn
except Exception:
    torch = None
    nn = object

if torch:
    class GRUBaseline(nn.Module):
        def __init__(self, feature_dim: int, hidden_dim: int = 64, out_dim: int = 4):
            super().__init__()
            self.gru = nn.GRU(feature_dim, hidden_dim, batch_first=True)
            self.head = nn.Linear(hidden_dim, out_dim)
        def forward(self, x):
            _, h = self.gru(x)
            return self.head(h[-1])
