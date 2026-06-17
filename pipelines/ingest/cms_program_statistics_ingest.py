from __future__ import annotations

import csv
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "public_api_samples"
PROC_DIR = ROOT / "data" / "processed" / "public_api_marts"
CACHE_DIR = ROOT / ".run" / "cms_program_statistics_cache"
MANIFEST = ROOT / "data" / "source_manifest.real_api_v1.json"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CMS_DATA_JSON = "https://data.cms.gov/data.json"
DATASET_TITLE = "CMS Program Statistics - Medicare Physician, Non-Physician Practitioner & Supplier"
RAW_SAMPLE = RAW_DIR / "cms_physician_supplier_utilization_sample.jsonl"
PROCESSED_MART = PROC_DIR / "cms_physician_supplier_utilization_mart.csv"
HEADERS = {"User-Agent": "Pokala-HealthIntel-OS-public-research-demo/1.0"}

SEARCH_PATTERN = re.compile(r"radiology|imaging|diagnostic|x-ray|radiography|computed tomography|magnetic resonance|ultrasound|physician|supplier|payment|utilization|allowed|submitted|service|specialty", re.I)

def get_json(url: str) -> dict[str, Any]:
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    return response.json()

def download_file(url: str, path: Path) -> None:
    with requests.get(url, headers=HEADERS, timeout=180, stream=True) as response:
        response.raise_for_status()
        with path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 512):
                if chunk:
                    f.write(chunk)

