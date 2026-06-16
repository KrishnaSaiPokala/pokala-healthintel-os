import { Activity, Database, FileText, Radar as RadarIcon, ShieldCheck } from 'lucide-react';
import {
  CartesianGrid,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar as RadarShape,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import { Panel } from '../../components/Panel';
import { ScoreCard } from '../../components/ScoreCard';
import { buildScoreCards, computeCompositeOpportunity } from '../../lib/scoring';
import { evidenceCoverage } from '../../lib/evidence';
import { formatNumber } from '../../lib/format';
import type { IntelligenceSnapshot } from '../../types/intelligence';

export function CommandCenter({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  const scoreCards = buildScoreCards(snapshot);
  const composite = Math.round(computeCompositeOpportunity(snapshot));
  const evidencePreview = snapshot.evidence.slice(0, 4);

  return (
    <section className="gridPage commandGrid executiveCommand">
      <Panel span={12} className="executiveHeroPanel">
        <div className="executiveHero">
          <div className="executiveHeroCopy">
            <div className="eyebrow">Flagship public-data intelligence case</div>
            <h2>Texas radiology AI market-entry command center</h2>
            <p>
              A no-PHI, public-source intelligence workspace for evaluating market opportunity,
              reimbursement motion, safety momentum, and evidence readiness for AI imaging workflow adoption.
            </p>

            <div className="heroProofRow">
              <span><strong>{formatNumber(snapshot.meta.evidenceRows)}</strong> evidence rows</span>
              <span><strong>{snapshot.meta.sources}</strong> public sources</span>
              <span><strong>{snapshot.meta.status}</strong> build status</span>
            </div>
          </div>

          <aside className="executiveDecision">
            <span>Composite opportunity</span>
            <strong>{composite}</strong>
            <small>/100</small>
            <p>Proceed with governed pilot screening, focused on human-review workflows and auditability.</p>
          </aside>
        </div>
      </Panel>

      <Panel span={12} title="Signal board" eyebrow="Executive scorecard" icon={Activity} className="signalBoardPanel">
        <div className="signalTiles">
          {scoreCards.map((card) => <ScoreCard key={card.label} card={card} />)}
        </div>
      </Panel>

      <Panel span={8} title="Temporal signal track" eyebrow="Momentum" icon={Activity} className="chartPanel">
        <ResponsiveContainer height={320}>
          <LineChart data={snapshot.temporal}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.07)" />
            <XAxis dataKey="period" stroke="#7d8aa5" tickLine={false} axisLine={false} />
            <YAxis stroke="#7d8aa5" tickLine={false} axisLine={false} domain={[0, 100]} />
            <Tooltip contentStyle={{ background: '#0a1020', border: '1px solid rgba(255,255,255,.14)', color: '#fff', borderRadius: 14 }} />
            <Line type="monotone" dataKey="market" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="safety" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="reimbursement" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Panel>

      <Panel span={4} title="Decision memo" eyebrow="Recommended motion" icon={FileText} className="decisionMemoPanel">
        <div className="memoStack">
          <strong>Governed pilot screening</strong>
          <p>
            Strong market and reimbursement signals justify deeper diligence. Safety momentum should be treated as
            a governance constraint, not a blocker.
          </p>
          <div className="memoPills">
            <span>No PHI</span>
            <span>Evidence linked</span>
            <span>Review required</span>
          </div>
        </div>
      </Panel>

      <Panel span={5} title="Opportunity / risk radar" eyebrow="Tradeoff map" icon={RadarIcon}>
        <ResponsiveContainer height={300}>
          <RadarChart data={snapshot.radar}>
            <PolarGrid stroke="rgba(255,255,255,.12)" />
            <PolarAngleAxis dataKey="axis" stroke="#9aa6c0" />
            <PolarRadiusAxis stroke="#64708a" />
            <RadarShape dataKey="value" fillOpacity={0.28} />
          </RadarChart>
        </ResponsiveContainer>
      </Panel>

      <Panel span={7} title="Evidence coverage" eyebrow="Source-backed claims" icon={ShieldCheck} className="evidencePreviewPanel">
        <div className="coverageSummary">
          <strong>{evidenceCoverage(snapshot)}</strong>
          <span>Every score should resolve to public-source evidence and caveats.</span>
        </div>

        <div className="evidencePreviewList">
          {evidencePreview.map((item) => (
            <article key={item.id}>
              <strong>{item.claim}</strong>
              <span>{item.source} ? {item.freshness} ? {formatNumber(item.rows)} rows</span>
            </article>
          ))}
        </div>
      </Panel>

      <Panel span={12} title="Pipeline status" eyebrow="Runtime boundary" icon={Database} className="terminalPanel compactRuntime">
        <pre>{`build: public-evidence-release\nmode: CPU-first static artifacts\nmodel: transformer-ready signal layer\nstatus: ${snapshot.meta.status}\nlineage: evidence-gated\nprivacy: no PHI / no patient-level data`}</pre>
      </Panel>
    </section>
  );
}
