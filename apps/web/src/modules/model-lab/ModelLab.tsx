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
  if (value === null || value === undefined) return '?';
  if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(4);
  if (Array.isArray(value)) return value.join(', ');
  return String(value);
}

function metric(row: AnyRecord, key: string) {
  const value = row?.[key];
  if (value === null || value === undefined) return '?';
  return typeof value === 'number' ? value.toFixed(4) : String(value);
}

function leaderboardRows() {
  const rows = Array.isArray(card.leaderboard) ? card.leaderboard : [];
  return rows.slice(0, 10);
}

export function ModelLab({ snapshot }: { snapshot?: IntelligenceSnapshot }) {
  const rows = leaderboardRows();
  const bestModel = card.best_model_by_rmse ?? card.best_model_by_roc_auc ?? card.best_model ?? 'Not reported';
  const target = card.target ?? manifest.target ?? 'target_next_composite_opportunity';
  const boundary = card.boundary ?? manifest.boundary ?? manifest.source_boundary ?? 'Bounded public-source model artifact.';

  return (
    <section className="gridPage modelLab">
      <Panel span={12} title="Temporal Model Lab" eyebrow="Artifact-backed benchmark" icon={Brain}>
        <div className="modelHero">
          <div>
            <span className="sectionKicker">Run artifact</span>
            <h2>{card.run_id ?? 'Enterprise temporal run'}</h2>
            <p>{boundary}</p>
          </div>

          <div className="modelHeroStats">
            <article>
              <span>Best model</span>
              <strong>{fmt(bestModel)}</strong>
            </article>
            <article>
              <span>Device</span>
              <strong>{fmt(card.device ?? 'unknown')}</strong>
            </article>
            <article>
              <span>CUDA</span>
              <strong>{card.cuda_available ? 'available' : 'not available'}</strong>
            </article>
          </div>
        </div>
      </Panel>

      <Panel span={4} title="Training frame" eyebrow="Scale" icon={Database}>
        <div className="metricList">
          <article><span>Rows</span><strong>{fmt(card.training_rows ?? manifest.rows)}</strong></article>
          <article><span>Windows</span><strong>{fmt(card.windows)}</strong></article>
          <article><span>Train windows</span><strong>{fmt(card.train_windows)}</strong></article>
          <article><span>Validation windows</span><strong>{fmt(card.val_windows)}</strong></article>
          <article><span>Test windows</span><strong>{fmt(card.test_windows)}</strong></article>
          <article><span>Entities</span><strong>{fmt(card.entities ?? manifest.entities)}</strong></article>
          <article><span>Periods</span><strong>{fmt(card.periods ?? manifest.periods)}</strong></article>
          <article><span>Feature count</span><strong>{fmt(card.feature_count ?? manifest.feature_count ?? manifest.feature_columns?.length)}</strong></article>
        </div>
      </Panel>

      <Panel span={4} title="Model setup" eyebrow="Run design" icon={Cpu}>
        <div className="metricList">
          <article><span>Target</span><strong>{fmt(target)}</strong></article>
          <article><span>Window</span><strong>{fmt(card.window)}</strong></article>
          <article><span>Horizon</span><strong>{fmt(card.horizon ?? 'next period')}</strong></article>
          <article><span>Epochs</span><strong>{fmt(card.epochs)}</strong></article>
          <article><span>Seeds</span><strong>{fmt(card.seeds)}</strong></article>
          <article><span>Split</span><strong>{fmt(card.split?.type)}</strong></article>
        </div>
      </Panel>

      <Panel span={4} title="Claim boundary" eyebrow="Safety" icon={ShieldCheck}>
        <div className="boundaryList">
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
        <div className="modelTableWrap">
          <table className="modelTable">
            <thead>
              <tr>
                <th>Model</th>
                <th>Seed</th>
                <th>RMSE</th>
                <th>MAE</th>
                <th>ROC-AUC</th>
                <th>PR-AUC</th>
                <th>F1</th>
                <th>Directional / Balanced Acc.</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row: AnyRecord, index: number) => (
                <tr key={`${row.model ?? 'model'}-${row.seed ?? index}-${index}`}>
                  <td>{fmt(row.model)}</td>
                  <td>{fmt(row.seed)}</td>
                  <td>{metric(row, 'rmse')}</td>
                  <td>{metric(row, 'mae')}</td>
                  <td>{metric(row, 'roc_auc')}</td>
                  <td>{metric(row, 'pr_auc')}</td>
                  <td>{metric(row, 'f1')}</td>
                  <td>{metric(row, 'directional_accuracy') !== '?' ? metric(row, 'directional_accuracy') : metric(row, 'balanced_accuracy')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel span={12} title="Run history" eyebrow="Reproducibility">
        <div className="runHistoryLine">
          <span>{runHistory.length} saved run{runHistory.length === 1 ? '' : 's'}</span>
          <span>Latest: {fmt((runHistory.length ? runHistory[runHistory.length - 1]?.run_id : card.run_id))}</span>
          <span>Generated: {fmt(card.generated_at ?? manifest.generated_at)}</span>
        </div>
      </Panel>
    </section>
  );
}

