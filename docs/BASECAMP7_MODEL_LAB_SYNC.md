# Basecamp7 Model Lab Sync

Generated: 2026-06-20T22:08:51.647147+00:00

Basecamp7 syncs real Basecamp6 baseline outputs into frontend-readable JSON and attempts a real MLP baseline with early stopping.

- Dataset: data\models\run_history_v4\basecamp4_shock_20260618_121556\enterprise_temporal_sequences_v4_shock.csv
- Target: target_v4_opportunity_shock

## Results

| Model | Status | ROC-AUC | PR-AUC | Balanced accuracy | F1 | Notes |
|---|---|---:|---:|---:|---:|---|
| majority_baseline | completed | 0.5 | 0.25333333333333335 | 0.5 | 0.0 | floor |
| logistic_regression | completed | 0.9986424394319131 | 0.9962466568502587 | 0.9735797827903091 | 0.9618768328445748 | linear |
| random_forest | completed | 1.0 | 1.0 | 1.0 | 1.0 | nonlinear |
| hist_gradient_boosting | completed | 1.0 | 1.0 | 1.0 | 1.0 | boosting |
| mlp_classifier | completed | 0.9998844144435711 | 0.9996638857201486 | 0.9921979749410513 | 0.9883720930232558 | Real sklearn MLP baseline with early stopping; one seed only, not final DL claim. |

## Boundary

Research benchmark only. No PHI. Not clinical decision support. No patient-level prediction.