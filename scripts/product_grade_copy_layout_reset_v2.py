from pathlib import Path
import re

REPO = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")

FILES = [
    REPO / "apps" / "web" / "src" / "app" / "App.tsx",
    REPO / "apps" / "web" / "src" / "modules" / "command-center" / "CommandCenter.tsx",
    REPO / "apps" / "web" / "src" / "modules" / "executive-brief" / "ExecutiveBrief.tsx",
    REPO / "apps" / "web" / "src" / "data" / "intelligence.json",
    REPO / "apps" / "web" / "src" / "data" / "model_benchmark.json",
]

CSS = REPO / "apps" / "web" / "src" / "styles" / "global.css"
INDEX = REPO / "apps" / "web" / "index.html"

REPLACEMENTS = {
    # App.tsx product copy
    "Reviewer takeaway": "Operational takeaway",
    "Reviewer signal": "Governance posture",
    "Reviewer summary": "System overview",
    "Copy recruiter summary": "Copy system summary",
    "recruiter-facing workspace": "public-source workspace",
    "A recruiter-facing workspace explains HIT maturity, model evaluation, and safe claim posture.": "The public interface presents source lineage, claim boundaries, benchmark posture, and deployment architecture.",
    "A recruiter-facing workspace explains HIT maturity, model evaluation, and safe claim posture": "The public interface presents source lineage, claim boundaries, benchmark posture, and deployment architecture",
    "Shows HIT judgment: useful public data, but bounded carefully.": "Keeps provider-market analysis tied to public-source context and explicit claim limits.",
    "Shows ability to use reimbursement context without overclaiming economics.": "Frames reimbursement signals as market context, not private economics or forecasted revenue.",
    "Shows mature safety-data interpretation in a healthcare IT setting.": "Treats passive safety reports as governance context, not incidence or causality.",
    "Shows registry interpretation without claiming product adoption.": "Uses registry activity as innovation context without inferring commercial adoption.",
    "Shows data governance awareness, not just dashboarding.": "Separates source lineage, freshness, and limitations from the analytical output.",
    "Shows DL maturity: metrics plus restraint.": "Reports benchmark metrics with explicit limitations and non-clinical-use boundaries.",
    "None in demo": "No PHI in source",
    "Reviewer takeaway": "Operational takeaway",
    "The project demonstrates healthcare data judgment, product communication, and ML evaluation discipline in a deployed interface.": "The system connects public data, evidence boundaries, model benchmarks, and deployment controls in one operational workspace.",
    "What this demonstrates": "System capabilities",
    "This workspace is designed to make the technical depth legible: healthcare data engineering, evidence controls, temporal modeling, and communication judgment behind the project.": "The workspace organizes healthcare data engineering, evidence controls, benchmark outputs, and deployment posture into a single reviewable operating surface.",
    "Judgment under constraints": "Governed analysis under constraints",
    "The strongest part of this project is not a single metric. It is the system design:": "The core value is the system design:",
    "Move from demo to deeper product proof": "Next system hardening step",
    "The next layer would add deeper evidence-row browsing, source freshness metadata, model run comparison, screenshots, and a README-driven recruiter package.": "The next layer should add deeper evidence-row browsing, richer source freshness metadata, model-run comparison, exportable summaries, and stronger architecture documentation.",
    "Deployed demo": "Deployed workspace",
    "Portfolio case study": "Implementation brief",
    "deep learning evaluation": "model benchmarking",
    "Deep learning evaluation": "Benchmark governance",
    "Compliance-aware product writing": "Healthcare claim boundaries",
    "Technical communication": "Architecture communication",
    "Architecture, model limits, and data lineage are written for technical stakeholders, professors, and technical stakeholders.": "Architecture, model limits, and data lineage are written as product-facing system controls.",
    "Pokala HealthIntel OS demonstrates healthcare data engineering, claim-boundary governance,\n            and transparent model evaluation using bounded public datasets only.": "Pokala HealthIntel OS organizes public healthcare datasets, source-linked evidence, benchmark outputs, and claim boundaries inside a deployed intelligence workspace.",
    "Pokala HealthIntel OS demonstrates healthcare data engineering, claim-boundary governance, and transparent model evaluation using bounded public datasets only.": "Pokala HealthIntel OS organizes public healthcare datasets, source-linked evidence, benchmark outputs, and claim boundaries inside a deployed intelligence workspace.",
    "Public data / HIT boundaries / transparent model benchmarks": "Public data / claim boundaries / transparent model benchmarks",
    "Healthcare intelligence workspace with evidence governance and transparent model evaluation.": "Healthcare intelligence workspace for evidence governance, data lineage, and model benchmarking.",

    # Command center
    "Enterprise public demo ? no-PHI evidence workspace": "Public-source healthcare intelligence workspace",
    "Enterprise public demo — no-PHI evidence workspace": "Public-source healthcare intelligence workspace",
    "HealthIntel OS turns public healthcare data into a structured decision brief: market motion,\n            reimbursement pressure, safety momentum, and evidence lineage. The product is intentionally\n            accountless, public-data-only, and safe for recruiter/researcher review.": "HealthIntel OS turns public healthcare data into a structured decision brief: market motion, reimbursement pressure, safety momentum, and evidence lineage. The workspace is intentionally accountless, public-data-only, and bounded for public technical review.",
    "safe for recruiter/researcher review": "bounded for public technical review",
    "Public demo posture": "Deployment posture",
    "Enterprise feel without accounts or PHI.": "Product-grade posture without accounts or PHI.",
    "This is a public, no-login artifact. The enterprise posture comes from transparency, lineage,\n            model boundaries, system status, and exportable evidence?not user accounts.": "This is a public, no-login workspace. The product posture comes from transparency, lineage, model boundaries, system status, and exportable evidence, not user accounts.",
    "This is a public, no-login artifact.": "This is a public, no-login workspace.",
    "evidence?not user accounts": "evidence, not user accounts",
    "D1 demo API": "D1-backed API",

    # Executive brief
    "A browser-native healthcare intelligence SaaS that converts public evidence into market, safety, reimbursement, and AI-risk dossiers. It demonstrates platform engineering, health data engineering, and applied AI architecture without PHI, paid APIs, or a hosted backend bill.": "A browser-native healthcare intelligence workspace that converts public evidence into market, safety, reimbursement, and AI-risk dossiers. It combines platform engineering, healthcare data engineering, and applied model governance without PHI or clinical decision-support claims.",

    # Data / benchmark JSON
    "public-demo summary marts; raw source snapshots not yet committed": "public summary marts; raw source snapshots not yet committed",
    "public demo mart": "public mart",
    "Real sklearn MLP baseline with early stopping; one seed only, not final DL claim.": "Real sklearn MLP baseline with early stopping; one seed only, not a final model claim.",
}

