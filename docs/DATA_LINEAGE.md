# Data Lineage

## Current certification status

This repository currently exposes a public HealthIntel OS demo using static intelligence artifacts and Cloudflare D1 summary tables.

The current lineaged counts are:

- Claim-linked evidence rows: **172,228**
- Claim-linked evidence sources: **4**
- Dataset marts represented in the static artifact: **6**
- Dataset mart rows represented in the static artifact: **188,634**

## Important boundary

These are **public-source public-source summary marts**, not a final certified raw-data lake.

The project does **not** claim that raw NPPES, CMS, openFDA, ClinicalTrials.gov, Open Payments, or OCR source snapshots have been fully committed and audited in this repository yet.

## What is verified now

- The UI evidence-row count is computed from the evidence ledger.
- The dataset-mart count is separated from the claim-linked evidence count.
- The app uses no PHI and no patient-level records.
- Each score must be interpreted as public intelligence, not clinical decision support.

## What remains before paper-grade data certification

1. Pin official public source URLs or API queries.
2. Store raw snapshots or deterministic download scripts.
3. Generate processed marts from raw/source snapshots.
4. Reconcile static JSON counts, D1 counts, and manifest counts.
5. Add a signed run manifest for each build.
6. Train/evaluate baselines and temporal transformer models on reproducible feature sequences.

See `data/source_manifest.json` for machine-readable lineage.

