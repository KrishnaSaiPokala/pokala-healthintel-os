from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / 'data' / 'processed' / 'public_api_marts'
OUT_DIR = ROOT / 'data' / 'features'
OUT_DIR.mkdir(parents=True, exist_ok=True)

NPPES = PROC / 'nppes_tx_radiology_provider_mart.csv'
TRIALS = PROC / 'clinicaltrials_radiology_ai_mart.csv'
EVENTS = PROC / 'openfda_device_imaging_event_mart.csv'

OUT_CSV = OUT_DIR / 'enterprise_temporal_sequences.csv'
OUT_MANIFEST = OUT_DIR / 'enterprise_temporal_manifest.json'

def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f'Missing required mart: {path}')

def minmax(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors='coerce').fillna(0.0)
    lo = float(series.min())
    hi = float(series.max())
    if hi - lo < 1e-9:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - lo) / (hi - lo)

def parse_openfda_date(value):
    text = str(value or '').strip()
    if len(text) == 8 and text.isdigit():
        return pd.to_datetime(text, format='%Y%m%d', errors='coerce')
    return pd.to_datetime(text, errors='coerce')

def main() -> int:
    for path in [NPPES, TRIALS, EVENTS]:
        require(path)

    providers = pd.read_csv(NPPES)
    trials = pd.read_csv(TRIALS)
    events = pd.read_csv(EVENTS)

    providers['city'] = providers.get('city', '').fillna('UNKNOWN').astype(str).str.upper().str.strip()
    providers = providers[providers['city'].ne('') & providers['city'].ne('UNKNOWN')].copy()
    city_counts = providers.groupby('city').size().sort_values(ascending=False).head(12)
    if city_counts.empty:
        raise SystemExit('No usable provider city counts found in NPPES mart.')

    cities = city_counts.index.tolist()
    provider_total = float(city_counts.sum())
    provider_share = city_counts / provider_total

    trials['parsed_date'] = pd.to_datetime(trials.get('start_date', ''), errors='coerce')
    events['parsed_date'] = events.get('date_received', '').apply(parse_openfda_date)

    trial_months = trials.dropna(subset=['parsed_date']).copy()
    event_months = events.dropna(subset=['parsed_date']).copy()
    trial_months['period'] = trial_months['parsed_date'].dt.to_period('M').dt.to_timestamp()
    event_months['period'] = event_months['parsed_date'].dt.to_period('M').dt.to_timestamp()

    valid_periods = []
    if not trial_months.empty:
        valid_periods.append(trial_months['period'])
    if not event_months.empty:
        valid_periods.append(event_months['period'])
    if not valid_periods:
        raise SystemExit('No usable dates found in trial or device-event marts.')

    all_periods = pd.concat(valid_periods)
    start = all_periods.min()
    end = all_periods.max()
    months = pd.date_range(start=start, end=end, freq='MS')
    if len(months) < 12:
        months = pd.date_range(end=end, periods=24, freq='MS')

    trial_counts = trial_months.groupby('period').size().reindex(months, fill_value=0).astype(float)
    event_counts = event_months.groupby('period').size().reindex(months, fill_value=0).astype(float)

    rows = []
    for city in cities:
        pc = float(city_counts.loc[city])
        share = float(provider_share.loc[city])
        for period in months:
            rows.append({
                'entity_id': f"TX_RADIOLOGY_{city.replace(' ', '_')}",
                'region': 'TX',
                'specialty': 'Radiology',
                'city': city,
                'period': period.strftime('%Y-%m-%d'),
                'provider_count': pc,
                'provider_share': share,
                'trial_starts_month': float(trial_counts.loc[period]) * share,
                'device_events_month': float(event_counts.loc[period]) * share,
            })

    df = pd.DataFrame(rows)
    df['period_dt'] = pd.to_datetime(df['period'])
    df = df.sort_values(['entity_id', 'period_dt']).reset_index(drop=True)

    df['trial_starts_3mo'] = df.groupby('entity_id')['trial_starts_month'].transform(lambda x: x.rolling(3, min_periods=1).sum())
    df['trial_starts_6mo'] = df.groupby('entity_id')['trial_starts_month'].transform(lambda x: x.rolling(6, min_periods=1).sum())
    df['device_events_3mo'] = df.groupby('entity_id')['device_events_month'].transform(lambda x: x.rolling(3, min_periods=1).sum())
    df['device_events_6mo'] = df.groupby('entity_id')['device_events_month'].transform(lambda x: x.rolling(6, min_periods=1).sum())
    df['trial_velocity'] = df.groupby('entity_id')['trial_starts_3mo'].diff().fillna(0.0)
    df['safety_velocity'] = df.groupby('entity_id')['device_events_3mo'].diff().fillna(0.0)

    df['provider_density_norm'] = minmax(df['provider_count'])
    df['trial_momentum_norm'] = minmax(df['trial_starts_6mo'] + df['trial_velocity'].clip(lower=0))
    df['safety_pressure_norm'] = minmax(df['device_events_6mo'] + df['safety_velocity'].clip(lower=0))
    df['reimbursement_proxy_norm'] = minmax((df['provider_share'] * 0.65) + (df['trial_starts_6mo'] * 0.35))

    df['market_signal'] = (0.45 * df['provider_density_norm']) + (0.35 * df['trial_momentum_norm']) + (0.20 * df['reimbursement_proxy_norm'])
    df['safety_signal'] = df['safety_pressure_norm']
    df['composite_opportunity'] = (0.70 * df['market_signal']) - (0.30 * df['safety_signal'])
    df['target_next_composite_opportunity'] = df.groupby('entity_id')['composite_opportunity'].shift(-1)
    df = df.dropna(subset=['target_next_composite_opportunity']).copy()

    keep = [
        'entity_id', 'region', 'specialty', 'city', 'period',
        'provider_count', 'provider_share',
        'trial_starts_month', 'trial_starts_3mo', 'trial_starts_6mo', 'trial_velocity',
        'device_events_month', 'device_events_3mo', 'device_events_6mo', 'safety_velocity',
        'provider_density_norm', 'trial_momentum_norm', 'safety_pressure_norm', 'reimbursement_proxy_norm',
        'market_signal', 'safety_signal', 'composite_opportunity', 'target_next_composite_opportunity'
    ]
    df[keep].to_csv(OUT_CSV, index=False)

    manifest = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'enterprise_temporal_matrix_v1',
        'boundary': 'Feature matrix derived from bounded real public API marts. Suitable for enterprise demo modeling, not final paper-scale claims.',
        'input_marts': [str(NPPES.relative_to(ROOT)), str(TRIALS.relative_to(ROOT)), str(EVENTS.relative_to(ROOT))],
        'output': str(OUT_CSV.relative_to(ROOT)),
        'rows': int(len(df)),
        'entities': int(df['entity_id'].nunique()),
        'periods': int(df['period'].nunique()),
        'feature_columns': [c for c in keep if c not in ['entity_id', 'region', 'specialty', 'city', 'period', 'target_next_composite_opportunity']],
        'target': 'target_next_composite_opportunity',
        'source_boundary': 'NPPES provider rows are static supply signals; trial and event rows provide temporal movement; passive safety reports cannot establish causality or incidence.'
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

    print(json.dumps(manifest, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
