# Model Evaluation Deep Dive — Basecamp5 Plan

## Goal

Move from a strong portfolio demo to a more robust Healthcare IT + Deep Learning artifact by adding stronger baselines, temporal validation, calibration, and failure analysis.

## Required comparisons

- Majority baseline
- Logistic regression
- Random forest
- Gradient boosting
- MLP
- Temporal CNN / TCN
- GRU or LSTM
- Temporal transformer

## Required validation

- Walk-forward temporal split
- Final holdout window
- At least 7 seeds
- Baseline pressure comparison
- Feature-family ablation
- Source-family ablation
- Calibration / Brier score
- Failure-case notes

## Epoch policy

More epochs matter only with early stopping, checkpointing, validation tracking, seed variance, and overfitting notes.

## Public claim boundary

This remains a research benchmark unless externally validated. It is not clinical forecasting, CDS, or patient-level prediction.
