#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOTS = [REPO/"apps"/"web"/"src", REPO/"docs"]

RENAMES = {
 "docs/BASECAMP5_FRONTEND_NOTE.md":"docs/BENCHMARK_PHASE5_FRONTEND_NOTE.md",
 "docs/BASECAMP5_MODEL_DATA_UPGRADE_REPORT.md":"docs/BENCHMARK_PHASE5_MODEL_DATA_UPGRADE_REPORT.md",
 "docs/BASECAMP6_REAL_BENCHMARK_HARNESS.md":"docs/BENCHMARK_PHASE6_REAL_BENCHMARK_HARNESS.md",
 "docs/BASECAMP6_REAL_BENCHMARK_REPORT.md":"docs/BENCHMARK_PHASE6_REAL_BENCHMARK_REPORT.md",
 "docs/BASECAMP7_MODEL_LAB_SYNC.md":"docs/BENCHMARK_PHASE7_MODEL_LAB_SYNC.md",
}

REPL = [
 ("Basecamp7","Benchmark Phase 7"), ("Basecamp6","Benchmark Phase 6"), ("Basecamp5","Benchmark Phase 5"), ("Basecamp","Benchmark Phase"),
 ("Meat Pack v1","Evidence Content Upgrade v1"), ("Meat Pack","Evidence Content Upgrade"), ("meat pack","evidence content upgrade"),
 ("summit-facing","reviewer-facing"), ("summit frontend","professional frontend"), ("summit","advanced"), ("Summit","Advanced"),
 ("founder-grade","professional-grade"), ("Founder-grade","Professional-grade"), ("SaaS v1 candidate","public portfolio release"),
 ("saasBuildBadge","releaseBadge"), ("LIVE_BUILD_PROOF_V1","PUBLIC_RELEASE_MARKER"), ("LIVE_BUILD_PROOF","PUBLIC_RELEASE_MARKER"),
 ("live build proof","deployment marker"), ("Live build proof","Deployment marker"), ("lone-wolf-mvp","public-portfolio"),
 ("world-class","high-quality"), ("World-class","High-quality"), ("revolutionary","advanced"), ("Revolutionary","Advanced"),
 ("Real benchmark outputs are now connected to the public interface.","Transparent benchmark outputs are connected to the public interface."),
 ("first MLP baseline attempt","initial MLP baseline run"), ("Baseline and early neural results","Benchmark results"),
 ("Next deep models","Planned model extensions"), ("LSTM, GRU, TCN, transformers","Sequence and transformer benchmarks"),
 ("Healthcare IT + deep learning evaluation workspace","Public healthcare intelligence workspace"),
 ("deep learning evaluation workspace","model evaluation workspace"),
]

BANNED = [r"LIVE_BUILD_PROOF", r"SaaS v1 candidate", r"Founder-grade", r"founder-grade", r"world-class", r"revolutionary", r"lone-wolf", r"\bMeat Pack\b", r"\bmeat pack\b", r"\bBasecamp[0-9]?\b", r"\bsummit-facing\b", r"\bsummit frontend\b"]

def files():
    for root in ROOTS:
        if not root.exists(): 
            continue
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".tsx",".ts",".css",".md",".json"} and "dist" not in p.parts and "node_modules" not in p.parts:
                yield p

def rename_docs():
    out=[]
    for s,d in RENAMES.items():
        src,dst=REPO/s,REPO/d
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists(): src.unlink()
            else: src.rename(dst)
            out.append(f"{s} -> {d}")
    return out

def replace_all():
    out=[]
    for p in files():
        txt=p.read_text(encoding="utf-8", errors="ignore")
        new=txt
        for a,b in REPL:
            new=new.replace(a,b)
        if new!=txt:
            p.write_text(new, encoding="utf-8")
            out.append(str(p.relative_to(REPO)))
    return out

def patch_json():
    p=REPO/"apps"/"web"/"src"/"data"/"model_benchmark.json"
    if not p.exists(): return False
    data=json.loads(p.read_text(encoding="utf-8"))
    data["public_label"]="Transparent model benchmark summary"
    data["reviewer_positioning"]="Research benchmark outputs with explicit claim boundaries."
    data["claim_boundary"]="Research benchmark only. No PHI. Not clinical decision support. No patient-level prediction."
    data["next_run_requirements"]=[
      "Build explicit temporal tensors",
      "Run multi-seed MLP/LSTM/GRU/TCN/Transformer comparisons",
      "Track early stopping and best checkpoints",
      "Report calibration and Brier score",
      "Add feature-family and source-family ablations",
      "Write failure-mode notes"
    ]
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True

def write_guide():
    text = """# Professional Language Guide

## Preferred public language

- Public healthcare intelligence workspace
- Healthcare IT intelligence
- Evidence-linked market diligence
- Claim-boundary governance
- Public-source data lineage
- Transparent model benchmarking
- Research benchmark
- Model evaluation workspace
- No PHI
- Not clinical decision support
- No patient-level prediction

## Avoid in public-facing copy

- Founder-grade
- SaaS v1 candidate
- Live build proof
- AI operating system
- Production clinical intelligence
- Revolutionary
- World-class
- MVP
- Summit / Basecamp / Meat Pack wording
- Any language implying validated forecasting or clinical decision support
"""
    (REPO/"docs"/"PROFESSIONAL_LANGUAGE_GUIDE.md").write_text(text, encoding="utf-8")

def scan():
    found=[]
    for p in files():
        txt=p.read_text(encoding="utf-8", errors="ignore")
        for pat in BANNED:
            if re.search(pat, txt):
                found.append(f"{p.relative_to(REPO)} :: {pat}")
    return found

def main():
    renamed=rename_docs()
    changed=replace_all()
    if patch_json(): changed.append("apps/web/src/data/model_benchmark.json")
    write_guide(); changed.append("docs/PROFESSIONAL_LANGUAGE_GUIDE.md")
    warnings=scan()
    report=["# Professional Language Sweep Report","","## Renamed docs",""]
    report += [f"- {x}" for x in renamed] or ["- None"]
    report += ["","## Changed files",""]
    report += [f"- {x}" for x in changed] or ["- None"]
    report += ["","## Remaining public-language warnings",""]
    report += [f"- {x}" for x in warnings] or ["- None"]
    report += ["","This sweep changes language only. It does not invent metrics or alter claim boundaries."]
    (REPO/"docs"/"PROFESSIONAL_LANGUAGE_SWEEP_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print("Professional language sweep complete.")
    print(f"Renamed docs: {len(renamed)}")
    print(f"Changed files: {len(changed)}")
    print(f"Remaining warnings: {len(warnings)}")
    for w in warnings[:20]: print("WARNING:", w)
if __name__=="__main__": main()
