# Deep Learning System Design

## Purpose

The deep learning track models temporal movement across healthcare market, safety, reimbursement, and provider-density signals.

The goal is not patient outcome prediction. The goal is public-source strategic intelligence.

## Current status

Current committed ML artifacts include a temporal feature builder, baseline evaluation script, PyTorch temporal transformer training script, baseline result JSON, transformer result JSON, and transformer weight artifact.

The first transformer run is a prototype trained on a small static demo-derived temporal sequence. It proves the ML spine, not final paper-grade performance.

## Target enterprise ML architecture

Raw or bounded public data -> processed marts -> region-specialty-month feature matrix -> temporal train/test split -> baselines and transformer -> model card -> Model Lab UI.

## Feature matrix

Target grain: region x specialty x period.

Feature families: provider supply, utilization intensity, reimbursement proxy, safety-event volume, trial activity, open influence signal, breach/system risk context, lagged deltas, rolling means, rolling volatility, and cross-source momentum.

Targets: next-period market momentum, safety acceleration, reimbursement pressure, and composite opportunity index.

## Baselines

Baselines are required before transformer claims.

Minimum baselines: persistence, rolling mean, ridge regression, random forest, and GRU or LSTM.

The transformer should only be described as useful if it beats or meaningfully complements simple baselines on a time-based holdout.

## Transformer design

Model family: Temporal Transformer Encoder.

Input shape: batch x time_window x feature_dim.

Output: next-period signal or composite opportunity score.

Core components: linear feature projection, temporal representation, transformer encoder blocks, layer normalization, regression head, and optional multi-task heads.

Artifacts: data/models/enterprise_temporal_transformer.pt, data/models/enterprise_temporal_transformer_results.json, and data/models/enterprise_model_card.json.

## Evaluation design

Use time-based splits, not random-only splits.

Required metrics: MAE, RMSE, directional accuracy, baseline comparison, train/test window counts, feature list, and data source manifest reference.

Optional metrics: calibration, error by source family, error by region, error by specialty, and ablation by feature family.

## Model Lab UI integration

The Model Lab should read exported artifacts and display model status, baseline comparison, transformer metrics, feature families, training window count, test window count, claim boundary, and next model milestone.

The UI must not imply clinical validity.

## Claim boundary

Acceptable claim: temporal transformer prototype trained on public-source market, safety, and reimbursement feature sequences.

Not acceptable yet: production-grade AI model for healthcare decision-making.

## Next implementation milestones

1. Add bounded real public API ingestion.
2. Generate expanded region-specialty-month features.
3. Add GRU or LSTM baseline.
4. Train enterprise temporal transformer v2.
5. Export model card.
6. Wire Model Lab to real artifacts.
7. Add paper methods and results section.
