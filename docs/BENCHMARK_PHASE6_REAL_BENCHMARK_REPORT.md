# Benchmark Phase 6 Real Benchmark Harness Report

Generated: 2026-06-20T21:39:25.841639+00:00

## Dataset discovery

| Dataset | Rows | Columns | Targets | Ready |
|---|---:|---:|---|---:|
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\enterprise_temporal_sequences_v4_shock.csv | 2700 | 234 | target_v4_opportunity_shock | True |
| data\processed\public_api_marts\cms_physician_supplier_utilization_mart.csv | 2732 | 8 | - | False |
| data\features\enterprise_temporal_sequences.csv | 2700 | 23 | - | False |
| data\models\run_history\Benchmark Phase3_v3_20260617_200429\enterprise_temporal_sequences_v3.csv | 2700 | 61 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\gru_classifier_seed_101_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\gru_classifier_seed_131_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\gru_classifier_seed_17_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\gru_classifier_seed_29_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\gru_classifier_seed_42_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\gru_classifier_seed_71_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\gru_classifier_seed_7_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\tcn_classifier_seed_101_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\tcn_classifier_seed_131_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\tcn_classifier_seed_17_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\tcn_classifier_seed_29_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\tcn_classifier_seed_42_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\tcn_classifier_seed_71_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\tcn_classifier_seed_7_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\temporal_transformer_classifier_seed_101_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\temporal_transformer_classifier_seed_131_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\temporal_transformer_classifier_seed_17_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\temporal_transformer_classifier_seed_29_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\temporal_transformer_classifier_seed_42_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\temporal_transformer_classifier_seed_71_test_predictions.csv | 372 | 2 | - | False |
| data\models\run_history_v4\Benchmark Phase4_shock_20260618_121556\temporal_transformer_classifier_seed_7_test_predictions.csv | 372 | 2 | - | False |
| data\processed\public_api_marts\nppes_tx_radiology_provider_mart.csv | 200 | 10 | - | False |
| data\processed\public_api_marts\clinicaltrials_radiology_ai_mart.csv | 100 | 7 | - | False |
| data\processed\public_api_marts\openfda_device_imaging_event_mart.csv | 100 | 8 | - | False |
| data\features\temporal_market_sequences.csv | 8 | 15 | - | False |

## Benchmark results

| Model | Status | ROC-AUC | PR-AUC | Balanced accuracy | F1 | Notes |
|---|---|---:|---:|---:|---:|---|
| majority_baseline | completed | 0.5 | 0.25333333333333335 | 0.5 | 0.0 | floor |
| logistic_regression | completed | 0.9986424394319131 | 0.9962466568502587 | 0.9735797827903091 | 0.9618768328445748 | linear |
| random_forest | completed | 1.0 | 1.0 | 1.0 | 1.0 | nonlinear |
| hist_gradient_boosting | completed | 1.0 | 1.0 | 1.0 | 1.0 | boosting |

## Next DL step

- Build explicit temporal tensors.
- Run MLP, LSTM, GRU, TCN, FT-Transformer, Temporal Transformer, and Temporal Fusion Transformer.
- Use early stopping, 7 seeds, calibration, ablations, and failure notes.

## Boundary

Research benchmark only. No CDS. No patient-level prediction. No causal/incidence claims.
