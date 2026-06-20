#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUN_DIR = REPO / ".run" / "basecamp5"
RUN_DIR.mkdir(parents=True, exist_ok=True)

data_expansion = [
  ["NPPES", "Provider identity/taxonomy context", "high", "Registry context only"],
  ["CMS Medicare utilization/payment", "Aggregate reimbursement/service context", "high", "No negotiated rates or patient economics"],
  ["CMS hospital price transparency", "Public pricing context", "medium", "Posted data can be incomplete/inconsistent"],
  ["openFDA MAUDE", "Device-event safety-pressure context", "high", "Passive reports cannot establish causality/incidence"],
  ["openFDA FAERS", "Drug adverse-event context", "medium", "Passive reports; not causal"],
  ["ClinicalTrials.gov", "Trial and innovation context", "high", "Trial presence is not outcome proof"],
  ["CMS Open Payments", "Industry relationship context", "medium", "Disclosure is not misconduct or endorsement"],
  ["FDA AI-enabled medical device list", "Regulatory category/product landscape", "high", "Listing is not market success"],
  ["HHS OCR Breach Portal", "Privacy/security incident context", "medium", "Breach context only"],
  ["CDC PLACES / population context", "Aggregate regional context", "medium", "Aggregate estimates only"],
]

model_suite = [
  ["Majority baseline", "floor comparison", "n/a"],
  ["Logistic regression", "linear baseline", "n/a"],
  ["Random forest", "nonlinear tabular baseline", "n/a"],
  ["Gradient boosting", "strong tabular comparator", "n/a"],
  ["MLP", "simple neural baseline", "300-800 with early stopping"],
  ["Temporal CNN / TCN", "sequence baseline", "500-1200 with early stopping"],
  ["GRU/LSTM", "recurrent sequence baseline", "500-1200 with early stopping"],
  ["Temporal transformer", "high-capacity sequence candidate", "720-2000 with early stopping"],
]

manifest = {
  "run_id": "basecamp5_model_data_upgrade_framework",
  "created_at_utc": datetime.now(timezone.utc).isoformat(),
  "purpose": "Prepare the next real robust public-source HIT + DL benchmark run without inventing metrics.",
  "data_expansion": [
    {"source": s, "role": r, "priority": p, "boundary": b}
    for s, r, p, b in data_expansion
  ],
  "model_suite": [
    {"family": m, "purpose": p, "training_policy": e}
    for m, p, e in model_suite
  ],
  "evaluation_protocol": {
    "splits": ["walk-forward temporal split", "final holdout window", "seed variance across 7 seeds"],
    "metrics": ["ROC-AUC", "PR-AUC", "balanced accuracy", "precision", "recall", "F1", "Brier score", "failure cases"],
    "ablations": ["feature-family ablation", "source-family ablation", "baseline pressure comparison"],
    "guardrails": ["No PHI", "No CDS", "No patient-level prediction", "No causality or incidence claims from passive reports"],
  },
  "training_policy": {
    "max_epochs": 2000,
    "early_stopping": True,
    "patience": 50,
    "seeds": [7, 17, 29, 42, 71, 101, 131],
    "checkpoint": "best validation PR-AUC with ROC-AUC tracked",
  },
}

json_path = RUN_DIR / "basecamp5_model_data_upgrade_manifest.json"
json_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

md = "# Basecamp5 Model/Data Upgrade Manifest\n\n"
md += f"Generated: {manifest['created_at_utc']}\n\n"
md += "This is a robust framework for the next real model/data run. It does **not** invent new performance.\n\n"
md += "## Data expansion\n\n| Source | Priority | Role | Boundary |\n|---|---:|---|---|\n"
for row in manifest["data_expansion"]:
    md += f"| {row['source']} | {row['priority']} | {row['role']} | {row['boundary']} |\n"
md += "\n## Model suite\n\n| Model | Purpose | Training policy |\n|---|---|---|\n"
for row in manifest["model_suite"]:
    md += f"| {row['family']} | {row['purpose']} | {row['training_policy']} |\n"
md += "\n## Evaluation requirements\n\n- Walk-forward temporal validation\n- Final holdout window\n- Seed variance\n- Baseline comparison\n- Calibration / Brier score\n- Feature/source-family ablations\n- Failure-case notes\n\n## Boundary\n\nResearch benchmark framework only until real training metrics are generated and reviewed. Not clinical decision support.\n"

(REPO / "docs" / "BASECAMP5_MODEL_DATA_UPGRADE_REPORT.md").write_text(md, encoding="utf-8")
print(f"Wrote {json_path}")
print("Wrote docs/BASECAMP5_MODEL_DATA_UPGRADE_REPORT.md")