def update_file(path: Path):
    if not path.exists():
        return False

    before = path.read_text(encoding="utf-8", errors="ignore")
    after = before

    for old, new in REPLACEMENTS.items():
        after = after.replace(old, new)

    # Remove leftover portfolio/recruiter language if it appears in variants.
    after = after.replace("recruiter package", "review package")
    after = after.replace("recruiter summary", "system summary")
    after = after.replace("recruiter/researcher", "technical")
    after = after.replace("portfolio artifact", "deployed workspace")
    after = after.replace("technical signal", "technical depth")
    after = after.replace("DL maturity", "benchmark maturity")
    after = after.replace("DL benchmark", "model benchmark")
    after = after.replace("DL evaluation", "model benchmarking")
    after = after.replace("SaaS", "workspace")
    after = after.replace("mvp", "workspace")
    after = after.replace("MVP", "workspace")

    if after != before:
        path.write_text(after, encoding="utf-8", newline="\n")
        return True

    return False

changed = []

for path in FILES:
    if update_file(path):
        changed.append(str(path.relative_to(REPO)).replace("\\", "/"))

if INDEX.exists():
    before = INDEX.read_text(encoding="utf-8", errors="ignore")
    after = before.replace(
        "Browser-native healthcare intelligence SaaS built from public evidence, temporal signals, and zero-PHI architecture.",
        "Browser-native healthcare intelligence workspace for public evidence, data lineage, and transparent model benchmarking."
    )
    if after != before:
        INDEX.write_text(after, encoding="utf-8", newline="\n")
        changed.append(str(INDEX.relative_to(REPO)).replace("\\", "/"))

if not CSS.exists():
    raise SystemExit("Missing global.css")

css = CSS.read_text(encoding="utf-8", errors="ignore")
marker = "/* === App Workspace Layout Reset v2 === */"
if marker in css:
    css = css[:css.index(marker)].rstrip()

