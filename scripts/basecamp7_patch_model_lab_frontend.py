#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APP = REPO / "apps" / "web" / "src" / "app" / "App.tsx"
CSS = REPO / "apps" / "web" / "src" / "styles" / "global.css"

app = APP.read_text(encoding="utf-8")

if "model_benchmark.json" not in app:
    app = app.replace(
        "import rawSnapshot from '../data/intelligence.json';",
        "import rawSnapshot from '../data/intelligence.json';\nimport modelBenchmark from '../data/model_benchmark.json';"
    )

new_model_lab = '''function ModelLab() {
  const benchmark = modelBenchmark as any;
  const baselineRows = benchmark?.benchmark_results ?? [];
  const deepRows = benchmark?.deep_results ?? [];
  const plannedRows = benchmark?.planned_deep_models ?? [];

  return (
    <div className="pageStack">
      <SectionIntro icon={BrainCircuit} eyebrow="Model Lab" title="Real benchmark outputs are now connected to the public interface.">
        Basecamp7 syncs actual Basecamp6 baseline results into the frontend and adds a first MLP baseline attempt with early stopping.
        The model layer remains a research benchmark, not validated forecasting.
      </SectionIntro>

      <section className="modelGrid">
        {modelMetrics.map((metric) => (
          <article className="modelCard" key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <p>{metric.note}</p>
          </article>
        ))}
      </section>

      <section className="benchmarkPanel">
        <div className="benchmarkHeader">
          <div>
            <span className="eyebrow"><BarChart3 size={15} /> Synced benchmark table</span>
            <h2>Baseline and early neural results</h2>
            <p>
              Dataset: <strong>{benchmark?.dataset_used ?? 'not available'}</strong> / Target:{' '}
              <strong>{benchmark?.target_used ?? 'not available'}</strong>
            </p>
          </div>
          <aside>
            <span>Run</span>
            <strong>{benchmark?.run_id ?? 'basecamp7_model_lab_sync'}</strong>
          </aside>
        </div>

        <div className="benchmarkTable">
          <div className="benchmarkRow benchmarkHead">
            <span>Model</span><span>Status</span><span>ROC-AUC</span><span>PR-AUC</span><span>Balanced acc.</span><span>F1</span><span>Notes</span>
          </div>
          {[...baselineRows, ...deepRows].map((row: any) => {
            const m = row.metrics ?? {};
            return (
              <div className="benchmarkRow" key={`${row.model}-${row.status}`}>
                <strong>{row.model}</strong>
                <span>{row.status}</span>
                <span>{formatMetric(m.roc_auc)}</span>
                <span>{formatMetric(m.pr_auc)}</span>
                <span>{formatMetric(m.balanced_accuracy)}</span>
                <span>{formatMetric(m.f1)}</span>
                <p>{row.notes}</p>
              </div>
            );
          })}
        </div>
      </section>

      <section className="twoPanel">
        <article>
          <span className="eyebrow"><BrainCircuit size={15} /> Next deep models</span>
          <h2>LSTM, GRU, TCN, transformers</h2>
          <p>{plannedRows.join(' / ')}</p>
        </article>
        <article className="warningPanel">
          <span className="eyebrow"><ShieldAlert size={15} /> Boundary</span>
          <h2>Research benchmark only</h2>
          <p>{benchmark?.claim_boundary ?? 'No PHI. Not clinical decision support. No patient-level prediction.'}</p>
        </article>
      </section>
    </div>
  );
}

function formatMetric(value: unknown) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '-';
  return value.toFixed(3);
}

'''

pattern = r"function ModelLab\(\) \{.*?\n\}\n\nfunction DataHealth\("
if not re.search(pattern, app, flags=re.S):
    raise SystemExit("Could not find ModelLab block to replace. App.tsx structure changed.")

app = re.sub(pattern, new_model_lab + "\nfunction DataHealth(", app, flags=re.S)
APP.write_text(app, encoding="utf-8")

css = CSS.read_text(encoding="utf-8")
addition = '''

.benchmarkPanel {
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 55px rgba(15, 23, 42, 0.07);
  overflow: hidden;
}

.benchmarkHeader {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 16px;
  padding: 22px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.benchmarkHeader h2 {
  margin: 10px 0 8px;
  color: #020617;
  font-size: 34px;
  line-height: 0.98;
  letter-spacing: -0.055em;
}

.benchmarkHeader p {
  margin: 0;
  color: #475569;
  font-weight: 720;
}

.benchmarkHeader aside {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 20px;
  padding: 16px;
  background: #f8fafc;
}

.benchmarkHeader aside span {
  display: block;
  color: #64748b;
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.benchmarkHeader aside strong {
  display: block;
  margin-top: 8px;
  color: #0f172a;
  overflow-wrap: anywhere;
}

.benchmarkTable { display: grid; }

.benchmarkRow {
  display: grid;
  grid-template-columns: 1.15fr 0.7fr 0.65fr 0.65fr 0.8fr 0.55fr minmax(220px, 1.5fr);
  gap: 12px;
  align-items: start;
  padding: 14px 18px;
  border-top: 1px solid rgba(15, 23, 42, 0.06);
}

.benchmarkRow span,
.benchmarkRow p {
  margin: 0;
  color: #475569;
  font-size: 12px;
  line-height: 1.4;
  font-weight: 720;
}

.benchmarkRow strong {
  color: #020617;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.benchmarkHead {
  border-top: 0;
  background: #0f172a;
}

.benchmarkHead span {
  color: white;
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

@media (max-width: 1160px) {
  .benchmarkHeader, .benchmarkRow { grid-template-columns: 1fr; }
}
'''
if ".benchmarkPanel" not in css:
    css += addition
CSS.write_text(css, encoding="utf-8")

print("Patched App.tsx Model Lab and appended benchmark styles.")
