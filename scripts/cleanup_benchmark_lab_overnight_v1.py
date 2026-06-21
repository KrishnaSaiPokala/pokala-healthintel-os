from pathlib import Path
import re

repo = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")
app = repo / "apps" / "web" / "src" / "app" / "App.tsx"
css = repo / "apps" / "web" / "src" / "styles" / "global.css"

text = app.read_text(encoding="utf-8")

replacements = {
    "Transparent benchmark outputs are connected to the public interface.": "Core benchmark outputs are connected to the public interface.",
    "Benchmark Phase 7 syncs actual Benchmark Phase 6 baseline results into the frontend and adds a initial MLP baseline run with early stopping. The model layer remains a research benchmark, not validated forecasting.": "The Benchmark Lab now leads with the overnight multi-seed deep learning suite. Earlier baseline runs are retained below only as lineage context, not as the primary model claim.",
    "Committed benchmark artifact": "Committed benchmark suite",
    "21 seeds per model family, committed as a reproducible benchmark artifact.": "21 seeds per model family, committed as a reproducible benchmark suite.",
    "Synced benchmark table": "Legacy baseline snapshot",
    "Benchmark results": "Earlier exploratory results",
    "Run ID": "Legacy run ID",
    "Benchmark Phase4_shock_20260618_121556": "Phase 4 shock benchmark",
    "reproducible benchmark reference": "retained for lineage",
    "Temporal transformer classifier": "Earlier temporal benchmark candidate",
    "sequence benchmark candidate": "legacy sequence candidate",
    "weak/moderate benchmark": "legacy exploratory signal",
    "Research only": "Benchmark only",
    "not validated forecasting": "not a forecasting claim",
    "Real sklearn MLP baseline with early stopping; one seed only, not a final model claim.": "Earlier single-seed MLP baseline with early stopping; retained for lineage only, not a final model claim.",
    "Planned model extensions": "Next technical phase",
    "Sequence and transformer benchmarks": "True temporal tensors and retrieval layer",
    "Research benchmark only. No PHI. Not clinical decision support. No patient-level prediction.": "Benchmark only. No PHI. Not clinical decision support. No patient-level prediction claim.",
}

for old, new in replacements.items():
    text = text.replace(old, new)

# Make the old baseline section visually less primary by changing one likely title if present.
text = text.replace(
    '<section className="benchmarkPanel">',
    '<section className="benchmarkPanel primaryBenchmarkPanel">',
    1
)

# Change later benchmark panels to legacy class when they occur after the overnight panel.
first = text.find('primaryBenchmarkPanel')
if first != -1:
    before = text[:first + len('primaryBenchmarkPanel')]
    after = text[first + len('primaryBenchmarkPanel'):]
    after = after.replace('<section className="benchmarkPanel">', '<section className="benchmarkPanel legacyBenchmarkPanel">')
    text = before + after

app.write_text(text, encoding="utf-8", newline="\n")

css_text = css.read_text(encoding="utf-8", errors="ignore")
marker = "/* === Benchmark Lab Overnight Cleanup v1 === */"
if marker in css_text:
    css_text = css_text[:css_text.index(marker)].rstrip()

css_text += r"""

/* === Benchmark Lab Overnight Cleanup v1 === */

.primaryBenchmarkPanel {
  border: 1px solid rgba(37, 99, 235, 0.18);
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.09), transparent 24rem),
    rgba(255, 255, 255, 0.97);
}

.legacyBenchmarkPanel {
  margin-top: 18px;
  opacity: 0.86;
  background: rgba(248, 250, 252, 0.92);
}

.legacyBenchmarkPanel .benchmarkHeader h2::after {
  content: " / retained for lineage";
  color: #64748b;
  font-weight: 700;
}

.benchmarkTable {
  width: 100%;
  overflow-x: auto;
  border: 1px solid rgba(15, 23, 42, 0.10);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.94);
}

.benchmarkRow {
  display: grid;
  grid-template-columns: minmax(220px, 1.8fr) minmax(130px, 1fr) 92px 108px 108px 108px 118px;
  gap: 14px;
  align-items: center;
  min-width: 980px;
  padding: 13px 16px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.075);
  font-size: 13px;
}

.benchmarkRow:last-child {
  border-bottom: 0;
}

.benchmarkHead {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f8fafc;
  color: #475569;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.055em;
  text-transform: uppercase;
}

.benchmarkRow strong {
  color: #0f172a;
  font-weight: 900;
  overflow-wrap: anywhere;
}

.benchmarkRow span {
  color: #334155;
  font-weight: 700;
}

.primaryBenchmarkPanel .modelGrid {
  margin-top: 18px;
}

.primaryBenchmarkPanel .modelCard strong {
  overflow-wrap: anywhere;
}

.leaderboardNote {
  margin-top: 16px;
  border-radius: 16px;
  padding: 14px 16px;
  background: rgba(15, 23, 42, 0.045);
  color: #475569;
  font-size: 13px;
  font-weight: 650;
  line-height: 1.55;
}

@media (max-width: 800px) {
  .benchmarkRow {
    grid-template-columns: minmax(210px, 1.8fr) minmax(120px, 1fr) 80px 95px 95px 95px 105px;
    min-width: 900px;
  }
}
"""

css.write_text(css_text, encoding="utf-8", newline="\n")

print("Benchmark Lab cleanup applied.")