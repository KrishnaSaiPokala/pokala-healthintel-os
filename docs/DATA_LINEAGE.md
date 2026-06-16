# Data Lineage and Evidence Contract

HealthIntel OS treats every score as an evidence-backed object. A score is not valid unless it can be traced to source metadata, refresh timing, row counts, feature definitions, and caveats.

## Current MVP source families

- NPPES Provider Index
- CMS utilization and reimbursement marts
- openFDA / MAUDE-style device-event signals
- ClinicalTrials.gov study-density summaries
- CMS Open Payments summaries
- HHS OCR breach signals

## Evidence object contract

Each evidence item must include:

```json
{
  "id": "stable evidence identifier",
  "claim": "human-readable claim",
  "source": "source or mart name",
  "freshness": "refresh or generation status",
  "rows": 0
}
```

## Lineage rules

1. Every visible score must link to at least one evidence item.
2. Public-source caveats must be shown near interpretation.
3. Derived artifacts must be reproducible from scripts or documented generation steps.
4. PHI, patient-level records, and private credentials are prohibited.
5. Demo data must be labeled as demo, generated, or sample-derived when applicable.
