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
SEARCH_PATTERN = re.compile(r"radiology|imaging|diagnostic|x-ray|radiography|computed tomography|magnetic resonance|ultrasound", re.I)

def get_json(url: str) -> dict[str, Any]:
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    return response.json()

def download_file(url: str, path: Path) -> None:
    with requests.get(url, headers=HEADERS, timeout=120, stream=True) as response:
        response.raise_for_status()
        with path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 256):
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

def read_csv_any(path: Path) -> pd.DataFrame:
    for encoding in ["utf-8", "utf-8-sig", "latin1"]:
        try:
            return pd.read_csv(path, dtype=str, encoding=encoding)
        except Exception:
            continue
    raise RuntimeError(f"Could not read CSV: {path}")

def find_dataset(catalog: dict[str, Any]) -> dict[str, Any]:
    datasets = catalog.get("dataset", [])
    for item in datasets:
        title = str(item.get("title", ""))
        if title == DATASET_TITLE:
            return item
    for item in datasets:
        title = str(item.get("title", ""))
        if "Medicare Physician" in title and "Supplier" in title and "Medicare Advantage" not in title:
            return item
    raise SystemExit("CMS Physician/Supplier dataset not found in CMS data.json")

def distribution_year(distribution: dict[str, Any]) -> int:
    text = " ".join(str(distribution.get(key, "")) for key in ["title", "temporal", "modified", "downloadURL"])
    years = [int(value) for value in re.findall(r"20\d{2}", text)]
    return max(years) if years else 0

def select_latest_zip(dataset: dict[str, Any]) -> dict[str, Any]:
    distributions = dataset.get("distribution", [])
    zip_distributions = [d for d in distributions if str(d.get("downloadURL", "")).lower().endswith(".zip")]
    if not zip_distributions:
        raise SystemExit("No ZIP distributions found for CMS Physician/Supplier dataset")
    return sorted(zip_distributions, key=distribution_year, reverse=True)[0]

def build_mart_from_csvs(csv_paths: list[Path], selected_year: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_rows = []
    mart_rows = []

    for csv_path in csv_paths:
        try:
            df = read_csv_any(csv_path)
        except Exception:
            continue
        if df.empty:
            continue

        df = df.fillna("")
        text_blob = df.astype(str).agg(" | ".join, axis=1)
        mask = text_blob.str.contains(SEARCH_PATTERN, regex=True, na=False)
        subset = df[mask].copy()
        if subset.empty:
            subset = df.head(150).copy()
        else:
            subset = subset.head(500).copy()

        for row_idx, row in subset.iterrows():
            row_dict = {str(k): str(v) for k, v in row.to_dict().items()}
            raw_rows.append({
                "source": "CMS Program Statistics Physician Supplier",
                "source_file": csv_path.name,
                "year": selected_year,
                "row": row_dict
            })

            numeric_items = []
            text_items = []
            for column, value in row_dict.items():
                numeric = clean_numeric(value)
                if numeric is None:
                    if value and len(text_items) < 8:
                        text_items.append(f"{column}: {value}")
                else:
                    numeric_items.append((column, numeric))

            topic = " | ".join(text_items)[:900]
            for metric_name, numeric_value in numeric_items[:20]:
                lower_metric = metric_name.lower()
                if any(term in lower_metric for term in ["year", "age", "percent"]) and "payment" not in lower_metric and "util" not in lower_metric:
                    continue
                mart_rows.append({
                    "source": "CMS Program Statistics Physician Supplier",
                    "source_file": csv_path.name,
                    "year": selected_year,
                    "topic": topic,
                    "measure_name": metric_name,
                    "numeric_value": numeric_value
                })

            if len(raw_rows) >= 600 and len(mart_rows) >= 2500:
                break

        if len(raw_rows) >= 600 and len(mart_rows) >= 2500:
            break

    return raw_rows[:600], mart_rows[:3000]

def update_manifest(source_record: dict[str, Any]) -> None:
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "real_public_api_ingestion_v1",
            "boundary": "Bounded public API samples for reproducible enterprise demo. Not full raw data lake yet.",
            "sources": []
        }

    manifest["sources"] = [s for s in manifest.get("sources", []) if s.get("name") != source_record["name"]]
    manifest["sources"].append(source_record)
    manifest["generated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["total_processed_rows"] = sum(int(s.get("rows", 0) or 0) for s in manifest.get("sources", []))
    manifest["next_steps"] = [
        "Regenerate enterprise temporal feature matrix with CMS utilization/payment pressure.",
        "Retrain baselines, GRU, and transformer against expanded feature set.",
        "Wire Model Lab run history to compare model versions.",
        "Add larger paginated/full-source extraction where source licensing and file size allow."
    ]
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

def main() -> int:
    catalog = get_json(CMS_DATA_JSON)
    dataset = find_dataset(catalog)
    distribution = select_latest_zip(dataset)
    download_url = distribution["downloadURL"]
    selected_year = distribution_year(distribution)
    selected_title = str(distribution.get("title", ""))

    zip_path = CACHE_DIR / f"cms_physician_supplier_{selected_year}.zip"
    extract_dir = CACHE_DIR / f"cms_physician_supplier_{selected_year}"
    extract_dir.mkdir(parents=True, exist_ok=True)

    print(f"Selected CMS distribution: {selected_title}")
    print(f"Downloading bounded source package to cache: {zip_path}")
    download_file(download_url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    csv_paths = sorted(extract_dir.rglob("*.csv"))
    if not csv_paths:
        raise SystemExit("No CSV files found inside CMS ZIP distribution")

    raw_rows, mart_rows = build_mart_from_csvs(csv_paths, selected_year)
    if not mart_rows:
        raise SystemExit("CMS source downloaded, but no numeric mart rows were produced")

    write_jsonl(RAW_SAMPLE, raw_rows)
    write_csv(PROCESSED_MART, mart_rows, ["source", "source_file", "year", "topic", "measure_name", "numeric_value"])

    source_record = {
        "name": "CMS Program Statistics Medicare Physician Supplier utilization and payment sample",
        "source_url": CMS_DATA_JSON,
        "distribution_title": selected_title,
        "distribution_download_url": download_url,
        "raw_artifact": str(RAW_SAMPLE.relative_to(ROOT)),
        "processed_artifact": str(PROCESSED_MART.relative_to(ROOT)),
        "rows": len(mart_rows),
        "caveat": "Bounded extracted sample from CMS Program Statistics Physician/Supplier ZIP distribution; aggregate utilization/payment context, not provider-level claims."
    }
    update_manifest(source_record)

    print(json.dumps(source_record, indent=2))
    print(f"Wrote {RAW_SAMPLE}")
    print(f"Wrote {PROCESSED_MART}")
    print(f"Updated {MANIFEST}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
