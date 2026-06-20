import { Database } from 'lucide-react';
import { Panel } from '../../components/Panel';
import { formatNumber } from '../../lib/format';
import type { IntelligenceSnapshot } from '../../types/intelligence';

export function DataHealth({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  return (
    <section className="gridPage dataGrid">
      {snapshot.datasets.map((dataset) => (
        <Panel key={dataset.name} span={4}>
          <div className="dataset">
            <Database size={18} />
            <strong>{dataset.name}</strong>
            <span>{formatNumber(dataset.rows)} rows</span>
            <em>{dataset.status}</em>
          </div>
        </Panel>
      ))}
      <Panel span={12} title="Data health controls" icon={Database}>
        <div className="controlList">
          <span>Source manifest required for every public-data mart.</span>
          <span>Every score must link to evidence rows and caveats.</span>
          <span>No PHI, login, claims of HIPAA certification, or clinical decision support.</span>
        </div>
      </Panel>
    </section>
  );
}

