import { useMemo, useState } from 'react';
import {
  Activity,
  ArrowRight,
  BrainCircuit,
  Building2,
  CheckCircle2,
  Clipboard,
  Database,
  FileSearch,
  Gauge,
  Lock,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Zap
} from 'lucide-react';
import rawSnapshot from '../data/intelligence.json';

type TabKey = 'market' | 'evidence' | 'model' | 'data';

const snapshot = rawSnapshot as any;

const tabs: Array<{ key: TabKey; label: string; icon: typeof Building2 }> = [
  { key: 'market', label: 'Market Brief', icon: Building2 },
  { key: 'evidence', label: 'Evidence Ledger', icon: ShieldCheck },
  { key: 'model', label: 'Model Lab', icon: BrainCircuit },
  { key: 'data', label: 'Data Health', icon: Database }
];

const sourceCount = snapshot?.meta?.sources ?? 4;

const topStats = [
  { label: 'Claim-linked evidence rows', value: '172,228', detail: 'public-source evidence spine' },
  { label: 'Dataset mart rows', value: '188,634', detail: 'bounded feature marts' },
  { label: 'Dataset marts', value: '6', detail: 'source-family coverage' },
  { label: 'PHI posture', value: '0', detail: 'no patient-level data' }
];

const evidenceClaims = [
  {
    family: 'Provider',
    title: 'Texas radiology diligence is supported by public provider/entity context.',
    supports: 'Market structure, specialty density, and diligence prioritization.',
    doesNotProve: 'Buyer intent, revenue, adoption, or patient demand.',
    boundary: 'NPI/entity context only. No PHI.'
  },
  {
    family: 'Payment',
    title: 'CMS utilization/payment signals provide reimbursement context.',
    supports: 'Aggregate pressure and market framing.',
    doesNotProve: 'Negotiated rates, profitability, or patient-level economics.',
    boundary: 'Aggregate public CMS data only.'
  },
  {
    family: 'Safety',
    title: 'openFDA/MAUDE signals are treated as safety-pressure context.',
    supports: 'Passive reporting posture and category pressure.',
    doesNotProve: 'Incidence, causality, comparative safety, or clinical risk rate.',
    boundary: 'Passive adverse-event reports cannot establish causality.'
  },
  {
    family: 'Model',
    title: 'Model Lab is an experimental benchmark artifact.',
    supports: 'Transparent weak/moderate signal testing and reproducibility.',
    doesNotProve: 'Validated forecasting, clinical utility, or production prediction.',
    boundary: 'Research benchmark only.'
  }
];

const modelMetrics = [
  { label: 'Best v4 ROC-AUC', value: '0.6030', tone: 'exploratory' },
  { label: 'Best v4 PR-AUC', value: '0.6230', tone: 'exploratory' },
  { label: 'Model windows', value: '2,388', tone: 'coverage' },
  { label: 'Posture', value: 'Benchmark only', tone: 'boundary' }
];

const sourceCards = [
  { name: 'NPPES', rows: '200 sample rows', status: 'public API sample' },
  { name: 'ClinicalTrials.gov', rows: '100 sample rows', status: 'innovation signal' },
  { name: 'openFDA / MAUDE', rows: '100 sample rows', status: 'passive safety context' },
  { name: 'CMS Physician Supplier', rows: '2,732 mart rows', status: 'aggregate payment/utilization' }
];

function copyText(text: string) {
  navigator.clipboard?.writeText(text).catch(() => undefined);
}

function ShellMetric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <article className="metricTile">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function MarketBrief() {
  return (
    <section className="pageStack">
      <div className="heroGrid">
        <article className="heroCard heroPrimary">
          <span className="eyebrow"><Sparkles size={15} /> Healthcare intelligence demo</span>
          <h1>Texas Radiology AI market entry brief.</h1>
          <p>
            A public-source diligence workspace for evaluating radiology AI market context,
            evidence strength, reimbursement context, safety posture, and model boundaries.
          </p>

          <div className="heroActions">
            <button
              type="button"
              onClick={() =>
                copyText(
                  'Pokala HealthIntel OS — Texas Radiology AI Market Brief\nRecommendation: investigate entry.\nBoundary: public-source diligence only; no PHI, no CDS, no causal claims.'
                )
              }
            >
              <Clipboard size={16} />
              Copy brief
            </button>
            <a href="#evidence">
              Open evidence spine
              <ArrowRight size={16} />
            </a>
          </div>
        </article>

        <article className="decisionCard">
          <span>Recommendation</span>
          <strong>Investigate entry</strong>
          <p>Confidence: medium-low, evidence-backed, not causal.</p>
          <div className="pulseLine">
            <i />
            Public-source diligence mode
          </div>
        </article>
      </div>

      <div className="metricGrid">
        {topStats.map((stat) => (
          <ShellMetric key={stat.label} {...stat} />
        ))}
      </div>

      <div className="bentoGrid">
        <article className="bentoTile large">
          <span className="eyebrow"><Gauge size={15} /> Opportunity posture</span>
          <h2>Useful market signal, not proof of demand.</h2>
          <p>
            The workspace is designed to support structured diligence: it shows what the public evidence supports,
            what is missing, and where a founder or analyst should investigate next.
          </p>
          <div className="meter"><i style={{ width: '78%' }} /></div>
        </article>

        <article className="bentoTile">
          <span>Strongest asset</span>
          <strong>Evidence spine</strong>
          <p>Claim-linked public evidence is the core technical asset.</p>
        </article>

        <article className="bentoTile warning">
          <span>Main risk</span>
          <strong>Overclaiming</strong>
          <p>Model and safety signals must stay bounded.</p>
        </article>

        <article className="bentoTile dark">
          <span>Boundary</span>
          <strong>No PHI. No CDS.</strong>
          <p>Market diligence only, not patient care.</p>
        </article>
      </div>
    </section>
  );
}

