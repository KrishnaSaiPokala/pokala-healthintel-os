import { Activity, Database, FileText, ShieldCheck } from 'lucide-react';
import { evidenceCoverage } from '../../lib/evidence';
import { formatNumber } from '../../lib/format';
import { computeCompositeOpportunity } from '../../lib/scoring';
import type { IntelligenceSnapshot } from '../../types/intelligence';

function classify(value: number) {
  if (value >= 85) return 'Strong';
  if (value >= 75) return 'Favorable';
  if (value >= 65) return 'Governed review';
  return 'Needs diligence';
}

export function CommandCenter({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  const composite = Math.round(computeCompositeOpportunity(snapshot));
  const rows = [
    {
      factor: 'Market demand',
      reading: classify(snapshot.scores.market),
      score: Math.round(snapshot.scores.market),
      basis: 'Provider concentration and utilization momentum support a first-pass Texas radiology screen.',
      control: 'Segment by region, specialty concentration, and workflow setting.'
    },
    {
      factor: 'Safety momentum',
      reading: classify(snapshot.scores.safety),
      score: Math.round(snapshot.scores.safety),
      basis: 'Device-event acceleration should shape governance, review, and claims discipline.',
      control: 'Position as workflow intelligence with human review, not autonomous diagnosis.'
    },
    {
      factor: 'Reimbursement pressure',
      reading: classify(snapshot.scores.reimbursement),
      score: Math.round(snapshot.scores.reimbursement),
      basis: 'Payment and utilization patterns suggest workflow ROI potential with payer-friction caveats.',
      control: 'Tie commercial claims to measurable operating leverage and auditability.'
    },
    {
      factor: 'Provider density',
      reading: classify(snapshot.scores.providerDensity),
      score: Math.round(snapshot.scores.providerDensity),
      basis: 'Specialty supply is sufficient for deeper account prioritization and regional targeting.',
      control: 'Use evidence-backed prioritization rather than broad market generalization.'
    }
  ];

  return (
    <section className="casefile">
      <section className="caseHero">
        <div className="caseHeroCopy">
          <span className="sectionKicker">Enterprise public demo ? no-PHI evidence workspace</span>
          <h2>Should an AI imaging workflow company enter the Texas radiology market?</h2>
          <p>
            HealthIntel OS turns public healthcare data into a structured decision brief: market motion,
            reimbursement pressure, safety momentum, and evidence lineage. The product is intentionally
            accountless, public-data-only, and safe for recruiter/researcher review.
          </p>

          <div className="caseHeroActions">
            <a href="#decision-ledger">View decision ledger</a>
            <a href="#evidence-ledger">Inspect evidence</a>
            <a href="#system-posture">System posture</a>
          </div>
        </div>

        <aside className="decisionPanel">
          <span>Recommended motion</span>
          <strong>Proceed to governed diligence</strong>
          <p>
            The market is attractive enough for pilot screening. Safety acceleration should become a
            governance workstream, not an ignored risk.
          </p>
          <div className="decisionIndex">
            <small>Opportunity index</small>
            <b>{composite}</b>
            <em>/100</em>
          </div>
        </aside>
      </section>

      <section className="whiteboardStrip" aria-label="Method plan">
        <article>
          <span>01</span>
          <strong>Frame the market question</strong>
          <p>Texas radiology AI workflow expansion, not clinical diagnosis automation.</p>
        </article>
        <article>
          <span>02</span>
          <strong>Collect public evidence</strong>
          <p>NPPES, CMS utilization, FDA-style safety events, trials, and source-health metadata.</p>
        </article>
        <article>
          <span>03</span>
          <strong>Score with caveats</strong>
          <p>Every signal is presented with uncertainty, source lineage, and claim boundaries.</p>
        </article>
        <article>
          <span>04</span>
          <strong>Export the dossier</strong>
          <p>Decision-ready memo for market, safety, reimbursement, and governance review.</p>
        </article>
      </section>

      <section id="decision-ledger" className="caseSection">
        <div className="caseSectionHeader">
          <span className="sectionKicker">Decision ledger</span>
          <h3>Four-factor executive readout</h3>
          <p>No oversized dashboard cards. The score is secondary to the interpretation and control path.</p>
        </div>

        <div className="ledgerTable">
          <div className="ledgerHead">
            <span>Factor</span>
            <span>Read</span>
            <span>Basis</span>
            <span>Control</span>
          </div>

          {rows.map((row) => (
            <article key={row.factor} className="ledgerRow">
              <div>
                <strong>{row.factor}</strong>
                <small>{row.score}/100</small>
              </div>
              <div><mark>{row.reading}</mark></div>
              <p>{row.basis}</p>
              <p>{row.control}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="caseGrid">
        <article className="narrativeCard">
          <span className="sectionKicker">Momentum narrative</span>
          <h3>Signals rise together, but not with the same risk profile.</h3>
          <p>
            Market and reimbursement movement are favorable. Safety movement needs a separate governance lane.
            The product story should focus on workflow intelligence, auditability, and human-supervised adoption.
          </p>

          <div className="timelineStack">
            {snapshot.temporal.map((point) => (
              <div key={point.period}>
                <span>{point.period}</span>
                <i style={{ width: `${point.market}%` }} />
                <i style={{ width: `${point.reimbursement}%` }} />
                <i style={{ width: `${point.safety}%` }} />
              </div>
            ))}
          </div>
        </article>

        <article className="narrativeCard">
          <span className="sectionKicker">Public demo posture</span>
          <h3>Enterprise feel without accounts or PHI.</h3>
          <p>
            This is a public, no-login artifact. The enterprise posture comes from transparency, lineage,
            model boundaries, system status, and exportable evidence?not user accounts.
          </p>

          <div className="postureGrid" id="system-posture">
            <span>Cloudflare Worker</span>
            <span>Static React assets</span>
            <span>D1 demo API</span>
            <span>Public-source data</span>
            <span>No patient data</span>
            <span>No clinical claims</span>
          </div>
        </article>
      </section>

      <section id="evidence-ledger" className="caseSection evidenceCaseSection">
        <div className="caseSectionHeader">
          <span className="sectionKicker">Source evidence ledger</span>
          <h3>{evidenceCoverage(snapshot)}</h3>
          <p>Each claim is tied to a public-source mart, row count, and claim boundary.</p>
        </div>

        <div className="evidenceLedger">
          {snapshot.evidence.slice(0, 6).map((item) => (
            <article key={item.id}>
              <div>
                <strong>{item.claim}</strong>
                <span>{item.source}</span>
              </div>
              <small>{item.freshness}</small>
              <em>{formatNumber(item.rows)} rows</em>
            </article>
          ))}
        </div>
      </section>

      <section className="caseFooterBrief">
        <FileText size={18} />
        <div>
          <strong>Boundary statement</strong>
          <p>
            HealthIntel OS is a public-data intelligence system. It does not ingest PHI, does not identify patients,
            and does not provide medical advice or clinical decision support.
          </p>
        </div>
        <div className="footerBadges">
          <span><ShieldCheck size={14} /> Evidence-gated</span>
          <span><Database size={14} /> {formatNumber(snapshot.meta.evidenceRows)} rows</span>
          <span><Activity size={14} /> {snapshot.meta.status}</span>
        </div>
      </section>
    </section>
  );
}

