import { Brain, Cpu, Database, GitBranch, ShieldCheck } from 'lucide-react';
import { Panel } from '../../components/Panel';
import modelCardRaw from '../../data/enterprise_model_card.json';
import featureManifestRaw from '../../data/enterprise_temporal_manifest.json';
import runHistoryRaw from '../../data/enterprise_run_history.json';
import type { IntelligenceSnapshot } from '../../types/intelligence';

type AnyRecord = Record<string, any>;

const card = modelCardRaw as AnyRecord;
const manifest = featureManifestRaw as AnyRecord;
const runHistory = runHistoryRaw as AnyRecord[];

function fmt(value: unknown) {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(4);
  if (Array.isArray(value)) return value.join(', ');
  return String(value);
}

function metric(row: AnyRecord, key: string) {
  const value = row?.[key];
  if (value === null || value === undefined || value === '') return '—';
  return typeof value === 'number' ? value.toFixed(4) : String(value);
}

function topRows() {
  const rows = Array.isArray(card.leaderboard) ? card.leaderboard : [];
  return rows.slice(0, 8);
}

function latestRunId() {
  if (!Array.isArray(runHistory) || runHistory.length === 0) return card.run_id;
  return runHistory[runHistory.length - 1]?.run_id ?? card.run_id;
}

function bestRow() {
  const rows = topRows();
  return rows.length ? rows[0] : {};
}

export function ModelLab({ snapshot }: { snapshot?: IntelligenceSnapshot }) {
  const rows = topRows();
  const best = bestRow();

  const bestModel = card.best_model_by_rmse ?? card.best_model_by_roc_auc ?? best.model ?? 'Not reported';
  const target = card.target ?? manifest.target ?? 'target_next_composite_opportunity';
  const boundary = card.boundary ?? manifest.boundary ?? manifest.source_boundary ?? 'Bounded public-source model artifact.';

  return (
    <section className="gridPage modelLab modelLabPolished">
      <Panel span={12} title="V4 Shock Benchmark" eyebrow="Benchmark Lab" icon={Brain}>
        <div className="modelVerdict">
          <div className="modelVerdictCopy">
            <span className="sectionKicker">Artifact-backed benchmark</span>
            <h2>{fmt(card.run_id ?? 'Enterprise temporal run')}</h2>
            <p>{boundary}</p>

            <div className="verdictBanner">
              <strong>Honest read</strong>
              <span>
                The harder v4 shock target is live. Best reported run is a temporal transformer, but the signal is still weak-to-moderate. Treat this as an experimental public-source benchmark, not a validated prediction engine.
              </span>
            </div>
          </div>

          <div className="modelScoreboard">
            <article>
              <span>Best model</span>
              <strong>{fmt(bestModel)}</strong>
            </article>
            <article>
              <span>Best ROC-AUC</span>
              <strong>{metric(best, 'roc_auc')}</strong>
            </article>
            <article>
              <span>Best PR-AUC</span>
              <strong>{metric(best, 'pr_auc')}</strong>
            </article>
            <article>
              <span>Best F1</span>
              <strong>{metric(best, 'f1')}</strong>
            </article>
          </div>
        </div>
      </Panel>

      <Panel span={4} title="Training frame" eyebrow="Scale" icon={Database}>
        <div className="modelMetricGrid">
          <article><span>Rows</span><strong>{fmt(card.training_rows ?? manifest.rows)}</strong></article>
          <article><span>Windows</span><strong>{fmt(card.windows)}</strong></article>
          <article><span>Train</span><strong>{fmt(card.train_windows)}</strong></article>
          <article><span>Validation</span><strong>{fmt(card.val_windows)}</strong></article>
          <article><span>Test</span><strong>{fmt(card.test_windows)}</strong></article>
          <article><span>Features</span><strong>{fmt(card.feature_count ?? manifest.feature_count ?? manifest.feature_columns?.length)}</strong></article>
        </div>
      </Panel>

      <Panel span={4} title="Run design" eyebrow="Target" icon={Cpu}>
        <div className="runDesignStack">
          <article>
            <span>Target</span>
            <strong>{fmt(target)}</strong>
          </article>
          <article>
            <span>Task type</span>
            <strong>Classification / shock detection</strong>
          </article>
          <article>
            <span>Window / horizon</span>
            <strong>{fmt(card.window)} / {fmt(card.horizon ?? 'next')}</strong>
          </article>
          <article>
            <span>Seeds</span>
            <strong>{fmt(card.seeds)}</strong>
          </article>
          <article>
            <span>Device</span>
            <strong>{fmt(card.device)} / CUDA {card.cuda_available ? 'available' : 'off'}</strong>
          </article>
        </div>
      </Panel>

      <Panel span={4} title="Claim boundary" eyebrow="Safety" icon={ShieldCheck}>
        <div className="boundaryList compactBoundary">
          {(card.claim_boundary ?? [
            'No PHI or patient-level records.',
            'Public-source bounded marts only.',
            'Not clinical decision support.',
            'Not causal validation.'
          ]).map((item: string) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </Panel>

      <Panel span={12} title="Leaderboard" eyebrow="Top reported runs" icon={GitBranch}>
        <div className="leaderboardNote">
          Classification runs use ROC-AUC, PR-AUC, F1, precision, recall, and balanced accuracy. RMSE/MAE are intentionally removed for v4.
        </div>

        <div className="modelTableWrap">
          <table className="modelTable polishedTable">
            <thead>
              <tr>
                <th>Model</th>
                <th>Seed</th>
                <th>ROC-AUC</th>
                <th>PR-AUC</th>
                <th>F1</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>Balanced Acc.</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row: AnyRecord, index: number) => (
                <tr key={`${row.model ?? 'model'}-${row.seed ?? index}-${index}`}>
                  <td>
                    <strong>{fmt(row.model)}</strong>
                    <small>{row.kind ? fmt(row.kind) : '—'}</small>
                  </td>
                  <td>{fmt(row.seed)}</td>
                  <td>{metric(row, 'roc_auc')}</td>
                  <td>{metric(row, 'pr_auc')}</td>
                  <td>{metric(row, 'f1')}</td>
                  <td>{metric(row, 'precision')}</td>
                  <td>{metric(row, 'recall')}</td>
                  <td>{metric(row, 'balanced_accuracy')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel span={12} title="Run history" eyebrow="Reproducibility">
        <div className="runHistoryLine">
          <span>{runHistory.length} saved run{runHistory.length === 1 ? '' : 's'}</span>
          <span>Latest: {fmt(latestRunId())}</span>
          <span>Generated: {fmt(card.generated_at ?? manifest.generated_at)}</span>
          <span>Source: public, no-PHI artifact path</span>
        </div>
      </Panel>
    </section>
  );
}

