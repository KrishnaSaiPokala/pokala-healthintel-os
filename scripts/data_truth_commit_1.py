from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

APP_JSON = ROOT / "apps" / "web" / "src" / "data" / "intelligence.json"
PUBLIC_JSON = ROOT / "data" / "public" / "intelligence.json"
MANIFEST = ROOT / "data" / "source_manifest.json"
DATA_LINEAGE = ROOT / "docs" / "DATA_LINEAGE.md"
PAPER = ROOT / "paper" / "Pokala_HealthIntel_OS_Manuscript_Draft.md"

def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

def as_int(value: object) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0

def patch_ui_copy() -> None:
    app = ROOT / "apps" / "web" / "src" / "app" / "App.tsx"
    if app.exists():
        text = app.read_text(encoding="utf-8")
        text = text.replace("{snapshot.meta.sources} sources", "{snapshot.meta.sources} evidence sources")
        text = text.replace("{snapshot.meta.sources} public sources", "{snapshot.meta.sources} claim-linked sources")
        text = text.replace("{formatNumber(snapshot.meta.evidenceRows)} evidence rows", "{formatNumber(snapshot.meta.evidenceRows)} claim-linked rows")
        app.write_text(text, encoding="utf-8")

    cc = ROOT / "apps" / "web" / "src" / "modules" / "command-center" / "CommandCenter.tsx"
    if cc.exists():
        text = cc.read_text(encoding="utf-8")
        text = text.replace("{formatNumber(snapshot.meta.evidenceRows)} evidence rows", "{formatNumber(snapshot.meta.evidenceRows)} claim-linked rows")
        text = text.replace("{snapshot.meta.sources} public sources", "{snapshot.meta.sources} claim-linked sources")
        text = text.replace("Every executive claim links back to public-source evidence", "Every executive claim links back to claim-linked public-source evidence")
        cc.write_text(text, encoding="utf-8")

def main() -> int:
    snapshot = load_json(APP_JSON if APP_JSON.exists() else PUBLIC_JSON)

    meta = snapshot.setdefault("meta", {})
    datasets = snapshot.get("datasets", [])
    evidence = snapshot.get("evidence", [])

    dataset_rows = sum(as_int(item.get("rows")) for item in datasets)
    evidence_rows = sum(as_int(item.get("rows")) for item in evidence)
    evidence_sources = sorted({str(item.get("source", "")).strip() for item in evidence if item.get("source")})
    dataset_names = sorted({str(item.get("name", "")).strip() for item in datasets if item.get("name")})

    meta["evidenceRows"] = evidence_rows
    meta["sources"] = len(evidence_sources)
    meta["datasetMarts"] = len(dataset_names)
    meta["datasetRows"] = dataset_rows
    meta["lineageStatus"] = "claim-linked evidence rows verified against static artifact; raw-source ingestion pending"
    meta["dataCertification"] = "public-demo summary marts; raw source snapshots not yet committed"

    for path in [APP_JSON, PUBLIC_JSON]:
        if path.exists():
            write_json(path, snapshot)

    generated_at = datetime.now(timezone.utc).isoformat()

    manifest = {
        "generated_at": generated_at,
        "status": "data_truth_commit_1",
        "claim_boundary": "Public-source demo summary marts. No PHI. Raw source snapshots are not yet committed.",
        "counts": {
            "claim_linked_evidence_rows": evidence_rows,
            "claim_linked_evidence_sources": len(evidence_sources),
            "dataset_marts": len(dataset_names),
            "dataset_mart_rows": dataset_rows
        },
        "dataset_marts": [
            {
                "name": item.get("name"),
                "rows": as_int(item.get("rows")),
                "status": item.get("status", "unknown"),
                "artifact": "data/public/intelligence.json",
                "raw_snapshot_committed": False,
                "certification": "summary_mart_only",
                "caveat": "Public/open dataset summary mart; raw source snapshot and exact source URL pinning pending."
            }
            for item in datasets
        ],
        "claim_linked_evidence": [
            {
                "id": item.get("id"),
                "claim": item.get("claim"),
                "source": item.get("source"),
                "freshness": item.get("freshness"),
                "rows": as_int(item.get("rows")),
                "artifact": "apps/web/src/data/intelligence.json",
                "raw_snapshot_committed": False
            }
            for item in evidence
        ],
        "next_certification_steps": [
            "Pin official source URL or reproducible API query for each dataset.",
            "Commit raw snapshots or deterministic download scripts.",
            "Generate derived marts from raw/source snapshots.",
            "Reconcile D1 data_health counts against static intelligence JSON.",
            "Train/evaluate temporal baselines and transformer on reproducible feature sequences."
        ]
    }

    write_json(MANIFEST, manifest)

    DATA_LINEAGE.write_text(f"""# Data Lineage

## Current certification status

This repository currently exposes a public HealthIntel OS demo using static intelligence artifacts and Cloudflare D1 summary tables.

The current lineaged counts are:

- Claim-linked evidence rows: **{evidence_rows:,}**
- Claim-linked evidence sources: **{len(evidence_sources)}**
- Dataset marts represented in the static artifact: **{len(dataset_names)}**
- Dataset mart rows represented in the static artifact: **{dataset_rows:,}**

## Important boundary

These are **public-source demo summary marts**, not a final certified raw-data lake.

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
""", encoding="utf-8")

    if PAPER.exists():
        paper_text = PAPER.read_text(encoding="utf-8")
        note = """

## Data certification note

The current repository release uses public-source demo summary marts and a claim-linked evidence ledger. The claim-linked evidence count is verified against the static intelligence artifact, while raw source snapshots and deterministic source downloads remain part of the next certification stage. This distinction is intentional: the system demonstrates the architecture, evidence lineage contract, and no-PHI operating boundary without overstating raw-data certification.
"""
        if "## Data certification note" not in paper_text:
            PAPER.write_text(paper_text.rstrip() + "\n" + note + "\n", encoding="utf-8")

    patch_ui_copy()

    print("Data truth patch complete.")
    print(f"claim_linked_evidence_rows={evidence_rows}")
    print(f"claim_linked_evidence_sources={len(evidence_sources)}")
    print(f"dataset_mart_rows={dataset_rows}")
    print(f"dataset_marts={len(dataset_names)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
