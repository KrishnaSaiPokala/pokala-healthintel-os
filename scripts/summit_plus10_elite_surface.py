#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APP = REPO / "apps" / "web" / "src" / "app" / "App.tsx"
CSS = REPO / "apps" / "web" / "src" / "styles" / "global.css"
DATA_DIR = REPO / "apps" / "web" / "src" / "data"
DOCS = REPO / "docs"

ROOTS = [REPO / "apps" / "web" / "src", DOCS]

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except Exception:
        return str(path)

def text_files():
    for root in ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".tsx", ".ts", ".css", ".md", ".json"}:
                if "dist" not in path.parts and "node_modules" not in path.parts:
                    yield path

def clean_public_text() -> list[str]:
    changed = []
    replacements = {
        "\u00c2\u00b7": " / ",
        "\u00c2": "",
        "\u00c3\u0082": "",
        "\u00c3\u0082\u00c2\u00b7": " / ",
        "\u00e2\u0080\u0099": "'",
        "\u00e2\u0080\u0098": "'",
        "\u00e2\u0080\u009c": '"',
        "\u00e2\u0080\u009d": '"',
        "\u00e2\u0080\u0093": "-",
        "\u00e2\u0080\u0094": "-",
        "\u00e2\u0080\u00a2": "-",
        "Public data /  HIT boundaries /  DL benchmark transparency": "Public data / HIT boundaries / transparent model benchmarks",
        "Public data / HIT boundaries / DL benchmark transparency": "Public data / HIT boundaries / transparent model benchmarks",
        "Public data / HIT boundaries / model benchmark transparency": "Public data / HIT boundaries / transparent model benchmarks",
        "Public data / HIT boundaries / model benchmarks transparency": "Public data / HIT boundaries / transparent model benchmarks",
        "DL benchmark transparency": "transparent model benchmarks",
        "DL benchmark": "model benchmark",
        "DL evaluation": "model evaluation",
        "Healthcare IT + deep learning evaluation workspace": "Public healthcare intelligence workspace",
        "Healthcare IT + model evaluation workspace": "Public healthcare intelligence workspace",
        "HIT maturity + DL evaluation discipline": "Healthcare IT maturity + model evaluation discipline",
        "DL evaluation discipline": "model evaluation discipline",
        "Evidence-linked healthcare intelligence with transparent model evaluation.": "Evidence-linked healthcare intelligence with transparent model benchmarking.",
        "Public healthcare intelligence with evidence governance and transparent model evaluation.": "Evidence-linked healthcare intelligence with transparent model benchmarking.",
    }

    for path in text_files():
        before = path.read_text(encoding="utf-8", errors="ignore")
        after = before
        for old, new in replacements.items():
            after = after.replace(old, new)
        after = re.sub(r"\s*/\s*/\s*", " / ", after)
        after = after.replace("Public data / HIT boundaries / transparent model benchmarks", "Public data / HIT boundaries / transparent model benchmarks")
        if after != before:
            path.write_text(after, encoding="utf-8", newline="\n")
            changed.append(rel(path))
    return changed

def patch_app_copy() -> list[str]:
    if not APP.exists():
        return []
    before = APP.read_text(encoding="utf-8", errors="ignore")
    after = before

    copy_replacements = {
        "A public-source Healthcare IT intelligence workspace for evidence-linked market diligence, data lineage, and transparent model benchmarking.": "A public healthcare intelligence workspace for evidence-linked market diligence, claim-boundary governance, and transparent model benchmarking.",
        "Built to demonstrate healthcare data engineering, claim-boundary governance, and deep learning evaluation without PHI or clinical decision-support claims.": "Built to demonstrate healthcare data engineering, public-source lineage, and model-evaluation transparency without PHI or clinical decision-support claims.",
        "Built with public data only. No PHI. Not clinical decision support.": "Built with public data only. No PHI. Not clinical decision support.",
        "transparent model evaluation": "transparent model benchmarking",
        "model evaluation workspace": "model benchmarking workspace",
    }
    for old, new in copy_replacements.items():
        after = after.replace(old, new)

    if after != before:
        APP.write_text(after, encoding="utf-8", newline="\n")
        return [rel(APP)]
    return []

