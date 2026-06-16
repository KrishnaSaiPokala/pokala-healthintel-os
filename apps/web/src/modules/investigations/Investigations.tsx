import { Database, FileText, Search } from 'lucide-react';
import { Panel } from '../../components/Panel';
import { summarizeEvidence } from '../../lib/evidence';
import type { IntelligenceSnapshot } from '../../types/intelligence';

function Field({ label, value }: { label: string; value: string }) {
  return (
    <label>
      <span>{label}</span>
      <input defaultValue={value} />
    </label>
  );
}

export function Investigations({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  return (
    <section className="gridPage">
      <Panel span={12} title="Investigation Builder" icon={Search}>
        <div className="builder">
          <Field label="Region" value="Texas" />
          <Field label="Specialty" value="Radiology" />
          <Field label="Product thesis" value="AI imaging workflow automation" />
          <button className="primary">Run Public Evidence Dossier</button>
        </div>
      </Panel>

      <Panel span={6} title="Generated executive memo" icon={FileText}>
        <div className="memo">
          <p><b>Recommendation:</b> Proceed with targeted Texas radiology AI market exploration, while prioritizing safety-governance messaging and payer-friction reduction.</p>
          <p><b>Why:</b> Provider density and reimbursement activity are favorable, while FDA device-event momentum requires evidence-backed risk controls.</p>
          <p><b>Next motion:</b> Position as workflow intelligence, not autonomous diagnosis. Lead with auditability, clinical review, and measurable operating leverage.</p>
        </div>
      </Panel>

      <Panel span={6} title="Evidence drawer" icon={Database}>
        <ul className="evidence">
          {snapshot.evidence.map((item) => (
            <li key={item.id}>
              <b>{item.claim}</b>
              <span>{summarizeEvidence(item)}</span>
            </li>
          ))}
        </ul>
      </Panel>
    </section>
  );
}
