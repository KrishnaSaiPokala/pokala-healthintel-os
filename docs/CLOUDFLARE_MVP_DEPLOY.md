# Pokala HealthIntel OS â€” Cloudflare Workers SaaS MVP Deploy

This deployment is not GitHub Pages. GitHub is only code storage.

Production surface:

```text
https://pokala-healthintel-os.<your-cloudflare-subdomain>.workers.dev
```

## 1. Build full-power local artifacts

From repo root:

```powershell
.\.venv\Scripts\activate
python .\scripts\fullpower_run.py --max-stage-seconds 20
```

This generates:

```text
apps/web/src/data/intelligence.json
data/public/temporal_transformer_result.json
data/public/d1_seed.sql
```

## 2. Install Worker dependencies

```powershell
cd .\apps\worker
npm install
npx wrangler login
```

## 3. Create Cloudflare D1 database

```powershell
npx wrangler d1 create pokala-healthintel-os-db
```

Copy the returned `database_id` into `apps/worker/wrangler.toml`.

## 4. Create schema and seed data

```powershell
npx wrangler d1 execute pokala-healthintel-os-db --remote --file=.\migrations\0001_init.sql
npx wrangler d1 execute pokala-healthintel-os-db --remote --file=..\..\data\public\d1_seed.sql
```

## 5. Deploy Worker API

```powershell
npx wrangler deploy
```

Expected URL:

```text
https://pokala-healthintel-os.<your-cloudflare-subdomain>.workers.dev
```

Check:

```text
/api/health
/api/command-center
/api/investigations
/api/model-lab
/api/data-health
```

## 6. Frontend routing plan

Phase A: Worker API live, local frontend points to it:

```powershell
cd ..\web
$env:VITE_API_BASE="https://pokala-healthintel-os.<your-cloudflare-subdomain>.workers.dev"
npm install
npm run dev
```

Phase B: Worker serves frontend assets too. This is the next upgrade after the API smoke check.

## Philosophy

Cloudflare Worker is the SaaS backend.
D1 is the product database.
Your laptop remains the overnight intelligence factory.

