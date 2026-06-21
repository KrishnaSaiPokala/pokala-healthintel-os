from pathlib import Path

repo = Path(r"C:\Users\Event\PycharmProjects\HealthIntel_OS\pokala-healthintel-os")
path = repo / "apps" / "web" / "src" / "modules" / "model-lab" / "ModelLab.tsx"

text = path.read_text(encoding="utf-8")

if "deep_benchmark_overnight.json" not in text:
    text = text.replace(
        "import runHistoryRaw from '../../data/enterprise_run_history.json';",
        "import runHistoryRaw from '../../data/enterprise_run_history.json';\nimport overnightBenchmarkRaw from '../../data/deep_benchmark_overnight.json';"
    )

if "const overnightBenchmark = overnightBenchmarkRaw as AnyRecord;" not in text:
    text = text.replace(
        "const runHistory = runHistoryRaw as AnyRecord[];",
        "const runHistory = runHistoryRaw as AnyRecord[];\nconst overnightBenchmark = overnightBenchmarkRaw as AnyRecord;"
    )

helper = r'''
function overnightModels() {
  return Array.isArray(overnightBenchmark.models) ? overnightBenchmark.models : [];
}

function summaryMetric(row: AnyRecord, key: string) {
  const value = row?.summary?.[key]?.mean;
  if (value === null || value === undefined || value === '') return '—';
  return typeof value === 'number' ? value.toFixed(4) : String(value);
}

function completedSeeds(row: AnyRecord) {
  return row?.summary?.completed_seeds ?? row?.per_seed?.length ?? '—';
}

function failedSeeds(row: AnyRecord) {
  return row?.summary?.failed_seeds ?? 0;
}

function bestOvernightModel() {
  const models = overnightModels();
  return models
    .filter((row: AnyRecord) => typeof row?.summary?.roc_auc?.mean === 'number')
    .sort((a: AnyRecord, b: AnyRecord) => b.summary.roc_auc.mean - a.summary.roc_auc.mean)[0];
}
'''

if "function overnightModels()" not in text:
    text = text.replace(
        "function bestRow() {\n  const rows = topRows();\n  return rows.length ? rows[0] : {};\n}\n",
        "function bestRow() {\n  const rows = topRows();\n  return rows.length ? rows[0] : {};\n}\n" + helper + "\n"
    )

if "const overnightRows = overnightModels();" not in text:
    text = text.replace(
        "  const rows = topRows();\n  const best = bestRow();",
        "  const rows = topRows();\n  const best = bestRow();\n  const overnightRows = overnightModels();\n  const overnightBest = bestOvernightModel() ?? {};"
    )

panel = r'''
      <Panel span={12} title="Overnight Core DL Benchmark" eyebrow="210-run multi-seed suite" icon={Cpu}>
        <div className="modelVerdict overnightBenchmarkPanel">
          <div className="modelVerdictCopy">
            <span className="sectionKicker">Committed benchmark artifact</span>
            <h2>{fmt(overnightBest.model_id ?? '10 model families / 21 seeds each')}</h2>
            <p>
              Overnight benchmark completed across {fmt(overnightRows.length)} model families and {fmt((overnightRows.length || 0) * 21)} seed runs on {fmt(overnightBenchmark.source_dataset)}.
              The target is {fmt(overnightBenchmark.target_column)} with {fmt(overnightBenchmark.dataset?.rows_after_class_filter)} rows and {fmt(overnightBenchmark.dataset?.feature_count)} engineered features.
            </p>

            <div className="verdictBanner">
              <strong>Best mean ROC-AUC</strong>
              <span>
                {fmt(overnightBest.model_id)} reported mean ROC-AUC {summaryMetric(overnightBest, 'roc_auc')} across {fmt(completedSeeds(overnightBest))} completed seeds.
                These are benchmark signals only: no PHI, not clinical decision support, and not a patient-level prediction claim.
              </span>
            </div>
          </div>

          <div className="modelScoreboard">
            <article>
              <span>Model families</span>
              <strong>{fmt(overnightRows.length)}</strong>
            </article>
            <article>
              <span>Completed runs</span>
              <strong>{fmt(overnightRows.reduce((sum: number, row: AnyRecord) => sum + Number(completedSeeds(row) || 0), 0))}</strong>
            </article>
            <article>
              <span>Failed runs</span>
              <strong>{fmt(overnightRows.reduce((sum: number, row: AnyRecord) => sum + Number(failedSeeds(row) || 0), 0))}</strong>
            </article>
            <article>
              <span>Best ROC-AUC</span>
              <strong>{summaryMetric(overnightBest, 'roc_auc')}</strong>
            </article>
          </div>
        </div>

        <div className="leaderboardNote">
          Overnight suite includes sklearn MLP, PyTorch MLP, residual MLP, wide-deep MLP, LSTM, GRU, TCN-style Conv1D, Transformer Encoder, CNN-MLP hybrid, and gated MLP. Sequence-family models are architecture benchmarks over single-step tabular tensors until a future phase constructs true temporal tensors.
        </div>

        <div className="modelTableWrap">
          <table className="modelTable polishedTable">
            <thead>
              <tr>
                <th>Model family</th>
                <th>Framework</th>
                <th>Seeds</th>
                <th>ROC-AUC mean</th>
                <th>PR-AUC mean</th>
                <th>F1 mean</th>
                <th>Balanced Acc.</th>
                <th>Runtime mean</th>
              </tr>
            </thead>
            <tbody>
              {overnightRows.map((row: AnyRecord) => (
                <tr key={row.model_id}>
                  <td>
                    <strong>{fmt(row.model_id)}</strong>
                    <small>{fmt(row.model_family)}</small>
                  </td>
                  <td>{fmt(row.framework)}</td>
                  <td>{fmt(completedSeeds(row))} / 21</td>
                  <td>{summaryMetric(row, 'roc_auc')}</td>
                  <td>{summaryMetric(row, 'pr_auc')}</td>
                  <td>{summaryMetric(row, 'f1_macro')}</td>
                  <td>{summaryMetric(row, 'balanced_accuracy')}</td>
                  <td>{row?.summary?.runtime_seconds?.mean ? `${row.summary.runtime_seconds.mean}s` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

'''

if "title=\"Overnight Core DL Benchmark\"" not in text:
    anchor = "      <Panel span={4} title=\"Training frame\" eyebrow=\"Scale\" icon={Database}>"
    if anchor not in text:
        raise SystemExit("Could not find Training frame anchor in ModelLab.tsx")
    text = text.replace(anchor, panel + anchor)

path.write_text(text, encoding="utf-8", newline="\n")
print("Patched ModelLab with overnight benchmark panel.")