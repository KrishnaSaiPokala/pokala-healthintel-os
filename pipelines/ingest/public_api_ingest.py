from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "public_api_samples"
PROC_DIR = ROOT / "data" / "processed" / "public_api_marts"
MANIFEST = ROOT / "data" / "source_manifest.real_api_v1.json"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Pokala-HealthIntel-OS-public-research-demo/1.0"
}

def get_json(url: str, params: dict[str, Any] | None = None, timeout: int = 45) -> dict[str, Any]:
    response = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.json()

def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

def ingest_nppes_texas_radiology(limit: int = 200) -> dict[str, Any]:
    # NPPES API returns provider search results. We keep this bounded for repo-safe reproducibility.
    url = "https://npiregistry.cms.hhs.gov/api/"
    params = {
        "version": "2.1",
        "state": "TX",
        "taxonomy_description": "Radiology",
        "limit": limit,
    }

    payload = get_json(url, params=params)
    rows = payload.get("results", []) or []

    raw_path = RAW_DIR / "nppes_tx_radiology_sample.jsonl"
    write_jsonl(raw_path, rows)

    mart = []
    for row in rows:
        basic = row.get("basic", {}) or {}
        addresses = row.get("addresses", []) or []
        taxonomies = row.get("taxonomies", []) or []
        primary_tax = next((t for t in taxonomies if t.get("primary")), taxonomies[0] if taxonomies else {})
        practice = next((a for a in addresses if a.get("address_purpose") == "LOCATION"), addresses[0] if addresses else {})

        mart.append({
            "source": "NPPES API",
            "npi": row.get("number", ""),
            "entity_type": row.get("enumeration_type", ""),
            "organization_name": basic.get("organization_name", ""),
            "first_name": basic.get("first_name", ""),
            "last_name": basic.get("last_name", ""),
            "taxonomy": primary_tax.get("desc", ""),
            "city": practice.get("city", ""),
            "state": practice.get("state", ""),
            "postal_code": practice.get("postal_code", ""),
        })

    mart_path = PROC_DIR / "nppes_tx_radiology_provider_mart.csv"
    write_csv(mart_path, mart, [
        "source", "npi", "entity_type", "organization_name", "first_name",
        "last_name", "taxonomy", "city", "state", "postal_code"
    ])

    return {
        "name": "NPPES Texas Radiology API sample",
        "source_url": url + "?" + urlencode(params),
        "raw_artifact": str(raw_path.relative_to(ROOT)),
        "processed_artifact": str(mart_path.relative_to(ROOT)),
        "rows": len(rows),
        "caveat": "Bounded API sample for reproducible public demo; not full NPPES downloadable file."
    }

def ingest_clinicaltrials_radiology_ai(page_size: int = 100) -> dict[str, Any]:
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.term": "radiology artificial intelligence",
        "pageSize": page_size,
        "format": "json",
    }

    payload = get_json(url, params=params)
    studies = payload.get("studies", []) or []

    raw_path = RAW_DIR / "clinicaltrials_radiology_ai_sample.jsonl"
    write_jsonl(raw_path, studies)

    mart = []
    for study in studies:
        protocol = study.get("protocolSection", {}) or {}
        identification = protocol.get("identificationModule", {}) or {}
        status = protocol.get("statusModule", {}) or {}
        design = protocol.get("designModule", {}) or {}
        conditions = protocol.get("conditionsModule", {}) or {}

        mart.append({
            "source": "ClinicalTrials.gov API",
            "nct_id": identification.get("nctId", ""),
            "brief_title": identification.get("briefTitle", ""),
            "overall_status": status.get("overallStatus", ""),
            "start_date": (status.get("startDateStruct", {}) or {}).get("date", ""),
            "study_type": design.get("studyType", ""),
            "conditions": "; ".join(conditions.get("conditions", []) or []),
        })

    mart_path = PROC_DIR / "clinicaltrials_radiology_ai_mart.csv"
    write_csv(mart_path, mart, [
        "source", "nct_id", "brief_title", "overall_status", "start_date", "study_type", "conditions"
    ])

    return {
        "name": "ClinicalTrials.gov radiology AI API sample",
        "source_url": url + "?" + urlencode(params),
        "raw_artifact": str(raw_path.relative_to(ROOT)),
        "processed_artifact": str(mart_path.relative_to(ROOT)),
        "rows": len(studies),
        "caveat": "Bounded API sample for innovation/activity signal; trial registry data is not market adoption proof."
    }

def ingest_openfda_device_events(limit: int = 100) -> dict[str, Any]:
    url = "https://api.fda.gov/device/event.json"
    params = {
        "search": 'device.generic_name:"radiology" OR device.generic_name:"imaging" OR device.generic_name:"x-ray"',
        "limit": limit,
    }

    payload = get_json(url, params=params)
    events = payload.get("results", []) or []

    raw_path = RAW_DIR / "openfda_device_imaging_events_sample.jsonl"
    write_jsonl(raw_path, events)

    mart = []
    for event in events:
        devices = event.get("device", []) or []
        first_device = devices[0] if devices else {}
        mart.append({
            "source": "openFDA Device Event API",
            "mdr_report_key": event.get("mdr_report_key", ""),
            "event_type": event.get("event_type", ""),
            "date_received": event.get("date_received", ""),
            "report_source_code": event.get("report_source_code", ""),
            "manufacturer_name": first_device.get("manufacturer_d_name", ""),
            "generic_name": first_device.get("generic_name", ""),
            "device_class": first_device.get("device_class", ""),
        })

    mart_path = PROC_DIR / "openfda_device_imaging_event_mart.csv"
    write_csv(mart_path, mart, [
        "source", "mdr_report_key", "event_type", "date_received", "report_source_code",
        "manufacturer_name", "generic_name", "device_class"
    ])

    return {
        "name": "openFDA imaging/radiology device-event API sample",
        "source_url": url + "?" + urlencode(params),
        "raw_artifact": str(raw_path.relative_to(ROOT)),
        "processed_artifact": str(mart_path.relative_to(ROOT)),
        "rows": len(events),
        "caveat": "MAUDE/openFDA adverse-event reports are passive surveillance and cannot establish causality or incidence alone."
    }

def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()

    sources = []
    for fn in [
        ingest_nppes_texas_radiology,
        ingest_clinicaltrials_radiology_ai,
        ingest_openfda_device_events,
    ]:
        print(f">>> {fn.__name__}")
        try:
            result = fn()
            print(json.dumps(result, indent=2))
            sources.append(result)
        except Exception as exc:
            failure = {
                "name": fn.__name__,
                "status": "failed",
                "error": repr(exc),
            }
            print(json.dumps(failure, indent=2))
            sources.append(failure)
        time.sleep(0.4)

    manifest = {
        "generated_at": generated_at,
        "status": "real_public_api_ingestion_v1",
        "boundary": "Bounded public API samples for reproducible enterprise demo. Not full raw data lake yet.",
        "sources": sources,
        "total_processed_rows": sum(int(s.get("rows", 0) or 0) for s in sources if "rows" in s),
        "next_steps": [
            "Add paginated ingestion for larger source extracts.",
            "Add CMS utilization/public provider data source.",
            "Generate region-specialty-month feature marts from processed API rows.",
            "Re-train baselines and transformer on expanded real-source sequences."
        ],
    }

    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
