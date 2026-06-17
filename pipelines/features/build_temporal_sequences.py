from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "apps" / "web" / "src" / "data" / "intelligence.json"
OUT_DIR = ROOT / "data" / "features"
OUT_CSV = OUT_DIR / "temporal_market_sequences.csv"
OUT_JSON = OUT_DIR / "temporal_feature_manifest.json"

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    snap = json.loads(SRC.read_text(encoding="utf-8"))

    temporal = snap.get("temporal", [])
    scores = snap.get("scores", {})
    datasets = snap.get("datasets", [])
    evidence = snap.get("evidence", [])

    dataset_rows = sum(int(d.get("rows", 0) or 0) for d in datasets)
    evidence_rows = sum(int(e.get("rows", 0) or 0) for e in evidence)

    rows = []
    for idx, point in enumerate(temporal):
        market = float(point.get("market", 0))
        safety = float(point.get("safety", 0))
        reimbursement = float(point.get("reimbursement", 0))

        rows.append({
            "case_id": "tx_radiology_ai_workflow",
            "region": "Texas",
            "specialty": "Radiology",
            "period": point.get("period", f"t{idx}"),
            "t": idx,
            "market": market,
            "safety": safety,
            "reimbursement": reimbursement,
            "provider_density": float(scores.get("providerDensity", 0)),
            "dataset_rows_log": dataset_rows,
            "evidence_rows_log": evidence_rows,
            "market_delta": market - float(temporal[idx - 1].get("market", market)) if idx else 0.0,
            "safety_delta": safety - float(temporal[idx - 1].get("safety", safety)) if idx else 0.0,
            "reimbursement_delta": reimbursement - float(temporal[idx - 1].get("reimbursement", reimbursement)) if idx else 0.0,
            "target_next_market": float(temporal[idx + 1].get("market", market)) if idx + 1 < len(temporal) else market,
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)

    manifest = {
        "artifact": str(OUT_CSV.relative_to(ROOT)),
        "rows": len(df),
        "case_id": "tx_radiology_ai_workflow",
        "status": "prototype_temporal_sequence",
        "boundary": "Feature sequence currently derived from static public-demo intelligence artifact. Real raw-source generated sequences are next.",
        "features": [c for c in df.columns if c not in {"target_next_market"}],
        "target": "target_next_market"
    }

    OUT_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CSV}")
    print(f"rows={len(df)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
