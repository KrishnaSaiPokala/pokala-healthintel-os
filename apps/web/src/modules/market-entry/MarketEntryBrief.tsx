import { motion } from 'framer-motion';
import {
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  Copy,
  Database,
  FileSearch,
  Gauge,
  MapPinned,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { Panel } from '../../components/Panel';
import modelCardRaw from '../../data/enterprise_model_card.json';
import featureManifestRaw from '../../data/enterprise_temporal_manifest.json';
import type { IntelligenceSnapshot } from '../../types/intelligence';

type AnyRecord = Record<string, any>;

const modelCard = modelCardRaw as AnyRecord;
const manifest = featureManifestRaw as AnyRecord;

const best = Array.isArray(modelCard.leaderboard) && modelCard.leaderboard.length
  ? modelCard.leaderboard[0]
  : {};

function fmt(value: unknown) {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'number') return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(4);
  if (Array.isArray(value)) return value.join(', ');
  return String(value);
}

const cardMotion = {
  initial: { opacity: 0, y: 16, scale: 0.985 },
  animate: { opacity: 1, y: 0, scale: 1 },
  transition: { duration: 0.46 }
};

const stagger = {
  animate: {
    transition: {
      staggerChildren: 0.055
    }
  }
};

export function MarketEntryBrief({ snapshot }: { snapshot?: IntelligenceSnapshot }) {
  const opportunityScore = snapshot?.scores?.market ?? 72;
  const evidenceScore = ((snapshot?.scores as any)?.evidence ?? snapshot?.scores?.market ?? 86);
  const safetyScore = snapshot?.scores?.safety ?? 58;
  const reimbursementScore = snapshot?.scores?.reimbursement ?? 64;

  const copyBrief = async () => {
    const text = [
      'Pokala HealthIntel OS — Texas Radiology AI Market Entry Brief',
      'Recommendation: Investigate entry.',
      'Confidence: medium-low.',
      'Boundary: public-source diligence intelligence only; no PHI, no patient-level prediction, not clinical decision support, not causal validation.',
      `Model caveat: v4 shock benchmark ROC-AUC ${fmt(best.roc_auc)}, PR-AUC ${fmt(best.pr_auc)}.`
    ].join('\n');

    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Clipboard may be blocked in some browser contexts. The UI remains usable.
    }
  };

  return (
    <motion.section
      className="gridPage marketBrief premiumMarketBrief"
      variants={stagger}
      initial="initial"
      animate="animate"
    >
      <Panel span={12} title="Texas Radiology AI Market Entry Brief" eyebrow="Flagship decision memo" icon={MapPinned}>
        <motion.div className="premiumBriefHero" {...cardMotion}>
          <div className="premiumBriefCopy">
            <span className="sectionKicker">Decision intelligence</span>
            <h2>Investigate entry — but do not overclaim predictive certainty.</h2>
            <p>
              A public-source diligence brief for evaluating whether a radiology AI workflow vendor should prioritize Texas.
              The product value is the combined evidence spine: market structure, reimbursement context, safety pressure,
              model caveats, and explicit claim boundaries.
            </p>

            <div className="premiumActionRow">
              <button type="button" onClick={copyBrief}>
                <Copy size={15} />
                Copy brief
              </button>
              <a href="#evidence-ledger">
                Evidence trail
                <ArrowUpRight size={15} />
              </a>
            </div>
          </div>

          <motion.div
            className="premiumDecisionPanel"
            whileHover={{ y: -4, scale: 1.012 }}
            whileTap={{ scale: 0.992 }}
            transition={{ type: 'spring', stiffness: 260, damping: 22 }}
          >
            <span>Recommendation</span>
            <strong>Investigate entry</strong>
            <small>Confidence: medium-low / evidence-backed, not causal</small>
            <div className="decisionPulse">
              <i />
              Public-data diligence mode
            </div>
          </motion.div>
        </motion.div>
      </Panel>

      <motion.div className="premiumBento bentoWide" {...cardMotion}>
        <article className="bentoTile primaryMetric">
          <span>Opportunity index</span>
          <strong>{Math.round(opportunityScore)}</strong>
          <p>Composite market signal from bounded public-source features.</p>
          <div className="premiumMeter"><i style={{ width: `${Math.min(100, Math.max(0, opportunityScore))}%` }} /></div>
        </article>

        <article className="bentoTile">
          <Sparkles size={18} />
          <span>Why now</span>
          <strong>Structured signal exists</strong>
          <p>Provider, safety, reimbursement, and trial context are usable enough for diligence prioritization.</p>
        </article>

        <article className="bentoTile warningTile">
          <AlertTriangle size={18} />
          <span>Main caveat</span>
          <strong>Model is not decisive</strong>
          <p>Best v4 ROC-AUC is {fmt(best.roc_auc)}. Useful benchmark, not validated forecasting.</p>
        </article>

        <article className="bentoTile">
          <Database size={18} />
          <span>Evidence health</span>
          <strong>{Math.round(evidenceScore)}</strong>
          <p>No-PHI public-source evidence spine is the strongest current asset.</p>
          <div className="premiumMeter"><i style={{ width: `${Math.min(100, Math.max(0, evidenceScore))}%` }} /></div>
        </article>
      </motion.div>

      <Panel span={4} title="Investable signals" eyebrow="Support" icon={CheckCircle2}>
        <motion.div className="premiumList" variants={stagger} initial="initial" animate="animate">
          {[
            ['Public-source spine exists', 'Bounded marts and no-PHI architecture are in place.'],
            ['Signal families are separated', 'Market, reimbursement, safety, and trial signals are not collapsed into one vague claim.'],
            ['Weakness is visible', 'The app states model caveats instead of pretending validated prediction.']
          ].map(([title, body]) => (
            <motion.article key={title} {...cardMotion}>
              <strong>{title}</strong>
              <span>{body}</span>
            </motion.article>
          ))}
        </motion.div>
      </Panel>

      <Panel span={4} title="Risk posture" eyebrow="Counterargument" icon={AlertTriangle}>
        <motion.div className="premiumList danger" variants={stagger} initial="initial" animate="animate">
          {[
            ['Weak model signal', `ROC-AUC ${fmt(best.roc_auc)} is exploratory, not decisive.`],
            ['Public-data incompleteness', 'Coverage, reporting bias, and refresh lag can distort apparent opportunity.'],
            ['No causal proof', 'Passive safety reports and aggregate payments cannot prove incidence or causality.']
          ].map(([title, body]) => (
            <motion.article key={title} {...cardMotion}>
              <strong>{title}</strong>
              <span>{body}</span>
            </motion.article>
          ))}
        </motion.div>
      </Panel>

      <Panel span={4} title="Model support" eyebrow="Benchmark caveat" icon={Gauge}>
        <motion.div className="premiumMetricGrid" variants={stagger} initial="initial" animate="animate">
          <motion.article {...cardMotion}><span>Run</span><strong>{fmt(modelCard.run_id)}</strong></motion.article>
          <motion.article {...cardMotion}><span>Best model</span><strong>{fmt(modelCard.best_model_by_roc_auc ?? modelCard.best_model_by_rmse)}</strong></motion.article>
          <motion.article {...cardMotion}><span>ROC-AUC</span><strong>{fmt(best.roc_auc)}</strong></motion.article>
          <motion.article {...cardMotion}><span>PR-AUC</span><strong>{fmt(best.pr_auc)}</strong></motion.article>
          <motion.article {...cardMotion}><span>Windows</span><strong>{fmt(modelCard.windows)}</strong></motion.article>
          <motion.article {...cardMotion}><span>Features</span><strong>{fmt(modelCard.feature_count ?? manifest.feature_count)}</strong></motion.article>
        </motion.div>
      </Panel>

      <Panel span={6} title="Evidence basis" eyebrow="Lineage" icon={FileSearch}>
        <motion.div className="premiumEvidenceRail" variants={stagger} initial="initial" animate="animate">
          {[
            'Provider and entity context from public-source feature marts.',
            'CMS utilization/payment pressure used only as aggregate reimbursement context.',
            'openFDA/MAUDE signals treated as passive safety pressure, not incidence.',
            'Clinical trial momentum treated as market activity signal, not adoption proof.',
            'No-PHI, no patient-level, no clinical-decision-support constraints.'
          ].map((item) => (
            <motion.span key={item} {...cardMotion}>{item}</motion.span>
          ))}
        </motion.div>
      </Panel>

      <Panel span={6} title="Diligence questions" eyebrow="Next action" icon={ShieldCheck}>
        <motion.div className="premiumQuestionStack" variants={stagger} initial="initial" animate="animate">
          {[
            ['Buyer proof', 'Which Texas radiology groups show enough scale and reimbursement context for outreach?'],
            ['Safety posture', 'Which imaging/device categories show pressure that could affect deployment risk?'],
            ['Competitive timing', 'Are trial activity and AI-device signals accelerating, flattening, or shifting regions?'],
            ['Commercial threshold', 'What signal combination changes the recommendation from investigate to enter?']
          ].map(([title, body]) => (
            <motion.article key={title} {...cardMotion}>
              <strong>{title}</strong>
              <span>{body}</span>
            </motion.article>
          ))}
        </motion.div>
      </Panel>

      <motion.div className="premiumBento bentoTight" {...cardMotion}>
        <article className="bentoTile">
          <span>Safety pressure</span>
          <strong>{Math.round(safetyScore)}</strong>
          <p>Used as posture context only.</p>
          <div className="premiumMeter"><i style={{ width: `${Math.min(100, Math.max(0, safetyScore))}%` }} /></div>
        </article>

        <article className="bentoTile">
          <span>Reimbursement context</span>
          <strong>{Math.round(reimbursementScore)}</strong>
          <p>Aggregate pressure, not patient-level economics.</p>
          <div className="premiumMeter"><i style={{ width: `${Math.min(100, Math.max(0, reimbursementScore))}%` }} /></div>
        </article>

        <article className="bentoTile boundaryTile">
          <span>Claim boundary</span>
          <strong>No PHI. No CDS. No causality.</strong>
          <p>Designed for public-data market diligence, not clinical care.</p>
        </article>
      </motion.div>
    </motion.section>
  );
}

