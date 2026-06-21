# Model Leakage and Stability Audit

## Summary

- Overnight benchmark completed 210 seed runs across 10 model families with 0 failed seeds.
- Best ROC-AUC model is torch_transformer_encoder_21_seed with mean ROC-AUC 0.997803.
- High single-feature leakage-risk candidates detected: 5. These should be reviewed before making stronger forecasting claims.
- Feature-name heuristic found 28 fields with target/outcome/future/shock-like terms; review them before asserting causal or forecasting strength.
- Current LSTM/GRU/TCN/Transformer results are architecture benchmarks over single-step tabular tensors, not final true temporal sequence validation.

## Dataset

- Source: `data/models/run_history_v4/basecamp4_shock_20260618_121556/enterprise_temporal_sequences_v4_shock.csv`
- Target: `target_v4_opportunity_shock`
- Rows audited: `2700`
- Numeric features: `227`
- Features scored: `227`

## Stability leaderboard

| Rank | Model | ROC-AUC mean | ROC-AUC std | PR-AUC mean | F1 macro | Failed seeds |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `torch_transformer_encoder_21_seed` | `0.997803` | `0.004658` | `0.995636` | `0.982315` | `0` |
| 2 | `torch_residual_mlp_21_seed` | `0.996085` | `0.005629` | `0.991126` | `0.980147` | `0` |
| 3 | `torch_mlp_21_seed` | `0.995378` | `0.006549` | `0.989761` | `0.974807` | `0` |
| 4 | `torch_wide_deep_mlp_21_seed` | `0.993803` | `0.00782` | `0.988235` | `0.981405` | `0` |
| 5 | `torch_tcn_21_seed` | `0.99235` | `0.008298` | `0.981726` | `0.978788` | `0` |
| 6 | `torch_cnn_mlp_hybrid_21_seed` | `0.992207` | `0.006296` | `0.985708` | `0.976989` | `0` |
| 7 | `torch_gated_mlp_21_seed` | `0.991599` | `0.007823` | `0.983247` | `0.97644` | `0` |
| 8 | `sklearn_mlp_21_seed` | `0.988952` | `0.007439` | `0.979718` | `0.971587` | `0` |
| 9 | `torch_lstm_21_seed` | `0.988061` | `0.007736` | `0.974786` | `0.946967` | `0` |
| 10 | `torch_gru_21_seed` | `0.986829` | `0.008459` | `0.971588` | `0.939721` | `0` |

## Leakage-risk candidates

### High-risk single-feature flags

| Feature | Single-feature AUC | abs corr | MI |
|---|---:|---:|---:|
| `shock_score_raw` | `1.0` | `0.379452` | `0.563475` |
| `delta_composite_h3` | `0.973102` | `0.389627` | `0.534897` |
| `delta_reimbursement_h3` | `0.96216` | `0.391771` | `0.411026` |
| `delta_trial_h3` | `0.962132` | `0.391771` | `0.41459` |
| `delta_market_h3` | `0.954241` | `0.400586` | `0.462163` |

### Feature-name heuristic flags

- `composite_opportunity` terms=['opportunity']
- `target_next_composite_opportunity` terms=['next', 'opportunity', 'target']
- `opportunity_pressure_ratio` terms=['opportunity']
- `composite_opportunity_lag1` terms=['opportunity']
- `composite_opportunity_lag3` terms=['opportunity']
- `composite_opportunity_lag6` terms=['opportunity']
- `composite_opportunity_roll3_mean` terms=['opportunity']
- `composite_opportunity_roll6_mean` terms=['opportunity']
- `composite_opportunity_roll12_mean` terms=['opportunity']
- `composite_opportunity_roll6_std` terms=['opportunity']
- `composite_opportunity_velocity1` terms=['opportunity']
- `composite_opportunity_velocity3` terms=['opportunity']
- `opportunity_pressure_ratio_lag1` terms=['opportunity']
- `opportunity_pressure_ratio_lag3` terms=['opportunity']
- `opportunity_pressure_ratio_lag6` terms=['opportunity']
- `opportunity_pressure_ratio_roll3_mean` terms=['opportunity']
- `opportunity_pressure_ratio_roll6_mean` terms=['opportunity']
- `opportunity_pressure_ratio_roll12_mean` terms=['opportunity']
- `opportunity_pressure_ratio_roll6_std` terms=['opportunity']
- `opportunity_pressure_ratio_velocity1` terms=['opportunity']
- `opportunity_pressure_ratio_velocity3` terms=['opportunity']
- `future_composite_h3` terms=['future']
- `future_market_h3` terms=['future']
- `future_safety_h3` terms=['future']
- `future_reimbursement_h3` terms=['future']
- `future_device_h3` terms=['future']
- `future_trial_h3` terms=['future']
- `shock_score_raw` terms=['shock']

## Boundary

- Public-source benchmark only.
- No PHI.
- Not clinical decision support.
- No patient-level prediction claim.
- This does not replace a true temporal walk-forward validation or a full leakage audit.
