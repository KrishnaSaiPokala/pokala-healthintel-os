from pathlib import Path
import re

REPO = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")

APP = REPO / "apps" / "web" / "src" / "app" / "App.tsx"
EVIDENCE = REPO / "apps" / "web" / "src" / "lib" / "evidence.ts"
CSS = REPO / "apps" / "web" / "src" / "styles" / "global.css"

def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")

if not APP.exists():
    raise SystemExit(f"Missing {APP}")

app = APP.read_text(encoding="utf-8", errors="ignore")

replacements = {
    "Reviewer summary": "System overview",
    "A portfolio artifact with real technical signal.": "Evidence-linked healthcare intelligence.",
    "Healthcare IT intelligence": "Healthcare intelligence workspace",
    "Public healthcare intelligence for market diligence, evidence tracking, and model transparency.": "A public-source workspace for healthcare market analysis, evidence-linked claims, and transparent model benchmarking.",
    "Pokala HealthIntel OS demonstrates healthcare data engineering, claim-boundary governance, and transparent deep learning evaluation using bounded public datasets only.": "Pokala HealthIntel OS organizes public healthcare datasets, source-linked evidence, benchmark results, and claim boundaries into a deployed intelligence workspace. Built with public datasets only, with no PHI and no clinical decision-support claims.",
    "Public data \u00c2\u00b7 HIT boundaries \u00c2\u00b7 DL benchmark transparency": "Public data / HIT boundaries / transparent model benchmarks",
    "Public data · HIT boundaries · DL benchmark transparency": "Public data / HIT boundaries / transparent model benchmarks",
    "Public data / HIT boundaries / DL benchmark transparency": "Public data / HIT boundaries / transparent model benchmarks",
    "DL benchmark transparency": "transparent model benchmarks",
    "DL evaluation": "model evaluation",
    "deep learning evaluation": "model evaluation",
}

for old, new in replacements.items():
    app = app.replace(old, new)

# Remove internal/recruiter-facing meta language if it appears in sentence form.
app = re.sub(
    r"The interface is designed so recruiters and reviewers can quickly see[^<\n\r.]*\.",
    "The interface presents the system architecture, evidence posture, data lineage, and model-benchmark boundaries in one reviewable product surface.",
    app,
)

app = re.sub(
    r"recruiters and reviewers",
    "technical reviewers",
    app,
    flags=re.IGNORECASE,
)

app = app.replace("portfolio artifact", "deployed intelligence workspace")
app = app.replace("technical signal", "technical depth")

write(APP, app)

if EVIDENCE.exists():
    evidence = EVIDENCE.read_text(encoding="utf-8", errors="ignore")
    evidence = evidence.replace(" \u00c2\u00b7 ", " / ")
    evidence = evidence.replace(" · ", " / ")
    evidence = evidence.replace(" Â· ", " / ")
    write(EVIDENCE, evidence)

if not CSS.exists():
    raise SystemExit(f"Missing {CSS}")

css = CSS.read_text(encoding="utf-8", errors="ignore")
marker = "/* === Elite App Surface v4 === */"
if marker in css:
    css = css[:css.index(marker)].rstrip()

elite_css = r'''
/* === Elite App Surface v4 === */

:root {
  --elite-ink: #07111f;
  --elite-muted: #44546a;
  --elite-soft: #64748b;
  --elite-line: rgba(15, 23, 42, 0.10);
  --elite-card: rgba(255, 255, 255, 0.96);
  --elite-blue: #1d4ed8;
  --elite-blue-soft: rgba(29, 78, 216, 0.10);
  --elite-shadow: 0 18px 48px rgba(15, 23, 42, 0.075);
}

body {
  color: var(--elite-ink);
  letter-spacing: -0.006em;
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
}

.topbar {
  min-height: 84px;
  padding: 18px 32px;
  border-bottom: 1px solid var(--elite-line);
  background:
    linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(248, 250, 252, 0.90));
  backdrop-filter: blur(18px);
}

.brand span {
  color: var(--elite-ink);
  font-size: 13px;
  font-weight: 950;
  line-height: 1.05;
  letter-spacing: -0.018em;
  text-transform: none;
}

.brand strong {
  max-width: 420px;
  color: var(--elite-muted);
  font-size: 12px;
  font-weight: 760;
  line-height: 1.38;
  letter-spacing: 0.006em;
}

.navPills {
  border-radius: 18px;
  padding: 5px;
  border: 1px solid var(--elite-line);
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
  color: var(--elite-muted);
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
  border: 1px solid var(--elite-line);
  padding: 23px;
  background:
    radial-gradient(circle at 15% 0%, rgba(29, 78, 216, 0.12), transparent 16rem),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.95));
  box-shadow: var(--elite-shadow);
}

.workspaceIntro aside strong {
  display: block;
  color: var(--elite-ink);
  font-size: 18px;
  font-weight: 940;
  line-height: 1.22;
  letter-spacing: -0.035em;
}

.workspaceIntro aside p {
  color: var(--elite-muted);
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
  color: var(--elite-soft);
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
  border-color: var(--elite-line);
  background: var(--elite-card);
  box-shadow: var(--elite-shadow);
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
  color: var(--elite-muted);
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
  color: var(--elite-muted);
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
'''

css = css.rstrip() + "\n\n" + elite_css.strip() + "\n"
write(CSS, css)

bad_terms = [
    "portfolio artifact",
    "real technical signal",
    "recruiters and reviewers",
    "Reviewer summary",
    "DL benchmark transparency",
    "\u00c2\u00b7",
    "Â·",
]

scan = APP.read_text(encoding="utf-8", errors="ignore") + "\n" + EVIDENCE.read_text(encoding="utf-8", errors="ignore")
found = [term for term in bad_terms if term in scan]

if found:
    print("BAD_TERMS_REMAIN")
    for term in found:
        print("-", term)
    raise SystemExit(2)

print("Elite copy and UI polish applied.")
print("Changed:")
print("- apps/web/src/app/App.tsx")
print("- apps/web/src/lib/evidence.ts")
print("- apps/web/src/styles/global.css")