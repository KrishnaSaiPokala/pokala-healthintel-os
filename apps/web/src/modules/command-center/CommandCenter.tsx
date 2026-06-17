import { Activity, Database, FileText, ShieldCheck } from 'lucide-react';
import { Panel } from '../../components/Panel';
import { evidenceCoverage } from '../../lib/evidence';
import { formatNumber } from '../../lib/format';
import { computeCompositeOpportunity } from '../../lib/scoring';
import type { IntelligenceSnapshot } from '../../types/intelligence';

type Tone = 'cyan' | 'green' | 'amber' | 'red';

function scoreLabel(value: number) {
  if (value >= 85) return 'Strong';
  if (value >= 75) return 'Favorable';
  if (value >= 65) return 'Watch';
  return 'Review';
}

function SignalRow({
  label,
  value,
  delta,
  interpretation,
  tone
}: {
  label: string;
  value: number;
  delta: string;
  interpretation: string;
  tone: Tone;
}) {
  const score = Math.round(Math.max(0, Math.min(100, value)));

  return (
    <article className={`signalRow ${tone}`}>
      <div className="signalRowMain">
        <div>
          <span className="signalLabel">{label}</span>
          <strong>{scoreLabel(score)}</strong>
        </div>
        <p>{interpretation}</p>
      </div>

      <div className="signalRowScore">
        <span>{score}</span>
        <small>/100</small>
        <em>{delta}</em>
      </div>
    </article>
  );
}

export function CommandCenter({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  const composite = Math.round(computeCompositeOpportunity(snapshot));
  const evidencePreview = snapshot.evidence.slice(0, 4);

  return (
    <section className="gridPage commandGrid executiveCommand finalCommand">
      <Panel span={12} className="productHeroPanel">
        <div className="productHero">
          <div className="productHeroText">
            <div className="eyebrow">Public-source healthcare intelligence</div>
            <h2>Evidence-backed market intelligence for AI radiology expansion.</h2>
            <p>
              HealthIntel OS converts public provider, reimbursement, safety, trial, and population signals
              into an auditable executive dossier. This view is deliberately no-PHI, no-login, and evidence-gated.
            </p>

            <div className="heroMetaLine">
              <span>{formatNumber(snapshot.meta.evidenceRows)} evidence rows</span>
              <span>{snapshot.meta.sources} public sources</span>
              <span>No PHI / no patient records</span>
            </div>
          </div>

          <aside className="thesisCard">
            <span>Recommended motion</span>
            <strong>Proceed to governed diligence</strong>
            <p>
              Market and payment signals are favorable. Safety acceleration requires governance positioning,
              evidence review, and human-in-the-loop workflow framing.
            </p>
            <div className="thesisScore">
              <small>Opportunity index</small>
              <b>{composite}</b>
              <em>/100</em>
            </div>
          </aside>
        </div>
      </Panel>

      <Panel span={12} title="Executive signal summary" eyebrow="Decision inputs" icon={Activity} className="signalSummaryPanel">
        <div className="signalRows">
          <SignalRow
            label="Market attractiveness"
            value={snapshot.scores.market}
            delta="+12.4%"
            tone="cyan"
            interpretation="Provider concentration and utilization momentum support a first-pass Texas radiology AI market screen."
          />
          <SignalRow
            label="Safety momentum"
            value={snapshot.scores.safety}
            delta="+6.8%"
            tone="amber"
            interpretation="Device-event momentum is not disqualifying, but it should shape governance, messaging, and review controls."
          />
          <SignalRow
            label="Reimbursement signal"
            value={snapshot.scores.reimbursement}
            delta="+9.1%"
            tone="green"
            interpretation="Payment and utilization signals suggest monetizable workflow pressure, with payer-friction caveats."
          />
          <SignalRow
            label="Provider density"
            value={snapshot.scores.providerDensity}
            delta="+4.6%"
            tone="cyan"
            interpretation="Specialty supply is strong enough to justify deeper regional segmentation and account prioritization."
          />
        </div>
      </Panel>

      <Panel span={7} title="Temporal signal narrative" eyebrow="Momentum pattern" icon={Activity} className="temporalNarrativePanel">
        <div className="temporalStory">
          {snapshot.temporal.map((point) => (
            <article key={point.period}>
              <span>{point.period}</span>
              <div className="temporalBars">
                <i className="market" style={{ width: `${point.market}%` }} />
                <i className="safety" style={{ width: `${point.safety}%` }} />
                <i className="reimbursement" style={{ width: `${point.reimbursement}%` }} />
              </div>
            </article>
          ))}
        </div>

        <div className="legendLine">
          <span><i className="market" /> Market</span>
          <span><i className="safety" /> Safety</span>
          <span><i className="reimbursement" /> Reimbursement</span>
        </div>
      </Panel>

      <Panel span={5} title="Decision brief" eyebrow="Why this matters" icon={FileText} className="briefPanel">
        <div className="briefStack">
          <article>
            <span>01</span>
            <p>Texas radiology shows enough public-market signal to justify a focused pilot-screening dossier.</p>
          </article>
          <article>
            <span>02</span>
            <p>Safety momentum should become a diligence lane, not a hidden risk or overclaimed blocker.</p>
          </article>
          <article>
            <span>03</span>
            <p>The correct product story is workflow intelligence, auditability, and operating leverage?not autonomous diagnosis.</p>
          </article>
        </div>
      </Panel>

      <Panel span={7} title="Evidence coverage" eyebrow="Source-backed claims" icon={ShieldCheck} className="evidenceCoveragePanel">
        <div className="coverageHeader">
          <strong>{evidenceCoverage(snapshot)}</strong>
          <span>Every executive claim links back to public-source evidence, row counts, and caveats.</span>
        </div>

        <div className="evidenceRows">
          {evidencePreview.map((item) => (
            <article key={item.id}>
              <strong>{item.claim}</strong>
              <span>{item.source} ? {item.freshness} ? {formatNumber(item.rows)} rows</span>
            </article>
          ))}
        </div>
      </Panel>

      <Panel span={5} title="Research boundary" eyebrow="Claim discipline" icon={Database} className="boundaryPanel">
        <div className="boundaryList">
          <span>No patient-level data</span>
          <span>No PHI ingestion</span>
          <span>No clinical decision support claim</span>
          <span>No paid API dependency</span>
          <span>Public-data intelligence only</span>
        </div>
      </Panel>
    </section>
  );
}
