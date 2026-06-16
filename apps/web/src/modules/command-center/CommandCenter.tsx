import { Activity, Database, Radar } from 'lucide-react';
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
import { Metric } from '../../components/Metric';
import { buildScoreCards, computeCompositeOpportunity } from '../../lib/scoring';
import { evidenceCoverage } from '../../lib/evidence';
import { formatNumber, formatScore } from '../../lib/format';
import type { IntelligenceSnapshot } from '../../types/intelligence';

export function CommandCenter({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  const scoreCards = buildScoreCards(snapshot);
  const composite = computeCompositeOpportunity(snapshot);

  return (
    <section className="gridPage commandGrid">
      <Panel span={8} title="AI device market-entry command center" eyebrow="Flagship vertical" icon={Activity}>
        <div className="heroPanel">
          <div>
            <p className="largeText">
              Evidence-backed public-data intelligence for evaluating a Texas radiology AI workflow market entry. The surface combines provider density, reimbursement momentum, FDA device-event signals, and innovation activity into an auditable executive dossier.
            </p>
            <div className="metricRow">
              <Metric label="Composite opportunity" value={formatScore(composite)} />
              <Metric label="Evidence rows" value={formatNumber(snapshot.meta.evidenceRows)} />
              <Metric label="Public sources" value={`${snapshot.meta.sources}`} />
            </div>
          </div>
          <div className="decisionBadge">
            <span>Recommended motion</span>
            <strong>Proceed with governed pilot screening</strong>
            <em>{evidenceCoverage(snapshot)}</em>
          </div>
        </div>
      </Panel>

      <Panel span={4} title="Pipeline status" eyebrow="Runtime" icon={Database} className="terminalPanel">
        <pre>{`run: public-evidence-build\nmode: CPU-first static artifacts\nmodel: transformer-ready signal layer\nstatus: ${snapshot.meta.status}\nlineage: evidence-gated`}</pre>
      </Panel>

      {scoreCards.map((card) => <ScoreCard key={card.label} card={card} />)}

      <Panel span={7} title="Temporal signal track" icon={Activity}>
        <ResponsiveContainer height={280}>
          <LineChart data={snapshot.temporal}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />
            <XAxis dataKey="period" stroke="#7d8aa5" />
            <YAxis stroke="#7d8aa5" />
            <Tooltip contentStyle={{ background: '#0a1020', border: '1px solid rgba(255,255,255,.14)', color: '#fff' }} />
            <Line type="monotone" dataKey="market" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="safety" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="reimbursement" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Panel>

      <Panel span={5} title="Opportunity / risk radar" icon={Radar}>
        <ResponsiveContainer height={280}>
          <RadarChart data={snapshot.radar}>
            <PolarGrid stroke="rgba(255,255,255,.12)" />
            <PolarAngleAxis dataKey="axis" stroke="#9aa6c0" />
            <PolarRadiusAxis stroke="#64708a" />
            <RadarShape dataKey="value" fillOpacity={0.32} />
          </RadarChart>
        </ResponsiveContainer>
      </Panel>
    </section>
  );
}
