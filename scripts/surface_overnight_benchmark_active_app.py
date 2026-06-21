from pathlib import Path

repo = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")
path = repo / "apps" / "web" / "src" / "app" / "App.tsx"

text = path.read_text(encoding="utf-8")

if "deep_benchmark_overnight.json" not in text:
    text = text.replace(
        "import modelBenchmark from '../data/model_benchmark.json';",
        "import modelBenchmark from '../data/model_benchmark.json';\nimport overnightBenchmarkRaw from '../data/deep_benchmark_overnight.json';"
    )

if "const overnightBenchmark = overnightBenchmarkRaw as any;" not in text:
    text = text.replace(
        "const snapshot = rawSnapshot as any;",
        "const snapshot = rawSnapshot as any;\nconst overnightBenchmark = overnightBenchmarkRaw as any;"
    )

helpers = r'''
function overnightModels() {
  return Array.isArray(overnightBenchmark?.models) ? overnightBenchmark.models : [];
}

function metricMean(row: any, key: string) {
  const value = row?.summary?.[key]?.mean;
  if (typeof value !== 'number' || Number.isNaN(value)) return '-';
  return value.toFixed(4);
}

function completedSeeds(row: any) {
  return Number(row?.summary?.completed_seeds ?? 0);
}

function failedSeeds(row: any) {
  return Number(row?.summary?.failed_seeds ?? 0);
}

function bestOvernightModel() {
  return overnightModels()
    .filter((row: any) => typeof row?.summary?.roc_auc?.mean === 'number')
    .sort((a: any, b: any) => b.summary.roc_auc.mean - a.summary.roc_auc.mean)[0] ?? {};
}
'''

if "function overnightModels()" not in text:
    text = text.replace(
        "function formatMetric(value: unknown) {\n  if (typeof value !== 'number' || Number.isNaN(value)) return '-';\n  return value.toFixed(3);\n}\n",
        "function formatMetric(value: unknown) {\n  if (typeof value !== 'number' || Number.isNaN(value)) return '-';\n  return value.toFixed(3);\n}\n\n" + helpers + "\n"
    )

old = """  const benchmark = modelBenchmark as any;
  const baselineRows = benchmark?.benchmark_results ?? [];
  const deepRows = benchmark?.deep_results ?? [];
  const plannedRows = benchmark?.planned_deep_models ?? [];
"""

new = """  const benchmark = modelBenchmark as any;
  const baselineRows = benchmark?.benchmark_results ?? [];
  const deepRows = benchmark?.deep_results ?? [];
  const plannedRows = benchmark?.planned_deep_models ?? [];
  const overnightRows = overnightModels();
  const overnightBest = bestOvernightModel();
  const overnightCompleted = overnightRows.reduce((sum: number, row: any) => sum + completedSeeds(row), 0);
  const overnightFailed = overnightRows.reduce((sum: number, row: any) => sum + failedSeeds(row), 0);
"""

if "const overnightRows = overnightModels();" not in text:
    text = text.replace(old, new)

panel = r'''
      <section className="benchmarkPanel">
        <div className="benchmarkHeader">
          <div>
            <span className="eyebrow"><BrainCircuit size={15} /> Overnight Core DL Benchmark</span>
            <h2>210 completed multi-seed model runs</h2>
            <p>
              Dataset: <strong>{overnightBenchmark?.source_dataset ?? 'not available'}</strong> / Target:{' '}
              <strong>{overnightBenchmark?.target_column ?? 'not available'}</strong>
            </p>
          </div>
          <aside>
            <span>Best mean ROC-AUC</span>
            <strong>{metricMean(overnightBest, 'roc_auc')}</strong>
          </aside>
        </div>

        <section className="modelGrid">
          <article className="modelCard">
            <span>Model families</span>
            <strong>{overnightRows.length}</strong>
            <p>sklearn MLP, PyTorch MLP variants, LSTM, GRU, TCN, Transformer, CNN hybrid, and gated MLP.</p>
          </article>
          <article className="modelCard">
            <span>Completed seed runs</span>
            <strong>{overnightCompleted}</strong>
            <p>21 seeds per model family, committed as a reproducible benchmark artifact.</p>
          </article>
          <article className="modelCard">
            <span>Failed seed runs</span>
            <strong>{overnightFailed}</strong>
            <p>Failure count from the overnight benchmark summary.</p>
          </article>
          <article className="modelCard">
            <span>Best model</span>
            <strong>{overnightBest?.model_id ?? '-'}</strong>
            <p>Best model selected by mean ROC-AUC across completed seeds.</p>
          </article>
        </section>

        <div className="benchmarkTable">
          <div className="benchmarkRow benchmarkHead">
            <span>Model</span><span>Family</span><span>Seeds</span><span>ROC-AUC</span><span>PR-AUC</span><span>F1 macro</span><span>Balanced acc.</span>
          </div>
          {overnightRows.map((row: any) => (
            <div className="benchmarkRow" key={row.model_id}>
              <strong>{row.model_id}</strong>
              <span>{row.model_family}</span>
              <span>{completedSeeds(row)} / 21</span>
              <span>{metricMean(row, 'roc_auc')}</span>
              <span>{metricMean(row, 'pr_auc')}</span>
              <span>{metricMean(row, 'f1_macro')}</span>
              <span>{metricMean(row, 'balanced_accuracy')}</span>
            </div>
          ))}
        </div>

        <div className="leaderboardNote">
          Boundary: benchmark signals only. No PHI. Not clinical decision support. No patient-level prediction claim.
          Sequence-family models are architecture benchmarks over single-step tabular tensors until a future phase constructs true temporal tensors.
        </div>
      </section>

'''

if "210 completed multi-seed model runs" not in text:
    anchor = "      <section className=\"modelGrid\">"
    if anchor not in text:
        raise SystemExit("Could not find active ModelLab modelGrid anchor in App.tsx")
    text = text.replace(anchor, panel + anchor, 1)

path.write_text(text, encoding="utf-8", newline="\n")
print("Patched ACTIVE App.tsx ModelLab with overnight benchmark.")