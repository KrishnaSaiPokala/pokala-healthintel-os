# Leakage-Clean Benchmark v2

## Status

- Status: `completed`
- Generated: `2026-06-21T22:37:07.269038+00:00`
- Source dataset: `data/models/run_history_v4/basecamp4_shock_20260618_121556/enterprise_temporal_sequences_v4_shock.csv`
- Target: `target_v4_opportunity_shock`
- Clean feature count: `120`
- Completed seed runs: `189`
- Failed seed runs: `0`
- Best model: `clean_torch_transformer_encoder_21_seed`
- Best ROC-AUC mean: `0.997516`

## Cleaning rules

- Removed target/future/next/lead/lookahead/post/outcome/label-style feature names.
- Removed features with absolute target correlation >= `0.92`.
- Removed constant columns and non-numeric columns.

## Boundary

- Public benchmark only.
- No PHI.
- Not clinical decision support.
- No patient-level prediction claim.
- True summit temporal proof still requires future walk-forward tensor validation.
