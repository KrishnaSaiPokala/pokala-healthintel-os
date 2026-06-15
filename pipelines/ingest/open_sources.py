"""Official-source ingestion hooks.

This file intentionally avoids broad scraping. Extend each function source-by-source.
The production pattern is: API/download -> raw snapshot -> normalized mart -> static app data.
"""
from __future__ import annotations
import json, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data' / 'raw'
RAW.mkdir(parents=True, exist_ok=True)

def fetch_json(url: str, out: Path, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent':'PokalaHealthIntelOS/0.1 public-data-research'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read().decode('utf-8')
    out.write_text(data, encoding='utf-8')
    return out

def fetch_nppes_radiology_tx(limit=200):
    query = urllib.parse.urlencode({'taxonomy_description':'Radiology','state':'TX','limit':limit,'version':'2.1'})
    return fetch_json(f'https://npiregistry.cms.hhs.gov/api/?{query}', RAW/'nppes_radiology_tx.json')

def fetch_openfda_device_events(limit=100):
    query = urllib.parse.urlencode({'search':'device.generic_name:radiology OR device.device_report_product_code:LLZ','limit':limit})
    return fetch_json(f'https://api.fda.gov/device/event.json?{query}', RAW/'openfda_device_events_radiology.json')

def fetch_clinical_trials_radiology(limit=100):
    query = urllib.parse.urlencode({'query.term':'radiology imaging artificial intelligence','pageSize':limit,'format':'json'})
    return fetch_json(f'https://clinicaltrials.gov/api/v2/studies?{query}', RAW/'clinical_trials_radiology_ai.json')

if __name__ == '__main__':
    for fn in [fetch_nppes_radiology_tx, fetch_openfda_device_events, fetch_clinical_trials_radiology]:
        try:
            print('fetching', fn.__name__)
            print(fn())
            time.sleep(1)
        except Exception as e:
            print('warning:', fn.__name__, 'failed:', e)
