# Pokala HealthIntel OS Architecture

## Product shape

A SaaS-like healthcare intelligence platform that runs without a traditional backend for the MVP.

## Runtime

- React/Vite app shell
- Local workspaces through browser storage
- Static intelligence marts loaded as JSON initially, Parquet/DuckDB-WASM in the advanced build
- No PHI, no account system, no server-side secrets

## Data platform

Official public data sources are ingested by offline Python jobs. The app reads curated marts, not giant raw datasets.

```text
Official APIs/downloads
  -> raw snapshots
  -> normalized tables
  -> entity graph
  -> temporal feature sequences
  -> deterministic scores
  -> optional temporal-transformer scores
  -> static web artifacts
```

## AI/DL layer

- Primary production MVP: deterministic evidence-backed scoring
- Advanced model lab: temporal transformer for sequence momentum/anomaly/risk direction
- Baseline: GRU/rolling z-score comparison
- Output: compact score tables, attention summaries, model cards

## Free deployment

- GitHub repo
- GitHub Actions for scheduled data refresh
- GitHub Pages or Cloudflare Pages static hosting
- Optional local GPU training on GTX 1660 Ti

