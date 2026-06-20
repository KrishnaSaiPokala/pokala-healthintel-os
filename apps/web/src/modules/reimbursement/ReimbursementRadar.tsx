import { BarChart3, Map } from 'lucide-react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Panel } from '../../components/Panel';
import type { IntelligenceSnapshot } from '../../types/intelligence';

export function ReimbursementRadar({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  return (
    <section className="gridPage">
      <Panel span={7} title="Reimbursement variability" icon={BarChart3}>
        <ResponsiveContainer height={300}>
          <LineChart data={snapshot.temporal}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)" />
            <XAxis dataKey="period" stroke="#7d8aa5" />
            <YAxis stroke="#7d8aa5" />
            <Tooltip contentStyle={{ background: '#0a1020', border: '1px solid rgba(255,255,255,.14)', color: '#fff' }} />
            <Line type="monotone" dataKey="reimbursement" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Panel>

      <Panel span={5} title="Market signal" icon={Map}>
        <p className="largeText">
          Reimbursement volatility is treated as both opportunity and risk: high spread may suggest monetizable workflow gaps, but also payer friction and implementation variability.
        </p>
        <div className="callout">The next production-grade step is provider/service-line stratification by geography and HCPCS family.</div>
      </Panel>
    </section>
  );
}

