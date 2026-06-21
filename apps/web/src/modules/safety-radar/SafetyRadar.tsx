import { AlertTriangle, ShieldCheck } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Panel } from '../../components/Panel';
import { classifySignal } from '../../lib/scoring';
import type { IntelligenceSnapshot } from '../../types/intelligence';

export function SafetyRadar({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  const safetyClass = classifySignal(snapshot.scores.safety);

  return (
    <section className="gridPage">
      <Panel span={8} title="FDA device-event momentum" icon={AlertTriangle}>
        <ResponsiveContainer height={320}>
          <BarChart data={snapshot.temporal}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />
            <XAxis dataKey="period" stroke="#7d8aa5" />
            <YAxis stroke="#7d8aa5" />
            <Tooltip contentStyle={{ background: '#0a1020', border: '1px solid rgba(255,255,255,.14)', color: '#fff' }} />
            <Bar dataKey="safety" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Panel>

      <Panel span={4} title="Safety interpretation" icon={ShieldCheck}>
        <p className="largeText">
          Safety momentum is <b>{safetyClass}</b>. The platform flags acceleration rather than absolute event count, so technical stakeholders can inspect underlying evidence before acting.
        </p>
        <div className="callout warning">Not a clinical safety determination. This is a public adverse-event signal review layer.</div>
      </Panel>
    </section>
  );
}

