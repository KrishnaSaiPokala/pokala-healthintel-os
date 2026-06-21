# Leakage-Clean Audit

- Audit level: `red`
- Blockers: `1`
- Warnings: `1`
- Dropped by name: `18`
- Dropped by correlation: `0`
- Max remaining absolute correlation: `0.258145`

## Blockers

- Best clean ROC-AUC is near-perfect (0.9975); require temporal split before green.

## Warnings

- Best clean ROC-AUC remains very high (0.9975); retain caution and validate with temporal split.

## Interpretation

This audit is green only for the cleaned tabular benchmark surface. It does not claim clinical utility and does not replace a future walk-forward temporal validation pass.