def write_reviewer_data() -> list[str]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact": "Pokala HealthIntel OS",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "positioning": "Public healthcare intelligence workspace with evidence governance, public-source lineage, and transparent model benchmarking.",
        "reviewer_takeaway": [
            "Healthcare IT product thinking",
            "Evidence-linked claim governance",
            "Public-source data lineage",
            "Model benchmark discipline",
            "Deployment and validation discipline",
        ],
        "boundaries": [
            "No PHI",
            "Not clinical decision support",
            "No patient-level prediction",
            "Research benchmark only",
            "Public-source evidence boundaries are explicit",
        ],
        "proof_points": [
            "Live Cloudflare Worker deployment",
            "Validated web build and worker typecheck",
            "Evidence rows and source counts checked by lineage script",
            "Baseline model results synced into Model Lab",
            "Professional language and encoding guardrails",
        ],
        "next_summit_steps": [
            "Design System v2 visual refinement",
            "Model Lab v2 with calibration and failure modes",
            "Deep benchmark runner for MLP, LSTM, GRU, TCN, and temporal transformers",
            "Evidence transformer retrieval layer",
            "Final README, case study, and architecture package",
        ],
    }
    path = DATA_DIR / "reviewer_artifact_summary.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
    return [rel(path)]

def write_docs() -> list[str]:
    DOCS.mkdir(parents=True, exist_ok=True)
    changed = []

    reviewer = """# Reviewer Guide

## One-sentence description

Pokala HealthIntel OS is a public healthcare intelligence workspace for evidence-linked market diligence, claim-boundary governance, public-source data lineage, and transparent model benchmarking.

## What a reviewer should notice

1. The project is deployed as a real web application.
2. The interface separates evidence, data health, model benchmarking, and architecture.
3. The model layer includes real baseline execution and a synced benchmark table.
4. The data story is public-source and explicitly bounded.
5. The project avoids clinical decision-support and patient-level prediction claims.

## Core boundaries

- No PHI
- Not clinical decision support
- No patient-level prediction
- Research benchmark only
- Public evidence does not prove causality unless the source directly supports that claim

## Best evaluation path

1. Start with the landing page.
2. Review Evidence Ledger for claim boundaries.
3. Review Data Health for lineage posture.
4. Review Model Lab for benchmark discipline.
5. Review HIT Architecture for system design.
6. Review Case Study for project coherence.
"""
    path = DOCS / "REVIEWER_GUIDE.md"
    path.write_text(reviewer, encoding="utf-8", newline="\n")
    changed.append(rel(path))

    case = """# Technical Case Study

## Problem

Healthcare market and product diligence often mixes public facts, inference, and unsupported claims. This project demonstrates a safer public-source workflow that separates evidence, data lineage, model benchmarks, and claim boundaries.

## Constraints

- Public data only
- No PHI
- Not clinical decision support
- No patient-level prediction
- No overclaiming from passive reports or public registries

## System shape

1. Public-source data ingestion
2. Evidence and data normalization
3. Claim-boundary ledger
4. Feature/data marts
5. Benchmark harness
6. Public web interface
7. Validation and deployment guardrails

## Model-evaluation posture

The current benchmark layer includes completed baseline families and an initial MLP baseline. The next model step is not to add model names for decoration, but to add temporal tensors, walk-forward validation, multi-seed runs, calibration, ablations, and failure-mode notes.

## Reviewer takeaway

This is a healthcare IT and model-evaluation artifact that prioritizes evidence discipline, public-source governance, transparent benchmarking, and deployed product presentation.
"""
    path = DOCS / "TECHNICAL_CASE_STUDY.md"
    path.write_text(case, encoding="utf-8", newline="\n")
    changed.append(rel(path))

    index = """# Project Index

## Live artifact

Pokala HealthIntel OS is a deployed public healthcare intelligence workspace.

## Public-facing modules

- Market Brief
- Evidence Ledger
- Model Lab
- Data Health
- HIT Architecture
- Case Study

## Core docs

- REVIEWER_GUIDE.md
- TECHNICAL_CASE_STUDY.md
- RECRUITER_BRIEF.md
- CLAIM_BOUNDARY.md
- DATA_LINEAGE.md
- MODEL_CARD.md
- ARCHITECTURE.md
- DATA_SOURCES.md

## Current proof points

- Web build passes
- Worker typecheck passes
- Artifact validation passes
- Data lineage verification passes
- Benchmark outputs are synced to the Model Lab
- Cloudflare Worker deployment succeeds

## Boundary

The project is a public-source research and portfolio artifact. It is not clinical decision support.
"""
    path = DOCS / "PROJECT_INDEX.md"
    path.write_text(index, encoding="utf-8", newline="\n")
    changed.append(rel(path))

    readme_add = """# Pokala HealthIntel OS

A public healthcare intelligence workspace for evidence-linked market diligence, claim-boundary governance, public-source data lineage, and transparent model benchmarking.

## Live system

The public application is deployed as a Cloudflare Worker-backed web interface.

## What it demonstrates

- Healthcare IT product thinking
- Public-source data engineering
- Evidence-linked claim governance
- Transparent model benchmarking
- Validation and deployment discipline

## Boundaries

- No PHI
- Not clinical decision support
- No patient-level prediction
- Research benchmark only

## Reviewer path

1. Open the live application.
2. Review Evidence Ledger for claim boundaries.
3. Review Data Health for source lineage.
4. Review Model Lab for benchmark discipline.
5. Review HIT Architecture and Case Study for system design.

## Key documentation

- docs/REVIEWER_GUIDE.md
- docs/TECHNICAL_CASE_STUDY.md
- docs/RECRUITER_BRIEF.md
- docs/PROJECT_INDEX.md
"""
    readme = REPO / "README.md"
    if not readme.exists() or "public healthcare intelligence workspace" not in readme.read_text(encoding="utf-8", errors="ignore").lower():
        readme.write_text(readme_add, encoding="utf-8", newline="\n")
        changed.append(rel(readme))

    return changed