function EvidenceLedger() {
  const [active, setActive] = useState(evidenceClaims[0].family);

  const activeClaim = useMemo(
    () => evidenceClaims.find((claim) => claim.family === active) ?? evidenceClaims[0],
    [active]
  );

  return (
    <section id="evidence" className="pageStack">
      <div className="sectionHero">
        <span className="eyebrow"><FileSearch size={15} /> Evidence Ledger</span>
        <h1>Every claim has a source, a boundary, and a “does not prove.”</h1>
        <p>
          This is the trust layer. It keeps the product honest by separating supportable public-data intelligence
          from clinical, causal, patient-level, or incidence claims.
        </p>
      </div>

      <div className="claimConsole">
        <aside className="claimRail">
          {evidenceClaims.map((claim) => (
            <button
              key={claim.family}
              type="button"
              className={claim.family === active ? 'active' : ''}
              onClick={() => setActive(claim.family)}
            >
              {claim.family}
            </button>
          ))}
        </aside>

        <article className="claimDetail">
          <span>{activeClaim.family}</span>
          <h2>{activeClaim.title}</h2>

          <div className="claimRows">
            <section>
              <CheckCircle2 size={17} />
              <div>
                <strong>Supports</strong>
                <p>{activeClaim.supports}</p>
              </div>
            </section>

            <section>
              <ShieldAlert size={17} />
              <div>
                <strong>Does not prove</strong>
                <p>{activeClaim.doesNotProve}</p>
              </div>
            </section>

            <section>
              <Lock size={17} />
              <div>
                <strong>Boundary</strong>
                <p>{activeClaim.boundary}</p>
              </div>
            </section>
          </div>

          <button
            type="button"
            className="secondaryAction"
            onClick={() => copyText(`${activeClaim.title}\nSupports: ${activeClaim.supports}\nDoes not prove: ${activeClaim.doesNotProve}\nBoundary: ${activeClaim.boundary}`)}
          >
            <Clipboard size={15} />
            Copy evidence note
          </button>
        </article>
      </div>
    </section>
  );
}

function ModelLab() {
  return (
    <section className="pageStack">
      <div className="sectionHero">
        <span className="eyebrow"><BrainCircuit size={15} /> Model Lab</span>
        <h1>Benchmark console, not prediction theater.</h1>
        <p>
          The model layer is intentionally framed as experimental signal testing. It helps compare runs,
          expose failure modes, and prevent false confidence.
        </p>
      </div>

      <div className="modelGrid">
        {modelMetrics.map((metric) => (
          <article key={metric.label} className="modelMetric">
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <p>{metric.tone}</p>
          </article>
        ))}
      </div>

      <article className="bentoTile large">
        <span className="eyebrow"><ShieldAlert size={15} /> Model boundary</span>
        <h2>The model layer is useful only when its limitations are visible.</h2>
        <p>
          A ROC-AUC around 0.60 can support research prioritization, but it cannot support clinical, causal,
          or production forecasting claims. The interface keeps this boundary visible.
        </p>
      </article>
    </section>
  );
}

function DataHealth() {
  return (
    <section className="pageStack">
      <div className="sectionHero">
        <span className="eyebrow"><Database size={15} /> Data Health</span>
        <h1>Public-source operations dashboard.</h1>
        <p>
          Source coverage, row counts, and caveats are shown as operational health signals rather than hidden footnotes.
        </p>
      </div>

      <div className="sourceGrid">
        {sourceCards.map((source) => (
          <article key={source.name} className="sourceCard">
            <span>{source.status}</span>
            <strong>{source.name}</strong>
            <p>{source.rows}</p>
          </article>
        ))}
      </div>

      <article className="bentoTile dark">
        <span>System boundary</span>
        <strong>Bounded public-source workspace</strong>
        <p>
          Raw source certification is pending. This is a bounded public-data workspace and does not process PHI.
        </p>
      </article>
    </section>
  );
}

export function App() {
  const [tab, setTab] = useState<TabKey>('market');
  const activeTab = tabs.find((item) => item.key === tab) ?? tabs[0];

  return (
    <div className="appShell">
      <header className="topbar">
        <div className="brand">
          <div className="brandMark">P</div>
          <div>
            <span>Pokala HealthIntel OS</span>
            <strong>Public healthcare intelligence workspace</strong>
          </div>
        </div>

        <nav className="navPills" aria-label="Main navigation">
          {tabs.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                type="button"
                className={tab === item.key ? 'active' : ''}
                onClick={() => setTab(item.key)}
              >
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="trustPills">
          <span><Activity size={14} /> Public demo</span>
          <span><Database size={14} /> {sourceCount} sources</span>
          <span><Lock size={14} /> No PHI</span>
        </div>
      </header>

      <main className="mainSurface">
        <section className="workspaceIntro">
          <div>
            <span className="eyebrow"><Zap size={15} /> {activeTab.label}</span>
            <h1>Public-source healthcare intelligence for market diligence, evidence tracking, and model transparency.</h1>
          </div>
          <div className="postureCard">
            <ShieldCheck size={18} />
            <span>Public-source bounded</span>
            <strong>No clinical decision support</strong>
          </div>
        </section>

        {tab === 'market' && <MarketBrief />}
        {tab === 'evidence' && <EvidenceLedger />}
        {tab === 'model' && <ModelLab />}
        {tab === 'data' && <DataHealth />}
      </main>
    </div>
  );
}

