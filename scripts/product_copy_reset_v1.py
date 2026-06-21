from pathlib import Path
import re

REPO = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")
SRC = REPO / "apps" / "web" / "src"
CSS = SRC / "styles" / "global.css"

FILES = [
    p for p in SRC.rglob("*")
    if p.is_file()
    and p.suffix.lower() in {".tsx", ".ts", ".json", ".css"}
    and "dist" not in p.parts
    and "node_modules" not in p.parts
]

COPY_REPLACEMENTS = {
    # Weak/meta framing -> product framing
    "Reviewer signal": "Governance posture",
    "Reviewer summary": "System overview",
    "A portfolio artifact with real technical signal.": "Evidence-linked healthcare intelligence.",
    "portfolio artifact": "deployed healthcare intelligence workspace",
    "technical signal": "technical depth",
    "real technical signal": "technical depth",
    "recruiters and reviewers": "technical stakeholders",
    "recruiters": "technical stakeholders",
    "reviewers": "technical stakeholders",
    "reviewer": "stakeholder",

    # Exact bad line
    "Public data \u00c2\u00b7 HIT boundaries \u00c2\u00b7 DL benchmark transparency": "Public data / evidence boundaries / transparent model benchmarks",
    "Public data Â· HIT boundaries Â· DL benchmark transparency": "Public data / evidence boundaries / transparent model benchmarks",
    "Public data · HIT boundaries · DL benchmark transparency": "Public data / evidence boundaries / transparent model benchmarks",
    "Public data / HIT boundaries / DL benchmark transparency": "Public data / evidence boundaries / transparent model benchmarks",
    "DL benchmark transparency": "transparent model benchmarks",

    # Weak hero/sidebar language
    "HIT maturity + model evaluation discipline": "Evidence governance / data lineage / model benchmarking",
    "Built to show practical judgment: public-data boundaries, lineage visibility, model transparency, and professional restraint.": "Built for source-bound analysis: public-data boundaries, lineage visibility, transparent benchmarks, and explicit non-clinical-use limits.",
    "Built to show practical judgment": "Built for source-bound analysis",
    "professional restraint": "explicit claim boundaries",
    "practical judgment": "operational clarity",

    # Product category cleanup
    "Healthcare IT intelligence": "Healthcare intelligence workspace",
    "Public healthcare intelligence for market diligence, evidence tracking, and model transparency.": "Public-source healthcare intelligence for market analysis, evidence governance, and transparent model benchmarking.",
    "Pokala HealthIntel OS demonstrates healthcare data engineering, claim-boundary governance, and transparent deep learning evaluation using bounded public datasets only.": "Pokala HealthIntel OS organizes public healthcare datasets, source-linked evidence, benchmark outputs, and claim boundaries inside a deployed intelligence workspace. It uses public data only, contains no PHI, and is not clinical decision support.",
    "deep learning evaluation": "model benchmarking",
    "DL evaluation": "model benchmarking",
    "model transparency": "transparent model benchmarking",

    # Tab names: make app-like, less portfolio-like
    "Market Brief": "Market Intelligence",
    "Evidence Ledger": "Evidence Governance",
    "Model Lab": "Benchmark Lab",
    "Data Health": "Data Lineage",
    "HIT Architecture": "System Architecture",
    "Case Study": "Implementation Brief",

    # Boundary wording
    "Not CDS": "Non-clinical use",
    "Not clinical decision support": "Not clinical decision support",
    "Claim-boundary governance": "Claim-boundary controls",
    "Model limitations disclosed": "Model limits disclosed",
}

