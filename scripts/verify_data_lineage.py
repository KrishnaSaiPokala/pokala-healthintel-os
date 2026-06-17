from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_JSON = ROOT / "apps" / "web" / "src" / "data" / "intelligence.json"
MANIFEST = ROOT / "data" / "source_manifest.json"

def as_int(value: object) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0

def main() -> int:
    snapshot = json.loads(APP_JSON.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    meta = snapshot.get("meta", {})
    datasets = snapshot.get("datasets", [])
    evidence = snapshot.get("evidence", [])

    evidence_rows = sum(as_int(item.get("rows")) for item in evidence)
    evidence_sources = len({item.get("source") for item in evidence if item.get("source")})
    dataset_rows = sum(as_int(item.get("rows")) for item in datasets)
    dataset_marts = len({item.get("name") for item in datasets if item.get("name")})

    errors: list[str] = []

    if as_int(meta.get("evidenceRows")) != evidence_rows:
        errors.append(f"meta.evidenceRows={meta.get('evidenceRows')} does not match evidence sum={evidence_rows}")

    if as_int(meta.get("sources")) != evidence_sources:
        errors.append(f"meta.sources={meta.get('sources')} does not match distinct evidence sources={evidence_sources}")

    counts = manifest.get("counts", {})
    if as_int(counts.get("claim_linked_evidence_rows")) != evidence_rows:
        errors.append("manifest claim_linked_evidence_rows mismatch")

    if as_int(counts.get("dataset_mart_rows")) != dataset_rows:
        errors.append("manifest dataset_mart_rows mismatch")

    if as_int(counts.get("dataset_marts")) != dataset_marts:
        errors.append("manifest dataset_marts mismatch")

    if errors:
        print("Data lineage verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Data lineage verification passed.")
    print(f"- claim-linked evidence rows: {evidence_rows:,}")
    print(f"- claim-linked evidence sources: {evidence_sources}")
    print(f"- dataset mart rows: {dataset_rows:,}")
    print(f"- dataset marts: {dataset_marts}")
    print("- raw source certification: pending")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
