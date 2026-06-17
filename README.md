# Pokala HealthIntel OS

**Browser-native healthcare intelligence SaaS for market strategy, reimbursement, safety, provider networks, and temporal AI-risk signals.**

Built to look and behave like a serious HealthTech intelligence product, not a static portfolio. The architecture is free-first: public datasets, offline pipelines, curated Parquet/JSON intelligence marts, browser compute, IndexedDB workspaces, and optional local temporal-transformer modeling.

## What this repo gives you

- Elite SaaS-style React/Vite app shell
- Command Center, Investigations, Entity Graph, Safety Radar, Reimbursement Radar, Model Lab, Data Health
- CPU-first overnight pipeline with progress monitor
- Public-data ingestion hooks for NPPES, openFDA, ClinicalTrials.gov, CMS-style summaries, Open Payments-style summaries, CDC/OCR placeholders
- Temporal Transformer skeleton for sequence-based healthcare risk/momentum modeling
- Deterministic scoring engine so the app works before deep learning is trained
- Static hosting deployment workflows for GitHub Pages / Cloudflare Pages style deployment

## The flagship thesis

> Pokala HealthIntel OS converts fragmented public healthcare data into evidence-backed intelligence dossiers. It connects providers, regions, specialties, FDA safety signals, Medicare utilization, clinical trials, payments, pricing, and breach exposure, then scores market opportunity and risk over time.

## Zero-cost constraints

- No PHI
- No paid APIs
- No permission-gated data
- No hosted database bill
- No required LLM API
- No server required for MVP
- Runs locally and deploys as a static app

## First vertical

**AI Radiology Market + Safety Intelligence**

Initial demo question:

> Should an AI imaging workflow company enter the Texas radiology market?

The app shows opportunity, reimbursement, provider density, FDA safety trend, trial activity, breach exposure, evidence lineage, and a generated executive memo.

## Overnight run

Terminal 1:

```bash
python scripts/overnight_run.py --profile demo --hours 8
```

Terminal 2:

```bash
python scripts/monitor.py
```

The runner writes:

- `.run/progress.json`
- `.run/run.log`
- `apps/web/src/data/intelligence.json`
- `data/public/*.json`

## Local web app

```bash
cd apps/web
npm install
npm run dev
```

Then open the printed local URL.

## Production-style build

```bash
cd apps/web
npm run build
```

The static app builds into `apps/web/dist`.

## Recommended GitHub push

```bash
mkdir pokala-healthintel-os
cd pokala-healthintel-os
unzip ../pokala-healthintel-os.zip

git init
git branch -M main
git add .
git commit -m "Launch Pokala HealthIntel OS SaaS scaffold"
git remote add origin https://github.com/KrishnaSaiPokala/pokala-healthintel-os.git
git push -u origin main
```

## Important note

The connected GitHub account in this chat did not have write access to `KrishnaSaiPokala`, so this package is built for you to push from your terminal using your own GitHub credentials.

## Cloudflare Workers SaaS MVP Path

This repo now includes a Cloudflare Worker backend in `apps/worker` and a D1 schema/seed flow. Use this when the product needs to feel like a real hosted SaaS, not a static portfolio page.

Full-power artifact build:

```powershell
python .\scripts\fullpower_run.py --max-stage-seconds 20
```

Worker deploy guide:

```text
docs/CLOUDFLARE_MVP_DEPLOY.md
```

The intended free MVP URL is:

```text
https://pokala-healthintel-os.<your-cloudflare-subdomain>.workers.dev
```


## Architecture and governance docs

- [Enterprise Architecture](docs/ENTERPRISE_ARCHITECTURE.md)
- [Deep Learning System Design](docs/DL_SYSTEM_DESIGN.md)
- [System Status](docs/SYSTEM_STATUS.md)
- [Roadmap](docs/ROADMAP.md)
- [Data Lineage](docs/DATA_LINEAGE.md)
- [Claim Boundary](docs/CLAIM_BOUNDARY.md)
- [Model Card](docs/MODEL_CARD.md)

