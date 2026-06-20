import { FileText } from 'lucide-react';
import { Panel } from '../../components/Panel';
import { computeCompositeOpportunity } from '../../lib/scoring';
import { evidenceCoverage } from '../../lib/evidence';
import { formatScore } from '../../lib/format';
import type { IntelligenceSnapshot } from '../../types/intelligence';

export function ExecutiveBrief({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  const composite = computeCompositeOpportunity(snapshot);

  return (
    <section className="gridPage">
      <Panel span={12} title="Executive Brief" icon={FileText}>
        <div className="briefHero">
          <h3>Pokala HealthIntel OS</h3>
          <p className="largeText">
            A browser-native healthcare intelligence SaaS that converts public evidence into market, safety, reimbursement, and AI-risk dossiers. It demonstrates platform engineering, health data engineering, and applied AI architecture without PHI, paid APIs, or a hosted backend bill.
          </p>
          <div className="metricRow">
            <div className="metric"><span>Composite opportunity</span><strong>{formatScore(composite)}</strong></div>
            <div className="metric"><span>Evidence coverage</span><strong>{evidenceCoverage(snapshot)}</strong></div>
            <div className="metric"><span>Claim boundary</span><strong>No clinical claims</strong></div>
          </div>
        </div>
      </Panel>

      <Panel span={6} title="Recommendation">
        <div className="memo">
          <p><b>Proceed</b> with targeted Texas radiology AI market exploration.</p>
          <p>Prioritize governed workflow positioning: auditability, human review, measurable operating leverage, and public-evidence transparency.</p>
        </div>
      </Panel>

      <Panel span={6} title="Risk controls">
        <div className="memo">
          <p><b>Do not frame</b> as autonomous diagnosis, treatment recommendation, or clinical safety validation.</p>
          <p><b>Do frame</b> as public-data strategy intelligence with evidence lineage and model-governance caveats.</p>
        </div>
      </Panel>
    </section>
  );
}

