from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IS_WINDOWS = os.name == "nt"

REQUIRED = [
    "apps/web/package.json",
    "apps/web/src/main.tsx",
    "apps/worker/package.json",
    "apps/worker/src",
    "apps/worker/migrations",
    "pipelines/ingest",
    "pipelines/features",
    "pipelines/export",
    "models/baselines",
    "models/temporal_transformer",
    "scripts/fullpower_run.py",
    "scripts/overnight_run.py",
    "docs/ARCHITECTURE.md",
    "docs/DATA_SOURCES.md",
]

STAFF_GRADE_TARGETS = [
    "apps/web/src/app",
    "apps/web/src/modules",
    "apps/web/src/modules/command-center",
    "apps/web/src/modules/investigations",
    "apps/web/src/modules/model-lab",
    "apps/web/src/modules/data-health",
    "apps/web/src/modules/evidence",
    "apps/web/src/types",
    "apps/web/src/lib/evidence.ts",
    "apps/web/src/lib/scoring.ts",
    "docs/CLAIM_BOUNDARY.md",
    "docs/DATA_LINEAGE.md",
    "docs/MODEL_CARD.md",
    "paper/Pokala_HealthIntel_OS_Manuscript_Draft.md",
    "scripts/validate_artifacts.py",
]

def normalize_cmd(cmd: list[str]) -> list[str]:
    if IS_WINDOWS and cmd and cmd[0] == "npm":
        return ["npm.cmd", *cmd[1:]]
    return cmd

def run(cmd: list[str], cwd: Path = ROOT) -> dict:
    try:
        proc = subprocess.run(
            normalize_cmd(cmd),
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        return {
            "exit_code": proc.returncode,
            "passed": proc.returncode == 0,
            "output_tail": (proc.stdout + proc.stderr)[-4000:],
        }
    except FileNotFoundError as exc:
        return {"exit_code": 127, "passed": False, "output_tail": str(exc)}

def exists(path: str) -> bool:
    return (ROOT / path).exists()

def main() -> int:
    web_dir = ROOT / "apps" / "web"
    worker_dir = ROOT / "apps" / "worker"

    report = {
        "repo_root": str(ROOT),
        "required": {path: exists(path) for path in REQUIRED},
        "staff_grade_targets": {path: exists(path) for path in STAFF_GRADE_TARGETS},
        "git": {
            "branch": run(["git", "branch", "--show-current"])["output_tail"].strip(),
            "status_short": run(["git", "status", "--short"])["output_tail"].strip(),
        },
        "checks": {},
    }

    if (web_dir / "package.json").exists():
        report["checks"]["web_install_needed"] = not (web_dir / "node_modules").exists()
        report["checks"]["web_build"] = run(["npm", "run", "build"], web_dir)
    else:
        report["checks"]["web_build"] = {
            "exit_code": 1,
            "passed": False,
            "output_tail": "apps/web/package.json missing",
        }

    if (worker_dir / "package.json").exists():
        report["checks"]["worker_install_needed"] = not (worker_dir / "node_modules").exists()
        report["checks"]["worker_typecheck"] = run(["npm", "run", "typecheck"], worker_dir)
    else:
        report["checks"]["worker_typecheck"] = {
            "exit_code": 1,
            "passed": False,
            "output_tail": "apps/worker/package.json missing",
        }

    out_dir = ROOT / ".run"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "repo_audit.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nWrote {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
