# Overnight Build Plan

## Terminal 1

```bash
python scripts/overnight_run.py --profile demo --hours 8 --max-stage-seconds 1800
```

For a fast local proof:

```bash
python scripts/overnight_run.py --profile demo --max-stage-seconds 4
```

## Terminal 2

```bash
python scripts/monitor.py
```

## Morning checklist

1. Open `.run/run.log`.
2. Confirm `apps/web/src/data/intelligence.json` refreshed.
3. Run the app.
4. Inspect Command Center, Model Lab, Data Health, and Executive Brief.
5. Commit and push.
6. Configure Pages deployment.

## Scope discipline

First launch focuses on AI Radiology Market + Safety Intelligence. Do not expand until this workflow feels complete.

