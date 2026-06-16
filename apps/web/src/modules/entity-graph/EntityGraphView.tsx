import { GitBranch } from 'lucide-react';
import { Panel } from '../../components/Panel';
import type { IntelligenceSnapshot } from '../../types/intelligence';

export function EntityGraphView({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  return (
    <section className="gridPage">
      <Panel span={12} title="Healthcare Entity Graph" icon={GitBranch} className="graphPanel">
        <div className="graphCanvas">
          {snapshot.graph.nodes.map((node, index) => (
            <div key={node.id} className={`node n${index}`}>{node.label}</div>
          ))}
          {snapshot.graph.edges.map((edge, index) => (
            <div key={`${edge[0]}-${edge[1]}`} className={`edge e${index}`} />
          ))}
        </div>
      </Panel>
    </section>
  );
}