POLISH_CSS = """
/* === Summit Plus 10: professional product surface === */

:root {
  --elite-ink: #07111f;
  --elite-muted: #475569;
  --elite-soft: #64748b;
  --elite-line: rgba(15, 23, 42, 0.10);
  --elite-card: rgba(255, 255, 255, 0.95);
}

body {
  color: var(--elite-ink);
  letter-spacing: -0.006em;
}

.topbar {
  min-height: 82px;
  padding: 18px 32px;
  border-bottom: 1px solid var(--elite-line);
  background: rgba(248, 250, 252, 0.94);
}

.brand span {
  color: var(--elite-ink);
  font-size: 13px;
  font-weight: 950;
  letter-spacing: -0.015em;
  text-transform: none;
}

.brand strong {
  max-width: 390px;
  color: var(--elite-muted);
  font-size: 12px;
  font-weight: 760;
  line-height: 1.38;
  letter-spacing: 0.01em;
}

.navPills {
  border-radius: 18px;
  padding: 5px;
  box-shadow: 0 16px 44px rgba(15, 23, 42, 0.055);
}

.navPills button {
  border-radius: 14px;
  font-size: 12px;
  font-weight: 820;
  letter-spacing: -0.005em;
}

.trustPills span,
.chipRow span {
  min-height: 30px;
  border-radius: 10px;
  padding: 0 10px;
  background: rgba(255, 255, 255, 0.88);
  color: var(--elite-muted);
  font-size: 11px;
  font-weight: 820;
  letter-spacing: 0.01em;
}

.workspaceIntro {
  grid-template-columns: minmax(0, 1fr) minmax(310px, 390px);
  gap: 20px;
  margin-bottom: 24px;
}

.workspaceIntro h1 {
  max-width: 980px;
  font-size: clamp(38px, 4.9vw, 66px);
  line-height: 0.96;
  letter-spacing: -0.062em;
}

.workspaceIntro aside {
  border-radius: 22px;
  padding: 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(248, 250, 252, 0.94)),
    radial-gradient(circle at 20% 0%, rgba(37, 99, 235, 0.10), transparent 16rem);
}

.workspaceIntro aside strong {
  display: block;
  color: var(--elite-ink);
  font-size: 17px;
  line-height: 1.28;
  letter-spacing: -0.025em;
}

.eyebrow,
.workspaceIntro aside span,
.statCard span,
.modelCard span,
.ledgerDetail > span,
.benchmarkHeader aside span,
.caseGrid span {
  color: var(--elite-soft);
  font-size: 10.5px;
  font-weight: 920;
  letter-spacing: 0.115em;
}

.heroPanel,
.summitPanel,
.sectionIntro,
.statCard,
.iconCard,
.modelCard,
.ledgerShell,
.sourceCard,
.architectureFlow article,
.twoPanel article,
.caseGrid article,
.benchmarkPanel {
  border-radius: 22px;
  border-color: var(--elite-line);
  background: var(--elite-card);
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.065);
}

.heroPrimary {
  padding: clamp(26px, 3.2vw, 42px);
  background:
    radial-gradient(circle at 0% 0%, rgba(37, 99, 235, 0.105), transparent 28rem),
    linear-gradient(135deg, #ffffff, #f8fbff 58%, #eef6ff);
}

.heroPrimary h1 {
  max-width: 980px;
  font-size: clamp(42px, 5.4vw, 78px);
  line-height: 0.92;
  letter-spacing: -0.07em;
}

.heroPrimary p,
.sectionIntro p {
  max-width: 850px;
  color: var(--elite-muted);
  font-size: 17px;
  font-weight: 650;
  line-height: 1.62;
}

.sectionIntro {
  padding: clamp(24px, 3vw, 36px);
}

.sectionIntro h2 {
  max-width: 880px;
  font-size: clamp(32px, 3.6vw, 50px);
  line-height: 1.02;
  letter-spacing: -0.058em;
}

.statGrid,
.skillsGrid,
.modelGrid,
.sourceGrid,
.caseGrid {
  gap: 16px;
}

.statCard,
.iconCard,
.modelCard,
.sourceCard,
.caseGrid article {
  padding: 20px;
}

.statCard strong {
  margin-top: 12px;
  font-size: clamp(28px, 3vw, 42px);
  line-height: 0.96;
  letter-spacing: -0.058em;
}

.modelCard strong {
  margin-top: 12px;
  font-size: clamp(20px, 2vw, 30px);
  line-height: 1.02;
  letter-spacing: -0.045em;
}

.iconCard strong,
.sourceCard strong,
.caseGrid strong {
  font-size: 21px;
  line-height: 1.05;
  letter-spacing: -0.043em;
}

.iconCard p,
.statCard p,
.modelCard p,
.sourceCard p,
.caseGrid p,
.ledgerDetail p,
.twoPanel p,
.architectureFlow p {
  color: var(--elite-muted);
  font-weight: 640;
  line-height: 1.55;
}

.benchmarkHeader h2,
.bentoTile h2,
.ledgerDetail h2,
.twoPanel h2 {
  font-size: clamp(27px, 2.8vw, 38px);
  line-height: 1.02;
  letter-spacing: -0.055em;
}

.benchmarkPanel {
  overflow: hidden;
}

.benchmarkHeader {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.98), rgba(255, 255, 255, 0.96));
}

.benchmarkTable {
  overflow-x: auto;
}

.benchmarkRow {
  min-width: 980px;
}

.benchmarkRow strong {
  font-size: 12.5px;
}

.benchmarkRow span,
.benchmarkRow p {
  font-size: 12px;
  font-weight: 640;
}

.dataTable,
.ledgerShell {
  border-radius: 22px;
}

.tableHeader,
.benchmarkHead {
  background: linear-gradient(135deg, #0f172a, #172033);
}

.actionRow button {
  border-radius: 13px;
  min-height: 44px;
  padding: 0 16px;
  font-size: 12.5px;
  letter-spacing: -0.005em;
}

@media (max-width: 1160px) {
  .workspaceIntro {
    grid-template-columns: 1fr;
  }

  .workspaceIntro aside {
    max-width: none;
  }
}

@media (max-width: 760px) {
  .topbar {
    padding: 14px;
  }

  .workspaceIntro h1,
  .heroPrimary h1 {
    font-size: clamp(38px, 12vw, 54px);
    line-height: 0.95;
  }

  .sectionIntro h2 {
    font-size: clamp(30px, 9vw, 42px);
  }
}
"""

