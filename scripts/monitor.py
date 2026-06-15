#!/usr/bin/env python3
from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT/'.run'/'progress.json'
LOG = ROOT/'.run'/'run.log'

def bar(pct, width=42):
    done = int(width*pct/100)
    return '█'*done + '░'*(width-done)

print('Pokala HealthIntel OS monitor — watching .run/progress.json')
while True:
    if PROGRESS.exists():
        p=json.loads(PROGRESS.read_text())
        print('\033[2J\033[H', end='')
        print('POKALA HEALTHINTEL OS — OVERNIGHT RUN')
        print('='*72)
        print(f"Status : {p['status']}")
        print(f"Stage  : {p['stage_index']}/{p['stage_count']} — {p['stage']}")
        print(f"Overall: {p['percent']:6.2f}%  [{bar(p['percent'])}]")
        print(f"Updated: {p['updated_at']}")
        print('\nRecent log:')
        if LOG.exists():
            lines=LOG.read_text(errors='ignore').splitlines()[-12:]
            for line in lines: print('  '+line)
        if p['status']=='complete': break
    else:
        print('Waiting for runner to create progress file...')
    time.sleep(1)
