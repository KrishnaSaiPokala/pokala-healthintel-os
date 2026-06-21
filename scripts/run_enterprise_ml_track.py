from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

steps = [
    [sys.executable, "pipelines/features/build_temporal_sequences.py"],
    [sys.executable, "models/baselines/evaluate_temporal_baselines.py"],
    [sys.executable, "models/temporal_transformer/train_temporal_transformer.py"],
]

for step in steps:
    print("\n>>>", " ".join(step))
    subprocess.check_call(step, cwd=ROOT)

print("\nEnterprise ML track v1 complete.")
