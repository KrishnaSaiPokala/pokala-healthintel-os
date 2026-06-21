from pathlib import Path
import json
import re

REPO = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")
ROOTS = [REPO / "apps" / "web" / "src", REPO / "docs"]

def files():
    for root in ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".tsx", ".ts", ".css", ".md", ".json"}:
                if "dist" not in path.parts and "node_modules" not in path.parts:
                    yield path

def bad_score(s: str) -> int:
    bad_chars = [chr(0x00C2), chr(0x00C3), chr(0x00E2), chr(0xFFFD)]
    return sum(s.count(ch) for ch in bad_chars)

def repair_text(text: str) -> str:
    candidates = [text]

    for enc in ("latin1", "cp1252"):
        try:
            candidate = text.encode(enc, errors="ignore").decode("utf-8", errors="ignore")
            if candidate.strip():
                candidates.append(candidate)
        except Exception:
            pass

    fixed = min(candidates, key=bad_score)

    replacements = {
        chr(0x00C2) + chr(0x00B7): " / ",
        chr(0x00C2): "",
        chr(0x00C3): "",
        chr(0xFFFD): "",
        chr(0x00E2) + chr(0x20AC) + chr(0x2122): "'",
        chr(0x00E2) + chr(0x20AC) + chr(0x0153): '"',
        chr(0x00E2) + chr(0x20AC) + chr(0x009D): '"',
        chr(0x00E2) + chr(0x20AC) + chr(0x0093): "-",
        chr(0x00E2) + chr(0x20AC) + chr(0x0094): "-",
        chr(0x00E2) + chr(0x20AC) + chr(0x00A2): "-",
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

    for old, new in replacements.items():
        fixed = fixed.replace(old, new)

    fixed = fixed.replace(chr(0x00E2), "-")
    fixed = re.sub(r"\s*/\s*/\s*", " / ", fixed)
    return fixed

changed = []

for path in files():
    before = path.read_text(encoding="utf-8", errors="ignore")
    after = repair_text(before)
    if after != before:
        path.write_text(after, encoding="utf-8", newline="\n")
        changed.append(str(path.relative_to(REPO)).replace("\\", "/"))

docs = REPO / "docs"
docs.mkdir(parents=True, exist_ok=True)

reviewer = docs / "REVIEWER_GUIDE.md"
reviewer.write_text(
    "# Reviewer Guide\n\n"
    "Pokala HealthIntel OS is a public healthcare intelligence workspace for evidence-linked market diligence, claim-boundary governance, public-source data lineage, and transparent model benchmarking.\n\n"
    "## What to review\n\n"
    "1. Evidence Ledger for claim boundaries.\n"
    "2. Data Health for lineage posture.\n"
    "3. Model Lab for benchmark discipline.\n"
    "4. HIT Architecture for system design.\n"
    "5. Case Study for project coherence.\n\n"
    "## Boundaries\n\n"
    "- No PHI\n"
    "- Not clinical decision support\n"
    "- No patient-level prediction\n"
    "- Research benchmark only\n",
    encoding="utf-8",
    newline="\n",
)
changed.append("docs/REVIEWER_GUIDE.md")

case = docs / "TECHNICAL_CASE_STUDY.md"
case.write_text(
    "# Technical Case Study\n\n"
    "This project demonstrates a public-source healthcare intelligence workflow that separates evidence, data lineage, model benchmarking, and claim boundaries.\n\n"
    "## System shape\n\n"
    "1. Public-source data ingestion\n"
    "2. Evidence normalization\n"
    "3. Claim-boundary ledger\n"
    "4. Feature and data marts\n"
    "5. Benchmark harness\n"
    "6. Public web interface\n"
    "7. Validation and deployment guardrails\n\n"
    "## Model posture\n\n"
    "The benchmark layer includes completed baseline families and an initial MLP baseline. The next model step is temporal tensors, walk-forward validation, multi-seed runs, calibration, ablations, and failure-mode notes.\n",
    encoding="utf-8",
    newline="\n",
)
changed.append("docs/TECHNICAL_CASE_STUDY.md")

project_index = docs / "PROJECT_INDEX.md"
project_index.write_text(
    "# Project Index\n\n"
    "## Public modules\n\n"
    "- Market Brief\n"
    "- Evidence Ledger\n"
    "- Model Lab\n"
    "- Data Health\n"
    "- HIT Architecture\n"
    "- Case Study\n\n"
    "## Core docs\n\n"
    "- REVIEWER_GUIDE.md\n"
    "- TECHNICAL_CASE_STUDY.md\n"
    "- RECRUITER_BRIEF.md\n"
    "- CLAIM_BOUNDARY.md\n"
    "- DATA_LINEAGE.md\n"
    "- MODEL_CARD.md\n"
    "- ARCHITECTURE.md\n"
    "- DATA_SOURCES.md\n",
    encoding="utf-8",
    newline="\n",
)
changed.append("docs/PROJECT_INDEX.md")

summary_path = REPO / "apps" / "web" / "src" / "data" / "reviewer_artifact_summary.json"
summary_path.parent.mkdir(parents=True, exist_ok=True)
summary_path.write_text(
    json.dumps(
        {
            "artifact": "Pokala HealthIntel OS",
            "positioning": "Public healthcare intelligence workspace with evidence governance, public-source lineage, and transparent model benchmarking.",
            "boundaries": [
                "No PHI",
                "Not clinical decision support",
                "No patient-level prediction",
                "Research benchmark only"
            ],
            "reviewer_takeaway": [
                "Healthcare IT product thinking",
                "Evidence-linked claim governance",
                "Public-source data lineage",
                "Model benchmark discipline",
                "Deployment and validation discipline"
            ]
        },
        indent=2
    ),
    encoding="utf-8",
    newline="\n",
)
changed.append("apps/web/src/data/reviewer_artifact_summary.json")

css_path = REPO / "apps" / "web" / "src" / "styles" / "global.css"
if css_path.exists():
    css = css_path.read_text(encoding="utf-8", errors="ignore")
    marker = "/* === Summit Plus10 Final Polish === */"
    if marker in css:
        css = css[:css.index(marker)].rstrip()

    css += """

/* === Summit Plus10 Final Polish === */

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

.workspaceIntro h1,
.heroPrimary h1 {
  max-width: 980px;
  font-size: clamp(42px, 5.4vw, 78px);
  line-height: 0.92;
  letter-spacing: -0.07em;
}

.sectionIntro h2 {
  max-width: 880px;
  font-size: clamp(32px, 3.6vw, 50px);
  line-height: 1.02;
  letter-spacing: -0.058em;
}

.heroPrimary p,
.sectionIntro p {
  max-width: 850px;
  color: var(--elite-muted);
  font-size: 17px;
  font-weight: 650;
  line-height: 1.62;
}

.heroPanel,
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

.statCard strong {
  font-size: clamp(28px, 3vw, 42px);
  line-height: 0.96;
  letter-spacing: -0.058em;
}

.modelCard strong,
.iconCard strong,
.sourceCard strong,
.caseGrid strong {
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

.benchmarkTable {
  overflow-x: auto;
}

.benchmarkRow {
  min-width: 980px;
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
}
"""
    css_path.write_text(css, encoding="utf-8", newline="\n")
    changed.append("apps/web/src/styles/global.css")

bad_chars = [chr(0x00C2), chr(0x00C3), chr(0x00E2), chr(0xFFFD)]
findings = []
for path in files():
    text = path.read_text(encoding="utf-8", errors="ignore")
    for ch in bad_chars:
        if ch in text:
            findings.append(f"{path.relative_to(REPO)} contains mojibake marker U+{ord(ch):04X}")

if findings:
    print("PUBLIC_TEXT_GUARD_FAILED")
    for item in findings[:50]:
        print(item)
    raise SystemExit(2)

print("Final cleanup complete.")
for item in sorted(set(changed)):
    print("-", item)