param(
  [string]$ProjectRoot = "C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os"
)

Write-Host "== Pokala HealthIntel OS :: Cloudflare MVP setup ==" -ForegroundColor Cyan
Set-Location $ProjectRoot

if (!(Test-Path ".\apps\worker\package.json")) { throw "apps\worker\package.json not found. Did you unzip the Cloudflare MVP overlay?" }
if (!(Get-Command node -ErrorAction SilentlyContinue)) { throw "Node.js not found. Install Node.js LTS first." }
if (!(Get-Command npm -ErrorAction SilentlyContinue)) { throw "npm not found. Install Node.js LTS first." }

Write-Host "Installing Worker dependencies..." -ForegroundColor Cyan
Set-Location "$ProjectRoot\apps\worker"
npm install

Write-Host "`nLogin to Cloudflare when browser opens..." -ForegroundColor Yellow
npx wrangler login

Write-Host "`nCreate D1 database if needed:" -ForegroundColor Cyan
Write-Host "  npx wrangler d1 create pokala-healthintel-os-db" -ForegroundColor White
Write-Host "Copy the database_id into apps\worker\wrangler.toml, replacing REPLACE_WITH_D1_DATABASE_ID." -ForegroundColor Yellow
Write-Host "Then run:" -ForegroundColor Cyan
Write-Host "  npx wrangler d1 execute pokala-healthintel-os-db --remote --file=./migrations/0001_init.sql" -ForegroundColor White
Write-Host "  npx wrangler d1 execute pokala-healthintel-os-db --remote --file=../../data/public/d1_seed.sql" -ForegroundColor White
Write-Host "  npx wrangler deploy" -ForegroundColor White
