#!/usr/bin/env python3
"""Full-power local artifact build for the Cloudflare MVP.

Runs the original overnight stages quickly unless --hours is set, then adds temporal self-attention
and D1 seed generation. This is the step to run before seeding Cloudflare D1.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd):
    print("$", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=0)
    ap.add_argument("--max-stage-seconds", type=float, default=20)
    args = ap.parse_args()
    cmd = [sys.executable, ROOT / "scripts" / "overnight_run.py", "--profile", "demo", "--max-stage-seconds", args.max_stage_seconds]
    if args.hours:
        cmd.extend(["--hours", args.hours])
    run(cmd)

    sys.path.insert(0, str(ROOT))
    from models.temporal_transformer.signal_transformer_numpy import run_temporal_attention, save_result
    intel_path = ROOT / "apps" / "web" / "src" / "data" / "intelligence.json"
    data = json.loads(intel_path.read_text(encoding="utf-8"))
    result = run_temporal_attention(data["temporal"])
    model_path = ROOT / "data" / "public" / "temporal_transformer_result.json"
    save_result(result, model_path)
    print(f"wrote {model_path}")
    data.setdefault("modelLab", {})["temporalTransformer"] = json.loads(model_path.read_text(encoding="utf-8"))
    data["scores"]["market"] = round(result.market_score, 2)
    data["scores"]["safety"] = round(result.safety_score, 2)
    data["scores"]["reimbursement"] = round(result.reimbursement_score, 2)
    data["meta"]["transformer"] = result.momentum_class
    intel_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    (ROOT / "data" / "public" / "intelligence.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    run([sys.executable, ROOT / "scripts" / "generate_d1_seed.py"])
    print("Full-power Cloudflare MVP artifacts are ready.")

if __name__ == "__main__":
    main()
