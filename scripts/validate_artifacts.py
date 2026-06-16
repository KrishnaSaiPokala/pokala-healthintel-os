from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "apps/web/src/app/App.tsx",
    "apps/web/src/types/intelligence.ts",
    "apps/web/src/lib/evidence.ts",
    "apps/web/src/lib/scoring.ts",
    "apps/web/src/modules/command-center/CommandCenter.tsx",
    "apps/web/src/modules/investigations/Investigations.tsx",
    "apps/web/src/modules/model-lab/ModelLab.tsx",
    "apps/web/src/modules/data-health/DataHealth.tsx",
    "docs/CLAIM_BOUNDARY.md",
    "docs/DATA_LINEAGE.md",
    "docs/MODEL_CARD.md",
    "paper/Pokala_HealthIntel_OS_Manuscript_Draft.md",
]

INTELLIGENCE_JSON = ROOT / "apps" / "web" / "src" / "data" / "intelligence.json"


def run(command: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return proc.returncode, (proc.stdout + proc.stderr)


def validate_files() -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")
    return errors


def validate_intelligence_json() -> list[str]:
    errors: list[str] = []
    if not INTELLIGENCE_JSON.exists():
        return ["missing intelligence.json"]

    data = json.loads(INTELLIGENCE_JSON.read_text(encoding="utf-8"))
    required_keys = {"meta", "scores", "temporal", "radar", "graph", "datasets", "evidence"}
    missing = sorted(required_keys - set(data))
    if missing:
        errors.append(f"intelligence.json missing keys: {missing}")

    if not data.get("evidence"):
        errors.append("intelligence.json evidence list is empty")
    if not data.get("datasets"):
        errors.append("intelligence.json datasets list is empty")
    return errors


def main() -> int:
    errors = validate_files() + validate_intelligence_json()

    web_code, web_output = run(["npm.cmd" if sys.platform.startswith("win") else "npm", "run", "build"], ROOT / "apps" / "web")
    if web_code != 0:
        errors.append("web build failed\n" + web_output[-3000:])

    worker_code, worker_output = run(["npm.cmd" if sys.platform.startswith("win") else "npm", "run", "typecheck"], ROOT / "apps" / "worker")
    if worker_code != 0:
        errors.append("worker typecheck failed\n" + worker_output[-3000:])

    if errors:
        print("Artifact validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Artifact validation passed: web build, worker typecheck, modular files, and intelligence JSON are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
