# Basecamp5 Model/Data Upgrade Manifest

Generated: 2026-06-20T20:33:10.565509+00:00

This is a robust framework for the next real model/data run. It does **not** invent new performance.

## Data expansion

| Source | Priority | Role | Boundary |
|---|---:|---|---|
| NPPES | high | Provider identity/taxonomy context | Registry context only |
| CMS Medicare utilization/payment | high | Aggregate reimbursement/service context | No negotiated rates or patient economics |
| CMS hospital price transparency | medium | Public pricing context | Posted data can be incomplete/inconsistent |
| openFDA MAUDE | high | Device-event safety-pressure context | Passive reports cannot establish causality/incidence |
| openFDA FAERS | medium | Drug adverse-event context | Passive reports; not causal |
| ClinicalTrials.gov | high | Trial and innovation context | Trial presence is not outcome proof |
| CMS Open Payments | medium | Industry relationship context | Disclosure is not misconduct or endorsement |
| FDA AI-enabled medical device list | high | Regulatory category/product landscape | Listing is not market success |
| HHS OCR Breach Portal | medium | Privacy/security incident context | Breach context only |
| CDC PLACES / population context | medium | Aggregate regional context | Aggregate estimates only |

## Model suite

| Model | Purpose | Training policy |
|---|---|---|
| Majority baseline | floor comparison | n/a |
| Logistic regression | linear baseline | n/a |
| Random forest | nonlinear tabular baseline | n/a |
| Gradient boosting | strong tabular comparator | n/a |
| MLP | simple neural baseline | 300-800 with early stopping |
| Temporal CNN / TCN | sequence baseline | 500-1200 with early stopping |
| GRU/LSTM | recurrent sequence baseline | 500-1200 with early stopping |
| Temporal transformer | high-capacity sequence candidate | 720-2000 with early stopping |

## Evaluation requirements

- Walk-forward temporal validation
- Final holdout window
- Seed variance
- Baseline comparison
- Calibration / Brier score
- Feature/source-family ablations
- Failure-case notes

## Boundary

Research benchmark framework only until real training metrics are generated and reviewed. Not clinical decision support.
