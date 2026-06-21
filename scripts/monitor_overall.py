from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
DATA_PUBLIC = ROOT / "data" / "public"
WEB_DATA = ROOT / "apps" / "web" / "src" / "data" / "intelligence.json"

STAGE_RE = re.compile(r"stage\s+(\d+)\/(\d+):\s+(.+)", re.IGNORECASE)
DONE_RE = re.compile(r"run complete|artifacts are ready|Full-power", re.IGNORECASE)

def latest_log() -> Path | None:
    if not LOG_DIR.exists():
        return None
    files = sorted(LOG_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def read_lines(path: Path | None, n: int = 80) -> list[str]:
    if not path or not path.exists():
        return []
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()[-n:]
    except Exception:
        return []

def fmt_seconds(sec: float) -> str:
    sec = max(0, int(sec))
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"

def artifact_status() -> list[tuple[str, bool]]:
    targets = [
        ("D1 seed SQL", DATA_PUBLIC / "d1_seed.sql"),
        ("Temporal transformer result", DATA_PUBLIC / "temporal_transformer_result.json"),
        ("Web intelligence payload", WEB_DATA),
        ("Worker app", ROOT / "apps" / "worker" / "src" / "index.ts"),
        ("Wrangler config", ROOT / "apps" / "worker" / "wrangler.toml"),
    ]
    return [(name, path.exists()) for name, path in targets]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    started = datetime.now()
    last_stage = 0
    total_stages = 9
    stage_name = "waiting for run"
    completed = False

    while True:
        log = latest_log()
        lines = read_lines(log)

        for line in lines:
            m = STAGE_RE.search(line)
            if m:
                last_stage = int(m.group(1))
                total_stages = int(m.group(2))
                stage_name = m.group(3).strip()
            if DONE_RE.search(line):
                completed = True

        if completed:
            pct = 100.0
        elif total_stages:
            pct = min(99.0, (last_stage - 1) / total_stages * 100.0 if last_stage else 0.0)
        else:
            pct = 0.0

        elapsed = (datetime.now() - started).total_seconds()
        if pct > 2 and not completed:
            total_est = elapsed / (pct / 100.0)
            remaining = total_est - elapsed
        else:
            remaining = 0

        bar_width = 36
        filled = int(bar_width * pct / 100)
        bar = "¦" * filled + "¦" * (bar_width - filled)

        clear()
        print("POKALA HEALTHINTEL OS — OVERNIGHT RUN MONITOR")
        print("=" * 72)
        print(f"Repo: {ROOT}")
        print(f"Log : {log if log else 'no log found yet'}")
        print("-" * 72)
        print(f"Overall: [{bar}] {pct:5.1f}%")
        print(f"Stage  : {last_stage}/{total_stages} — {stage_name}")
        print(f"Elapsed: {fmt_seconds(elapsed)}")
        print(f"ETA    : {fmt_seconds(remaining) if remaining else 'calculating...'}")
        print("-" * 72)
        print("Artifacts:")
        for name, ok in artifact_status():
            print(f"  {'?' if ok else '?'} {name}")
        print("-" * 72)
        print("Latest log:")
        for line in lines[-12:]:
            print("  " + line)
        print("=" * 72)
        print("Ctrl+C exits monitor only. It does not stop the main overnight run.")

        if completed:
            print("\nRUN COMPLETE. You can close this monitor.")
            time.sleep(10)
        else:
            time.sleep(3)

if __name__ == "__main__":
    main()
