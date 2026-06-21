# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import time
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / ".run" / "progress.json"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def read_progress():
    for _ in range(5):
        try:
            raw = PROGRESS.read_text(encoding="utf-8", errors="ignore").strip()
            if raw:
                return json.loads(raw)
        except Exception:
            time.sleep(0.2)
    return None

def pick(d, *names, default=""):
    for name in names:
        if isinstance(d, dict) and name in d and d[name] not in (None, ""):
            return d[name]
    return default

def main():
    print("Pokala HealthIntel OS safe monitor")
    time.sleep(1)

    while True:
        p = read_progress()
        clear()
        print("POKALA HEALTHINTEL OS - OVERNIGHT RUN")
        print("=" * 72)
        print("Live site: https://pokala-healthintel-os.krishnasaipokala.workers.dev")
        print("Repo     :", ROOT)
        print("-" * 72)

        if not p:
            print("Progress file is mid-write or unavailable. Retrying...")
            time.sleep(5)
            continue

        status = pick(p, "status", default="running")
        stage_index = pick(p, "stage_index", "stage", "current_stage", default="?")
        stage_total = pick(p, "stage_total", "total_stages", default="9")
        stage_name = pick(p, "stage_name", "current_stage_name", "name", default="")
        percent = pick(p, "overall_percent", "percent", "progress_percent", default="")
        updated = pick(p, "updated_at", "updated", default="")

        print("Status  :", status)
        print("Stage   :", str(stage_index) + "/" + str(stage_total), "-", stage_name)
        print("Overall :", str(percent) + "%")
        print("Updated :", updated)
        print("-" * 72)

        print("Raw progress keys:")
        print(", ".join(sorted([str(k) for k in p.keys()])))
        print("-" * 72)

        recent = pick(p, "recent_log", "recent_logs", "log_tail", default=[])
        print("Recent log:")
        if isinstance(recent, list):
            for line in recent[-10:]:
                print("  " + str(line))
        elif recent:
            print(str(recent))
        else:
            print("  No embedded recent log. This is okay if progress is updating.")

        print("=" * 72)
        print("Ctrl+C stops this monitor only. Do not touch Terminal 1.")
        time.sleep(5)

if __name__ == "__main__":
    main()
