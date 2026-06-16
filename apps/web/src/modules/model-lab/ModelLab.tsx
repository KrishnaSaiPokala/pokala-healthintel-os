import { Activity, BrainCircuit, Terminal } from 'lucide-react';
import { Panel } from '../../components/Panel';
import type { IntelligenceSnapshot } from '../../types/intelligence';

const attentionTokens = [
  'UTILIZATION_VOLUME',
  'MEDICARE_PAYMENT',
  'PRICE_SPREAD',
  'FDA_EVENT_RATE',
  'TRIAL_DENSITY',
  'BREACH_HISTORY',
  'PROVIDER_DENSITY',
  'AI_DEVICE_ACTIVITY'
];

export function ModelLab({ snapshot }: { snapshot: IntelligenceSnapshot }) {
  return (
    <section className="gridPage">
      <Panel span={12} title="Temporal Transformer Intelligence Layer" icon={BrainCircuit}>
        <div className="attentionGrid">
          {attentionTokens.map((token, index) => (
            <div className="token" key={token}>
              <span>{token}</span>
              <b>{(0.42 + index * 0.06).toFixed(2)}</b>
            </div>
          ))}
        </div>
        <p className="largeText">
          The current deployed MVP uses deterministic scoring over static public-data artifacts. The Model Lab documents the temporal-transformer target architecture for sequence-level momentum, anomaly, and risk-direction classification.
        </p>
      </Panel>

      <Panel span={6} title="Architecture" icon={Activity}>
        <pre className="code">{`signal tokens\n  ↓\npositional encoding\n  ↓\nmulti-head self-attention\n  ↓\nfeed-forward block\n  ↓\nrisk / opportunity heads\n  ↓\nevidence-backed scores`}</pre>
      </Panel>

      <Panel span={6} title="Baseline discipline" icon={Terminal}>
        <pre className="code">{`Baseline: rolling z-score + logistic rules\nComparator: GRU / BiLSTM sequence encoder\nPrimary: temporal transformer encoder\nDeployment: offline inference to static artifacts\nRuntime: browser-native UI + Cloudflare Worker`}</pre>
      </Panel>

      <Panel span={12} title="Model card summary" eyebrow={snapshot.meta.runId}>
        <div className="modelCardGrid">
          <div><span>Current status</span><strong>Prototype layer documented</strong></div>
          <div><span>Clinical use</span><strong>Not permitted</strong></div>
          <div><span>Inputs</span><strong>Public aggregated signals</strong></div>
          <div><span>Output</span><strong>Market/risk screening scores</strong></div>
        </div>
      </Panel>
    </section>
  );
}