def rewrite_text(text: str) -> str:
    out = text

    for old, new in COPY_REPLACEMENTS.items():
        out = out.replace(old, new)

    # Replace common mojibake separator only; do not run broad encoding repair.
    out = out.replace(" \u00c2\u00b7 ", " / ")
    out = out.replace(" Â· ", " / ")
    out = out.replace(" · ", " / ")

    # Remove awkward meta sentence variants.
    out = re.sub(
        r"The interface is designed so technical stakeholders can quickly see[^<\n\r.]*\.",
        "The interface surfaces source lineage, evidence boundaries, benchmark outputs, and system architecture in one product workspace.",
        out,
        flags=re.IGNORECASE,
    )

    out = re.sub(
        r"The interface is designed so recruiters and reviewers can quickly see[^<\n\r.]*\.",
        "The interface surfaces source lineage, evidence boundaries, benchmark outputs, and system architecture in one product workspace.",
        out,
        flags=re.IGNORECASE,
    )

    return out

changed = []

for path in FILES:
    before = path.read_text(encoding="utf-8", errors="ignore")
    after = rewrite_text(before)
    if after != before:
        path.write_text(after, encoding="utf-8", newline="\n")
        changed.append(str(path.relative_to(REPO)).replace("\\", "/"))

if not CSS.exists():
    raise SystemExit("Missing global.css")

css = CSS.read_text(encoding="utf-8", errors="ignore")
marker = "/* === Product-grade Surface Reset v1 === */"
if marker in css:
    css = css[:css.index(marker)].rstrip()

