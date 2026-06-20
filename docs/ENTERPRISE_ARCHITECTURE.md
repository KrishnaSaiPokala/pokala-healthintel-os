# Pokala HealthIntel OS — Enterprise Architecture

## Positioning

Pokala HealthIntel OS is a public-source healthcare intelligence operating system for AI market-entry, safety surveillance, reimbursement strategy, and evidence-backed executive dossiers.

The product is intentionally no-login, no-PHI, public-source only, edge-deployed, evidence-gated, and reproducible by scripts and manifests.

This is not a hospital EHR product, clinical decision support product, or patient-risk prediction system.

## System thesis

Healthcare AI strategy requires combining provider supply, utilization pressure, safety-event momentum, trial activity, market context, evidence lineage, and temporal movement.

HealthIntel OS turns those public signals into a structured executive casefile.

## Runtime architecture

Public browser -> Cloudflare Worker -> D1 demo API

Offline pipelines -> ingest -> process -> feature build -> model train -> export -> static artifacts

## Frontend architecture

The public site is a recruiter/researcher-facing enterprise casefile interface, not a generic dashboard.

Primary surfaces: Command Center, Investigation Builder, Entity Graph, Safety Radar, Reimbursement Radar, Model Lab, Data Health, and Executive Brief.

Design principles: decision hierarchy before charts, evidence ledger before decorative metrics, public-data boundary always visible, compact signals over large score tiles, no fake login surface, and no unsupported clinical claims.

## Edge/API architecture

Cloudflare Worker serves static React assets, JSON API routes, and D1-backed demo data while preserving the no-PHI/no-login boundary.

Representative routes: /, /api, /api/health, /api/command-center, /api/data-health, /api/model-lab, /api/investigations, /api/entities/search, /api/signals.

## Data architecture

Data layers: data/raw for raw or bounded public-source samples, data/processed for cleaned marts, data/features for temporal matrices, and data/models for baseline and transformer artifacts.

Governance files: data/source_manifest.json, docs/DATA_LINEAGE.md, docs/CLAIM_BOUNDARY.md, docs/MODEL_CARD.md, and scripts/verify_data_lineage.py.

## Intelligence layer

Scores are public-market intelligence signals, not clinical predictions.

Core signal families: market attractiveness, safety momentum, reimbursement pressure, provider density, evidence coverage, and temporal momentum.

Every score must have evidence source, row count or sample size, freshness, caveat, and claim boundary.

## Deep learning architecture

The model track is offline and artifact-based: public marts -> temporal feature matrix -> baselines -> temporal transformer -> model card -> exported metrics -> Model Lab UI.

The site does not train models live. That is intentional enterprise architecture.

## Enterprise boundary

HealthIntel OS may claim public-source healthcare intelligence, no-PHI architecture, evidence-linked executive casefiles, reproducible model/data artifacts, temporal modeling prototype, and public-market strategy support.

HealthIntel OS must not claim clinical decision support, patient diagnosis, patient outcome prediction, HIPAA certification, production EHR integration, causal safety conclusions from passive reports, or a fully audited raw-data lake until raw-source certification is complete.

