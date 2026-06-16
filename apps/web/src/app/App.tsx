import { useMemo, useState } from 'react';
import { Activity, Lock, ShieldCheck, Zap } from 'lucide-react';
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

const snapshot: IntelligenceSnapshot = {
  ...rawSnapshot,
  graph: {
    ...rawSnapshot.graph,
    edges: rawSnapshot.graph.edges.map((edge) => [edge[0] ?? "", edge[1] ?? ""] as [string, string]),
  },
};

export function App() {
  const [view, setView] = useState<IntelligenceView>('command');
  const [workspace, setWorkspace] = useState('Texas Radiology AI Market');
  const activeLabel = useMemo(() => navItems.find((item) => item.id === view)?.label ?? 'Command Center', [view]);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brandBlock">
          <div className="brandMark">P</div>
          <div>
            <div className="eyebrow">Pokala Systems</div>
            <h1>HealthIntel OS</h1>
          </div>
        </div>

        <div className="workspace">
          <div className="eyebrow">Active Workspace</div>
          <input value={workspace} onChange={(event) => setWorkspace(event.target.value)} aria-label="Active workspace" />
        </div>

        <nav aria-label="Product navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id} className={view === item.id ? 'active' : ''} onClick={() => setView(item.id)}>
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="opsCard">
          <ShieldCheck size={18} />
          <div>
            <strong>No-PHI intelligence boundary</strong>
            <p>Public data only. No login. No patient data. No clinical decision support claims.</p>
          </div>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <div className="eyebrow">{activeLabel}</div>
            <h2>{workspace}</h2>
          </div>
          <div className="topActions">
            <span><Activity size={15} /> {snapshot.meta.status}</span>
            <span><Zap size={15} /> {snapshot.meta.runId}</span>
            <span><Lock size={15} /> local-first</span>
          </div>
        </header>

        {view === 'command' && <CommandCenter snapshot={snapshot} />}
        {view === 'investigations' && <Investigations snapshot={snapshot} />}
        {view === 'graph' && <EntityGraphView snapshot={snapshot} />}
        {view === 'safety' && <SafetyRadar snapshot={snapshot} />}
        {view === 'reimbursement' && <ReimbursementRadar snapshot={snapshot} />}
        {view === 'model' && <ModelLab snapshot={snapshot} />}
        {view === 'data' && <DataHealth snapshot={snapshot} />}
        {view === 'brief' && <ExecutiveBrief snapshot={snapshot} />}
      </main>
    </div>
  );
}