css += r"""

/* === Product-grade Surface Reset v1 === */

:root {
  --surface-ink: #07111f;
  --surface-muted: #405166;
  --surface-soft: #64748b;
  --surface-line: rgba(15, 23, 42, 0.10);
  --surface-card: rgba(255, 255, 255, 0.96);
  --surface-blue: #1d4ed8;
  --surface-shadow: 0 18px 48px rgba(15, 23, 42, 0.075);
}

body {
  color: var(--surface-ink);
  letter-spacing: -0.006em;
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
}

.topbar {
  min-height: 84px;
  padding: 18px 32px;
  border-bottom: 1px solid var(--surface-line);
  background:
    linear-gradient(180deg, rgba(248, 250, 252, 0.97), rgba(248, 250, 252, 0.91));
  backdrop-filter: blur(18px);
}

.brand span {
  color: var(--surface-ink);
  font-size: 13px;
  font-weight: 950;
  line-height: 1.05;
  letter-spacing: -0.018em;
  text-transform: none;
}

.brand strong {
  max-width: 430px;
  color: var(--surface-muted);
  font-size: 12px;
  font-weight: 760;
  line-height: 1.38;
  letter-spacing: 0.006em;
}

.navPills {
  border-radius: 18px;
  padding: 5px;
  border: 1px solid var(--surface-line);
  background: rgba(255, 255, 255, 0.76);
  box-shadow: 0 16px 44px rgba(15, 23, 42, 0.055);
}

.navPills button {
  min-height: 38px;
  border-radius: 14px;
  padding: 0 13px;
  font-size: 12px;
  font-weight: 820;
  letter-spacing: -0.006em;
}

.trustPills span,
.chipRow span {
  min-height: 30px;
  border-radius: 10px;
  padding: 0 10px;
  background: rgba(255, 255, 255, 0.90);
  color: var(--surface-muted);
  font-size: 11px;
  font-weight: 820;
  letter-spacing: 0.012em;
}

.workspaceIntro {
  grid-template-columns: minmax(0, 1fr) minmax(320px, 410px);
  gap: 22px;
  margin-bottom: 26px;
}

.workspaceIntro h1,
.heroPrimary h1 {
  max-width: 1040px;
  font-size: clamp(44px, 5.5vw, 78px);
  line-height: 0.92;
  letter-spacing: -0.072em;
}

.workspaceIntro aside {
  border-radius: 24px;
  border: 1px solid var(--surface-line);
  padding: 23px;
  background:
    radial-gradient(circle at 15% 0%, rgba(29, 78, 216, 0.12), transparent 16rem),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.95));
  box-shadow: var(--surface-shadow);
}

.workspaceIntro aside strong {
  display: block;
  color: var(--surface-ink);
  font-size: 18px;
  font-weight: 940;
  line-height: 1.22;
  letter-spacing: -0.035em;
}

.workspaceIntro aside p {
  color: var(--surface-muted);
  font-size: 14px;
  font-weight: 650;
  line-height: 1.55;
}

.eyebrow,
.workspaceIntro aside span,
.statCard span,
.modelCard span,
.ledgerDetail > span,
.benchmarkHeader aside span,
.caseGrid span {
  color: var(--surface-soft);
  font-size: 10.5px;
  font-weight: 920;
  letter-spacing: 0.115em;
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
  border-radius: 24px;
  border-color: var(--surface-line);
  background: var(--surface-card);
  box-shadow: var(--surface-shadow);
}

.heroPrimary {
  padding: clamp(28px, 3.4vw, 44px);
  background:
    radial-gradient(circle at 0% 0%, rgba(29, 78, 216, 0.12), transparent 30rem),
    radial-gradient(circle at 100% 20%, rgba(14, 165, 233, 0.10), transparent 24rem),
    linear-gradient(135deg, #ffffff, #f8fbff 58%, #eef6ff);
}

.heroPrimary p,
.sectionIntro p {
  max-width: 880px;
  color: var(--surface-muted);
  font-size: 17px;
  font-weight: 650;
  line-height: 1.62;
}

.sectionIntro {
  padding: clamp(24px, 3vw, 38px);
}

.sectionIntro h2 {
  max-width: 900px;
  font-size: clamp(32px, 3.7vw, 52px);
  line-height: 1.01;
  letter-spacing: -0.06em;
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
  padding: 21px;
}

.statCard strong {
  margin-top: 12px;
  font-size: clamp(29px, 3vw, 43px);
  line-height: 0.96;
  letter-spacing: -0.06em;
}

.modelCard strong {
  margin-top: 12px;
  font-size: clamp(20px, 2vw, 30px);
  line-height: 1.02;
  letter-spacing: -0.047em;
}

.iconCard strong,
.sourceCard strong,
.caseGrid strong {
  font-size: 21px;
  line-height: 1.05;
  letter-spacing: -0.044em;
}

.iconCard p,
.statCard p,
.modelCard p,
.sourceCard p,
.caseGrid p,
.ledgerDetail p,
.twoPanel p,
.architectureFlow p {
  color: var(--surface-muted);
  font-weight: 640;
  line-height: 1.57;
}

.benchmarkHeader h2,
.bentoTile h2,
.ledgerDetail h2,
.twoPanel h2 {
  font-size: clamp(27px, 2.8vw, 39px);
  line-height: 1.02;
  letter-spacing: -0.056em;
}

.benchmarkPanel {
  overflow: hidden;
}

.benchmarkHeader {
  background:
    radial-gradient(circle at 0% 0%, rgba(29, 78, 216, 0.08), transparent 16rem),
    linear-gradient(180deg, rgba(248, 250, 252, 0.99), rgba(255, 255, 255, 0.96));
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
  border-radius: 24px;
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
  font-weight: 820;
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

CSS.write_text(css, encoding="utf-8", newline="\n")
changed.append(str(CSS.relative_to(REPO)).replace("\\", "/"))

bad_terms = [
    "Reviewer signal",
    "Reviewer summary",
    "portfolio artifact",
    "technical signal",
    "real technical signal",
    "recruiters",
    "recruiter",
    "Built to show practical judgment",
    "professional restraint",
    "HIT maturity + model evaluation discipline",
    "DL benchmark transparency",
    " Â· ",
    "\u00c2\u00b7",
]

scan_files = [
    p for p in FILES
    if p.suffix.lower() in {".tsx", ".ts", ".json"}
]

findings = []
for path in scan_files:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for term in bad_terms:
        if term in text:
            findings.append(f"{path.relative_to(REPO)} :: {term}")

if findings:
    print("BAD_PRODUCT_COPY_REMAINS")
    for item in findings[:80]:
        print(item)
    raise SystemExit(2)

print("Product copy reset complete.")
print("Changed files:")
for item in sorted(set(changed)):
    print("-", item)