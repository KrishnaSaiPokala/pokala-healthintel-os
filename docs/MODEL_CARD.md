# Model Card: Temporal Transformer Intelligence Layer

## Model status

Prototype / architecture layer. The current deployed MVP uses deterministic scoring over public-data artifacts. The temporal transformer layer is documented and scaffolded for offline sequence modeling.

## Intended use

- Market-entry screening.
- Safety-signal acceleration review.
- Reimbursement momentum analysis.
- Provider-density and innovation trend summarization.
- Executive dossier generation with evidence lineage.

## Not intended for

- Diagnosis.
- Treatment recommendations.
- Clinical triage.
- Patient-level risk prediction.
- Autonomous medical decision-making.
- Regulatory safety determination.

## Inputs

Monthly or quarterly aggregate signal tokens such as utilization volume, Medicare payment, price spread, FDA event rate, trial density, breach history, provider density, and AI-device activity.

## Outputs

Interpretable market/risk/reimbursement screening scores, trend classifications, and attention summaries for evidence review.

## Baselines

The evaluation plan requires deterministic rolling z-score rules, logistic or tree baselines, and recurrent baselines such as GRU/BiLSTM before claiming transformer lift.

## Governance controls

- Public data only.
- No PHI.
- Evidence lineage required.
- Caveats surfaced in UI.
- Model claims separated from clinical claims.