css += r"""

/* === App Workspace Layout Reset v2 === */

:root {
  --app-ink: #07111f;
  --app-muted: #435166;
  --app-soft: #64748b;
  --app-line: rgba(15, 23, 42, 0.11);
  --app-card: rgba(255, 255, 255, 0.96);
  --app-panel: #f8fafc;
  --app-shadow: 0 16px 42px rgba(15, 23, 42, 0.07);
}

body {
  color: var(--app-ink);
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
}

.mainSurface {
  width: min(1220px, calc(100% - 48px));
  padding: 26px 0 64px;
}

.topbar {
  min-height: 76px;
  padding: 14px 28px;
  background: rgba(248, 250, 252, 0.94);
  border-bottom: 1px solid var(--app-line);
}

.brandMark {
  width: 40px;
  height: 40px;
  border-radius: 14px;
}

.brand span {
  color: var(--app-ink);
  font-size: 13px;
  font-weight: 950;
  letter-spacing: -0.015em;
  text-transform: none;
}

.brand strong {
  color: var(--app-muted);
  font-size: 12px;
  font-weight: 760;
  letter-spacing: 0;
}

.navPills {
  border-radius: 18px;
  padding: 5px;
}

.navPills button {
  min-height: 36px;
  border-radius: 13px;
  font-size: 12px;
  font-weight: 850;
}

.trustPills span,
.chipRow span {
  min-height: 29px;
  border-radius: 10px;
  padding: 0 10px;
  font-size: 11px;
  font-weight: 820;
  background: rgba(255, 255, 255, 0.86);
}

.workspaceIntro {
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 18px;
  margin-bottom: 18px;
}

.workspaceIntro h1 {
  max-width: 900px;
  margin-top: 8px;
  font-size: clamp(34px, 4.6vw, 58px);
  line-height: 0.98;
  letter-spacing: -0.062em;
}

.workspaceIntro aside {
  min-height: auto;
  align-content: center;
  border-radius: 22px;
  padding: 20px;
  background:
    radial-gradient(circle at 0% 0%, rgba(37, 99, 235, 0.10), transparent 16rem),
    rgba(255, 255, 255, 0.94);
  box-shadow: var(--app-shadow);
}

.workspaceIntro aside strong {
  font-size: 17px;
  line-height: 1.22;
  letter-spacing: -0.03em;
}

.heroGrid {
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 16px;
}

.heroPrimary {
  padding: clamp(24px, 2.7vw, 34px);
}

.heroPrimary h1 {
  max-width: 780px;
  font-size: clamp(34px, 4.3vw, 56px);
  line-height: 0.98;
  letter-spacing: -0.06em;
}

.heroPrimary p {
  max-width: 760px;
  color: var(--app-muted);
  font-size: 15.5px;
  line-height: 1.58;
  font-weight: 640;
}

.advancedPanel {
  min-height: auto;
  padding: 22px;
  border-radius: 24px;
  background: linear-gradient(180deg, #172033, #0f172a);
}

.advancedPanel strong {
  font-size: clamp(24px, 2.5vw, 34px);
  line-height: 1.02;
  letter-spacing: -0.052em;
}

.advancedPanel p {
  font-size: 14px;
  line-height: 1.58;
}

.sectionIntro {
  padding: clamp(22px, 2.4vw, 30px);
  border-radius: 24px;
}

.sectionIntro h2 {
  max-width: 820px;
  font-size: clamp(28px, 3.1vw, 42px);
  line-height: 1.04;
  letter-spacing: -0.052em;
}

.sectionIntro p {
  max-width: 820px;
  color: var(--app-muted);
  font-size: 15.5px;
  line-height: 1.58;
}

.heroPanel,
.advancedPanel,
.sectionIntro,
.statCard,
.iconCard,
.modelCard,
.bentoTile,
.ledgerShell,
.sourceCard,
.architectureFlow article,
.twoPanel article,
.caseGrid article,
.benchmarkPanel {
  box-shadow: var(--app-shadow);
  border-color: var(--app-line);
}

.statGrid,
.skillsGrid,
.modelGrid,
.sourceGrid,
.caseGrid {
  gap: 14px;
}

.statCard,
.iconCard,
.modelCard,
.sourceCard,
.caseGrid article {
  padding: 18px;
  border-radius: 22px;
}

.statCard strong {
  font-size: clamp(26px, 2.5vw, 36px);
  letter-spacing: -0.052em;
}

.iconCard strong,
.modelCard strong,
.sourceCard strong,
.caseGrid strong {
  letter-spacing: -0.04em;
}

.iconCard p,
.statCard p,
.modelCard p,
.sourceCard p,
.caseGrid p,
.ledgerDetail p,
.twoPanel p,
.architectureFlow p {
  color: var(--app-muted);
  font-weight: 620;
  line-height: 1.55;
}

.actionRow button {
  min-height: 42px;
  border-radius: 13px;
  padding: 0 15px;
  font-size: 12px;
}

@media (max-width: 1100px) {
  .workspaceIntro,
  .heroGrid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .mainSurface {
    width: min(100% - 28px, 1220px);
    padding-top: 18px;
  }

  .workspaceIntro h1,
  .heroPrimary h1 {
    font-size: clamp(34px, 10vw, 48px);
    line-height: 1;
  }
}
"""

CSS.write_text(css, encoding="utf-8", newline="\n")
changed.append(str(CSS.relative_to(REPO)).replace("\\", "/"))

BAD_TERMS = [
    "recruiter",
    "Reviewer takeaway",
    "Reviewer signal",
    "portfolio artifact",
    "technical signal",
    "HIT maturity",
    "judgment",
    "restraint",
    "DL benchmark",
    "DL evaluation",
    "SaaS",
    "mvp",
    "MVP",
    "Deployed demo",
    "Portfolio case study",
]

scan_paths = [
    REPO / "apps" / "web" / "src" / "app" / "App.tsx",
    REPO / "apps" / "web" / "src" / "modules" / "command-center" / "CommandCenter.tsx",
    REPO / "apps" / "web" / "src" / "modules" / "executive-brief" / "ExecutiveBrief.tsx",
]

findings = []
for path in scan_paths:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for term in BAD_TERMS:
        if term in text:
            findings.append(f"{path.relative_to(REPO)} :: {term}")

if findings:
    print("BAD_PRODUCT_COPY_REMAINS")
    for item in findings:
        print(item)
    raise SystemExit(2)

print("Product-grade copy and layout reset applied.")
print("Changed files:")
for item in sorted(set(changed)):
    print("-", item)