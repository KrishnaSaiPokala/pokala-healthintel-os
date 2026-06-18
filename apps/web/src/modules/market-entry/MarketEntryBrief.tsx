import { AlertTriangle, CheckCircle2, Database, FileSearch, Gauge, MapPinned, ShieldCheck } from 'lucide-react';
import { Panel } from '../../components/Panel';
import modelCardRaw from '../../data/enterprise_model_card.json';
import featureManifestRaw from '../../data/enterprise_temporal_manifest.json';
import type { IntelligenceSnapshot } from '../../types/intelligence';

type AnyRecord = Record<string, any>;

const modelCard = modelCardRaw as AnyRecord;
const manifest = featureManifestRaw as AnyRecord;

function fmt(value: unknown) {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(4);
  if (Array.isArray(value)) return value.join(', ');
  return String(value);
}

const best = Array.isArray(modelCard.leaderboard) && modelCard.leaderboard.length
  ? modelCard.leaderboard[0]
  : {};

export function MarketEntryBrief({ snapshot }: { snapshot?: IntelligenceSnapshot }) {
  return (
    <section className="gridPage marketBrief">
      <Panel span={12} title="Texas Radiology AI Market Entry Brief" eyebrow="Flagship decision memo" icon={MapPinned}>
        <div className="briefHero">
          <div>
            <span className="sectionKicker">Decision</span>
            <h2>Cautiously favorable — investigate entry, do not claim predictive certainty.</h2>
            <p>
              The current public-source evidence supports continued diligence for a Texas radiology AI workflow entry thesis.
              The strongest product value is not the model alone; it is the combined evidence ledger across provider density,
              trial momentum, safety pressure, reimbursement context, and transparent model weakness.
            </p>
          </div>

          <div className="briefDecisionCard">
            <span>Recommendation</span>
            <strong>Investigate entry</strong>
            <small>Confidence: medium-low · evidence-backed, not causal</small>
          </div>
        </div>
      </Panel>

      <Panel span={4} title="Why this is investable" eyebrow="Supporting signals" icon={CheckCircle2}>
        <div className="briefStack">
          <article>
            <strong>Public-source spine exists</strong>
            <span>The system uses bounded public marts and no PHI.</span>
          </article>
          <article>
            <strong>Market signal is structured</strong>
            <span>Provider, trial, safety, and reimbursement context are fused into temporal features.</span>
          </article>
          <article>
            <strong>Model weakness is visible</strong>
            <span>The app does not hide weak/moderate benchmark results.</span>
          </article>
        </div>
      </Panel>

      <Panel span={4} title="What could break the thesis" eyebrow="Counterargument" icon={AlertTriangle}>
        <div className="briefStack danger">
          <article>
            <strong>Model signal is not strong yet</strong>
            <span>Best reported v4 ROC-AUC is {fmt(best.roc_auc)}, which is exploratory, not decisive.</span>
          </article>
          <article>
            <strong>Public data is incomplete</strong>
            <span>Claims are limited by public-source coverage, refresh timing, and reporting bias.</span>
          </article>
          <article>
            <strong>No causal proof</strong>
            <span>Passive safety reports and aggregate payment data cannot establish incidence or causality.</span>
          </article>
        </div>
      </Panel>

      <Panel span={4} title="Model support" eyebrow="Benchmark caveat" icon={Gauge}>
        <div className="briefMetricGrid">
          <article><span>Run</span><strong>{fmt(modelCard.run_id)}</strong></article>
          <article><span>Best model</span><strong>{fmt(modelCard.best_model_by_roc_auc ?? modelCard.best_model_by_rmse)}</strong></article>
          <article><span>ROC-AUC</span><strong>{fmt(best.roc_auc)}</strong></article>
          <article><span>PR-AUC</span><strong>{fmt(best.pr_auc)}</strong></article>
          <article><span>Windows</span><strong>{fmt(modelCard.windows)}</strong></article>
          <article><span>Features</span><strong>{fmt(modelCard.feature_count ?? manifest.feature_count)}</strong></article>
        </div>
      </Panel>

      <Panel span={6} title="Evidence basis" eyebrow="Lineage" icon={Database}>
        <div className="briefEvidenceList">
          <span>Provider and entity context from public-source feature marts.</span>
          <span>CMS utilization/payment pressure used only as aggregate reimbursement context.</span>
          <span>openFDA/MAUDE signals treated as passive safety pressure, not incidence.</span>
          <span>Clinical trial momentum treated as market activity signal, not adoption proof.</span>
          <span>All claims remain bounded by no-PHI, no patient-level, no clinical-decision-support constraints.</span>
        </div>
      </Panel>

      <Panel span={6} title="Next diligence questions" eyebrow="Analyst workflow" icon={FileSearch}>
        <div className="briefQuestions">
          <article>
            <strong>Buyer proof</strong>
            <span>Which Texas radiology groups show enough scale and reimbursement context to justify outreach?</span>
          </article>
          <article>
            <strong>Safety posture</strong>
            <span>Which imaging/device categories show adverse-event pressure that could affect deployment risk?</span>
          </article>
          <article>
            <strong>Competitive timing</strong>
            <span>Are trial activity and AI-device signals accelerating, flattening, or shifting regions?</span>
          </article>
          <article>
            <strong>Commercial threshold</strong>
            <span>What combination of provider density, reimbursement pressure, and safety pressure changes the recommendation?</span>
          </article>
        </div>
      </Panel>

      <Panel span={12} title="Claim boundary" eyebrow="What this brief is not" icon={ShieldCheck}>
        <div className="briefBoundary">
          <span>Not clinical advice.</span>
          <span>Not patient-level prediction.</span>
          <span>Not causal validation.</span>
          <span>Not incidence estimation.</span>
          <span>Not a complete market forecast.</span>
          <span>Designed as a public-data intelligence brief for diligence prioritization.</span>
        </div>
      </Panel>
    </section>
  );
}
