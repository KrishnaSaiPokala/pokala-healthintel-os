# Pokala HealthIntel OS: A Browser-Native Public-Data Intelligence System for Healthcare Market, Safety, and Reimbursement Dossiers

## Abstract

Healthcare strategy teams often need to evaluate market opportunity, safety signals, reimbursement variability, provider density, and innovation momentum across fragmented public datasets. Pokala HealthIntel OS is a browser-native prototype that converts public healthcare data artifacts into evidence-backed intelligence dossiers without using protected health information, paid APIs, or a hosted backend data warehouse. The system combines static public-data marts, a Cloudflare Worker surface, local-first browser interaction, evidence-lineage contracts, and a temporal-modeling workbench. The initial flagship vertical evaluates radiology AI workflow market entry using provider-density, reimbursement, FDA device-event, and clinical-trial signals. This manuscript describes the architecture, evidence model, claim boundaries, and temporal transformer design. The current version should be interpreted as a systems and product-engineering prototype rather than a clinical tool or validated medical device.

## 1. Introduction

Public healthcare datasets contain signals relevant to market access, safety surveillance, reimbursement planning, and innovation strategy. However, these sources are distributed across provider registries, reimbursement files, adverse-event repositories, clinical-trial registries, open payments, and breach portals. HealthIntel OS explores whether a browser-native, no-PHI architecture can turn these public sources into auditable executive dossiers.

## 2. System Overview

The system is organized around a local-first SaaS surface, static intelligence artifacts, Cloudflare Worker endpoints, evidence drawers, and a model-lab page. The product is intentionally bounded: it supports strategic screening and evidence review, not clinical decision support or patient-level prediction.

## 3. Data and Evidence Contract

Every score must map to an evidence object containing a claim, source name, freshness indicator, and row count. The evidence contract prevents unsupported dashboard claims and provides a review path for public-data caveats.

## 4. Flagship Use Case

The first vertical evaluates whether a radiology AI workflow vendor should explore market entry in Texas. The dossier combines provider density, reimbursement momentum, FDA device-event acceleration, and clinical-trial or innovation signals. The output is an evidence-backed recommendation with explicit limitations.

## 5. Temporal Intelligence Layer

The Model Lab documents a temporal transformer design for aggregate healthcare signal sequences. Signal tokens include utilization volume, Medicare payment, price spread, FDA event rate, trial density, breach history, provider density, and AI-device activity. Baselines must be evaluated before any claim of transformer improvement.

## 6. Claim Boundary

HealthIntel OS is not a medical device, diagnostic system, clinical decision support tool, HIPAA certification, or production EHR integration. It is a public-data intelligence prototype for portfolio, architecture, and strategy demonstration.

## 7. Limitations

The current MVP uses demonstration artifacts and deterministic scoring. Public adverse-event data are subject to reporting bias. Reimbursement and provider datasets may lag reality. Model-layer claims require future evaluation against baselines and external validation.

## 8. Conclusion

Pokala HealthIntel OS demonstrates a practical architecture for browser-native public healthcare intelligence with evidence lineage and model-governance controls. The next phase is replacing demonstration marts with reproducible public-data refresh jobs, adding baseline/transformer evaluation, and exporting deterministic executive dossiers.


## Data certification note

The current repository release uses public-source demo summary marts and a claim-linked evidence ledger. The claim-linked evidence count is verified against the static intelligence artifact, while raw source snapshots and deterministic source downloads remain part of the next certification stage. This distinction is intentional: the system demonstrates the architecture, evidence lineage contract, and no-PHI operating boundary without overstating raw-data certification.