def append_css() -> list[str]:
    if not CSS.exists():
        return []
    css = CSS.read_text(encoding="utf-8", errors="ignore")
    for marker in ["/* === Summit Plus 10:", "/* === Professional UI Polish"]:
        if marker in css:
            css = css[:css.index(marker)].rstrip() + "\n"
    css = css.rstrip() + "\n\n" + POLISH_CSS.strip() + "\n"
    CSS.write_text(css, encoding="utf-8", newline="\n")
    return [rel(CSS)]

def guard_public_text() -> None:
    bad_terms = [
        "\u00c2",
        "\u00e2",
        "LIVE_BUILD_PROOF",
        "SaaS v1 candidate",
        "Founder-grade",
        "founder-grade",
        "world-class",
        "revolutionary",
        "lone-wolf",
        "Meat Pack",
        "meat pack",
        "summit-facing",
        "summit frontend",
    ]
    findings = []
    for path in text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term in bad_terms:
            if term in text:
                findings.append(f"{rel(path)} :: {term}")
    if findings:
        print("PUBLIC_TEXT_GUARD_FAILED")
        for item in findings[:80]:
            print(item)
        raise SystemExit(2)

def main() -> int:
    changed = []
    changed += clean_public_text()
    changed += patch_app_copy()
    changed += write_reviewer_data()
    changed += write_docs()
    changed += append_css()

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "changed_files": sorted(set(changed)),
        "boundary": "Copy, docs, and presentation only. Metrics were not invented or altered.",
    }
    DOCS.mkdir(parents=True, exist_ok=True)
    report_path = DOCS / "SUMMIT_PLUS10_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    changed.append(rel(report_path))

    guard_public_text()

    print("Summit plus 10 elite surface pack complete.")
    print("Changed files:")
    for item in sorted(set(changed)):
        print("-", item)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