def clean_numeric(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    text = text.replace(",", "").replace("$", "").replace("%", "")
    text = text.replace("(", "-").replace(")", "")
    try:
        return float(text)
    except ValueError:
        return None

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

def find_dataset(catalog: dict[str, Any]) -> dict[str, Any]:
    for item in catalog.get("dataset", []):
        title = str(item.get("title", ""))
        if title == DATASET_TITLE:
            return item
    for item in catalog.get("dataset", []):
        title = str(item.get("title", ""))
        if "Medicare Physician" in title and "Supplier" in title and "Medicare Advantage" not in title:
            return item
    raise SystemExit("CMS Physician/Supplier dataset not found in CMS catalog")

def distribution_year(distribution: dict[str, Any]) -> int:
    text = " ".join(str(distribution.get(key, "")) for key in ["title", "temporal", "modified"])
    years = [int(value) for value in re.findall(r"20\d{2}", text)]
    return max(years) if years else 0

def select_latest_zip(dataset: dict[str, Any]) -> dict[str, Any]:
    zips = [d for d in dataset.get("distribution", []) if str(d.get("downloadURL", "")).lower().endswith(".zip")]
    if not zips:
        raise SystemExit("No ZIP distribution found for CMS Physician/Supplier dataset")
    return sorted(zips, key=distribution_year, reverse=True)[0]

def cells_from_row(row: pd.Series) -> list[str]:
    cells = []
    for value in row.tolist():
        text = str(value).strip()
        if text and text.lower() != "nan":
            cells.append(text)
    return cells

def iter_frames(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".csv":
        yield path.name, pd.read_csv(path, dtype=str, header=None).fillna("")
    elif suffix in {".xlsx", ".xls"}:
        sheets = pd.read_excel(path, sheet_name=None, dtype=str, header=None, engine="openpyxl")
        for sheet_name, df in sheets.items():
            yield f"{path.name}::{sheet_name}", df.fillna("")

def build_mart(tabular_paths: list[Path], selected_year: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_rows: list[dict[str, Any]] = []
    mart_rows: list[dict[str, Any]] = []

    for path in tabular_paths:
        for frame_name, df in iter_frames(path):
            for row_index, row in df.iterrows():
                cells = cells_from_row(row)
                if not cells:
                    continue

                topic = " | ".join(cells)[:900]
                numeric_items = []
                for col_index, value in enumerate(row.tolist()):
                    numeric = clean_numeric(value)
                    if numeric is not None:
                        numeric_items.append((col_index, numeric))

                if not numeric_items:
                    continue

                relevant = bool(SEARCH_PATTERN.search(topic))
                if not relevant and len(mart_rows) > 2500:
                    continue

                if len(raw_rows) < 900:
                    raw_rows.append({
                        "source": "CMS Program Statistics Physician Supplier",
                        "source_file": path.name,
                        "frame": frame_name,
                        "year": selected_year,
                        "row_index": int(row_index),
                        "cells": cells[:80]
                    })

                for col_index, numeric_value in numeric_items[:24]:
                    measure_name = f"{frame_name}::cell_{col_index}"
                    mart_rows.append({
                        "source": "CMS Program Statistics Physician Supplier",
                        "source_file": path.name,
                        "frame": frame_name,
                        "year": selected_year,
                        "row_index": int(row_index),
                        "topic": topic,
                        "measure_name": measure_name,
                        "numeric_value": numeric_value
                    })

                if len(mart_rows) >= 5000:
                    return raw_rows, mart_rows

    return raw_rows, mart_rows

def update_manifest(source_record: dict[str, Any]) -> None:
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        manifest = {"status": "real_public_api_ingestion_v1", "sources": []}

    manifest["sources"] = [s for s in manifest.get("sources", []) if s.get("name") != source_record["name"]]
    manifest["sources"].append(source_record)
    manifest["generated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["status"] = "real_public_api_ingestion_v1"
    manifest["boundary"] = "Bounded public-source samples for reproducible enterprise demo. Not full raw data lake yet."
    manifest["total_processed_rows"] = sum(int(s.get("rows", 0) or 0) for s in manifest.get("sources", []))
    manifest["next_steps"] = [
        "Regenerate enterprise temporal feature matrix with CMS utilization/payment pressure.",
        "Retrain baselines, GRU, and transformer against expanded feature set.",
        "Wire Model Lab run history to compare model versions.",
        "Scale source extraction beyond bounded samples."
    ]
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

def main() -> int:
    catalog = get_json(CMS_DATA_JSON)
    dataset = find_dataset(catalog)
    distribution = select_latest_zip(dataset)
    download_url = distribution["downloadURL"]
    selected_title = str(distribution.get("title", ""))
    selected_year = distribution_year(distribution)

    zip_path = CACHE_DIR / f"cms_physician_supplier_{selected_year}.zip"
    extract_dir = CACHE_DIR / f"cms_physician_supplier_{selected_year}"
    extract_dir.mkdir(parents=True, exist_ok=True)

    print(f"Selected CMS distribution: {selected_title}")
    print(f"Downloading CMS package: {zip_path}")
    download_file(download_url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    tabular_paths = sorted(list(extract_dir.rglob("*.csv")) + list(extract_dir.rglob("*.xlsx")) + list(extract_dir.rglob("*.xls")))
    print("Tabular files found:")
    for path in tabular_paths:
        print(f"- {path}")
    if not tabular_paths:
        raise SystemExit("No CSV/XLSX/XLS files found inside CMS ZIP distribution")

    raw_rows, mart_rows = build_mart(tabular_paths, selected_year)
    if not mart_rows:
        raise SystemExit("CMS source downloaded, but no numeric mart rows were produced")

    write_jsonl(RAW_SAMPLE, raw_rows)
    write_csv(PROCESSED_MART, mart_rows, ["source", "source_file", "frame", "year", "row_index", "topic", "measure_name", "numeric_value"])

    source_record = {
        "name": "CMS Program Statistics Medicare Physician Supplier utilization and payment sample",
        "source_url": CMS_DATA_JSON,
        "distribution_title": selected_title,
        "distribution_download_url": download_url,
        "raw_artifact": str(RAW_SAMPLE.relative_to(ROOT)),
        "processed_artifact": str(PROCESSED_MART.relative_to(ROOT)),
        "rows": len(mart_rows),
        "caveat": "Bounded extracted sample from CMS Program Statistics Physician/Supplier workbook; aggregate utilization/payment context, not patient-level data."
    }
    update_manifest(source_record)

    print(json.dumps(source_record, indent=2))
    print(f"Wrote {RAW_SAMPLE}")
    print(f"Wrote {PROCESSED_MART}")
    print(f"Updated {MANIFEST}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
