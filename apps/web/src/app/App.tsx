import { useMemo, useState } from 'react';
import { Activity, Database, Lock, ShieldCheck } from 'lucide-react';
import rawSnapshot from '../data/intelligence.json';
import { CommandCenter } from '../modules/command-center/CommandCenter';
import { Investigations } from '../modules/investigations/Investigations';
import { EntityGraphView } from '../modules/entity-graph/EntityGraphView';
import { SafetyRadar } from '../modules/safety-radar/SafetyRadar';
import { ReimbursementRadar } from '../modules/reimbursement/ReimbursementRadar';
import { ModelLab } from '../modules/model-lab/ModelLab';
import { DataHealth } from '../modules/data-health/DataHealth';
import { ExecutiveBrief } from '../modules/executive-brief/ExecutiveBrief';
import { navItems } from './navigation';
import type { IntelligenceSnapshot, IntelligenceView } from '../types/intelligence';

const raw = rawSnapshot as any;

const snapshot: IntelligenceSnapshot = {
  ...raw,
  graph: {
    ...raw.graph,
    edges: (raw.graph?.edges ?? []).map((edge: string[]) => [edge[0] ?? '', edge[1] ?? ''] as [string, string]),
  },
};

export function App() {
  const [view, setView] = useState<IntelligenceView>('command');
  const activeLabel = useMemo(() => navItems.find((item) => item.id === view)?.label ?? 'Command Center', [view]);

  return (
    <div className="productShell">
      <header className="productHeader">
        <div className="brandLockup">
          <div className="brandSeal">P</div>
          <div>
            <span>Pokala HealthIntel OS</span>
            <strong>Public healthcare intelligence workspace</strong>
          </div>
        </div>

        <nav className="productNav" aria-label="Product navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id} className={view === item.id ? 'active' : ''} onClick={() => setView(item.id)}>
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="trustCluster" aria-label="System posture">
          <span><Activity size={14} /> Evidence ready</span>
          <span><Database size={14} /> {snapshot.meta.sources} evidence sources</span>
          <span><Lock size={14} /> No PHI</span>
        </div>
      </header>

      <main className="productMain">
        <section className="workspaceHeader">
          <div>
            <span className="sectionKicker">{activeLabel}</span>
            <h1>Texas Radiology AI Market</h1>
          </div>
          <div className="workspacePosture">
            <span><ShieldCheck size={15} /> Public-source demo</span>
            <span>No account required</span>
            <span>No patient-level data</span>
          </div>
        </section>

        {view === 'command' && <CommandCenter snapshot={snapshot} />}
        {view === 'investigations' && <Investigations snapshot={snapshot} />}
        {view === 'graph' && <EntityGraphView snapshot={snapshot} />}
        {view === 'safety' && <SafetyRadar snapshot={snapshot} />}
        {view === 'reimbursement' && <ReimbursementRadar snapshot={snapshot} />}
        {view === 'model' && <ModelLab />}
        {view === 'data' && <DataHealth snapshot={snapshot} />}
        {view === 'brief' && <ExecutiveBrief snapshot={snapshot} />}
      </main>
    </div>
  );
}
