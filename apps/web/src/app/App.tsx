import { useMemo, useState } from 'react';
import type { LucideIcon, LucideProps } from 'lucide-react';
import {
  Activity,
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Building2,
  CheckCircle2,
  Clipboard,
  Database,
  FileSearch,
  GitBranch,
  Layers3,
  Lock,
  Microscope,
  Network,
  ServerCog,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  TableProperties,
  Workflow,
  Zap
} from 'lucide-react';
import rawSnapshot from '../data/intelligence.json';
import modelBenchmark from '../data/model_benchmark.json';
import overnightBenchmarkRaw from '../data/deep_benchmark_overnight.json';

type TabKey = 'market' | 'evidence' | 'model' | 'data' | 'architecture' | 'case';

type Tab = {
  key: TabKey;
  label: string;
  short: string;
  icon: LucideIcon;
};

type EvidenceRow = {
  domain: string;
  claim: string;
  source: string;
  supports: string;
  doesNotProve: string;
  boundary: string;
  takeaway: string;
};

type DataRow = {
  source: string;
  role: string;
  rows: string;
  refresh: string;
  phiRisk: string;
  limitation: string;
  certification: string;
};

const snapshot = rawSnapshot as any;
const overnightBenchmark = overnightBenchmarkRaw as any;

const tabs: Tab[] = [
  { key: 'market', label: 'Market Intelligence', short: 'Market', icon: Building2 },
  { key: 'evidence', label: 'Evidence Governance', short: 'Evidence', icon: ShieldCheck },
  { key: 'model', label: 'Benchmark Lab', short: 'Model', icon: BrainCircuit },
  { key: 'data', label: 'Data Lineage', short: 'Data', icon: Database },
  { key: 'architecture', label: 'System Architecture', short: 'Architecture', icon: Network },
  { key: 'case', label: 'Implementation Brief', short: 'Case', icon: FileSearch }
];

const systemStats = [
  { label: 'Claim-linked evidence rows', value: '172,228', detail: 'evidence spine rows' },
  { label: 'Dataset mart rows', value: '188,634', detail: 'bounded analytical marts' },
  { label: 'Dataset marts', value: '6', detail: 'source-family coverage' },
  { label: 'PHI posture', value: '0', detail: 'no patient-level data' }
];

const demoSkills = [
  {
    title: 'Healthcare data engineering',
    detail: 'Public healthcare sources are framed as bounded marts with source roles, caveats, and lineage status.',
    icon: Database
  },
  {
    title: 'Evidence governance',
    detail: 'Each claim is separated into evidence, support, what it does not prove, and the applicable boundary.',
    icon: ShieldCheck
  },
  {
    title: 'Benchmark governance',
    detail: 'Temporal benchmark metrics are presented with limitations rather than inflated product claims.',
    icon: BrainCircuit
  },
  {
    title: 'Healthcare claim boundaries',
    detail: 'No PHI, no patient-level inference, and no clinical-decision support language are used.',
    icon: Lock
  },
  {
    title: 'Cloud deployment',
    detail: 'React/Vite frontend is built and deployed through Cloudflare Worker assets with validation gates.',
    icon: ServerCog
  },
  {
    title: 'Architecture communication',
    detail: 'Architecture, model limits, and data lineage are written as product-facing system controls.',
    icon: TableProperties
  }
];

const evidenceRows: EvidenceRow[] = [
  {
    domain: 'Provider network',
    claim: 'Texas radiology market context can be evaluated using public provider and organizational signals.',
    source: 'NPPES provider identity, taxonomy, and public entity metadata.',
    supports: 'Provider density, specialty context, entity-level diligence, and market structure framing.',
    doesNotProve: 'Revenue, buyer intent, clinical adoption, patient demand, or private contracting.',
    boundary: 'Public provider/entity context only. No PHI and no patient-level inference.',
    takeaway: 'Keeps provider-market analysis tied to public-source context and explicit claim limits.'
  },
  {
    domain: 'Reimbursement',
    claim: 'CMS utilization and payment aggregates can frame diligence pressure.',
    source: 'CMS Medicare utilization/payment public aggregates and derived marts.',
    supports: 'Aggregate reimbursement context, service-line pressure, and market-level signal triage.',
    doesNotProve: 'Profitability, negotiated rates, payer mix, or patient-level economics.',
    boundary: 'Aggregate public data only. Not a financial forecast.',
    takeaway: 'Frames reimbursement signals as market context, not private economics or forecasted revenue.'
  },
  {
    domain: 'Safety signal',
    claim: 'openFDA / MAUDE reports are useful as safety-pressure context, not incidence.',
    source: 'Passive adverse-event and device-event public reports.',
    supports: 'Reporting attention, safety posture, and operational caveat tracking.',
    doesNotProve: 'Causality, incidence, comparative safety rates, or clinical risk.',
    boundary: 'Passive reports are incomplete and cannot establish causation.',
    takeaway: 'Treats passive safety reports as governance context, not incidence or causality.'
  },
  {
    domain: 'Innovation signal',
    claim: 'ClinicalTrials.gov can indicate research activity around a product area.',
    source: 'Public trial registry records and trial metadata.',
    supports: 'Research intensity, trial-stage context, and innovation landscape review.',
    doesNotProve: 'Commercial traction, regulatory clearance, or clinical superiority.',
    boundary: 'Registry context only; trial existence is not outcome proof.',
    takeaway: 'Shows market-diligence use of public clinical research data.'
  },
  {
    domain: 'Relationship context',
    claim: 'CMS Open Payments can provide relationship-context signals.',
    source: 'Public Open Payments disclosure data.',
    supports: 'Industry relationship context and diligence questions.',
    doesNotProve: 'Improper influence, procurement intent, or product endorsement.',
    boundary: 'Disclosure context only; not an allegation system.',
    takeaway: 'Shows careful interpretation of sensitive healthcare public data.'
  },
  {
    domain: 'Deep learning benchmark',
    claim: 'Temporal public-data benchmarks show exploratory signal, not validated forecasting.',
    source: 'Model cards, run metadata, seed metrics, ROC/PR results, and failure notes.',
    supports: 'Experiment design, reproducibility, baseline comparison, and transparent evaluation.',
    doesNotProve: 'Clinical utility, causal effect, production forecasting, or patient-level prediction.',
    boundary: 'Research benchmark only. Not clinical decision support.',
    takeaway: 'Reports benchmark metrics with explicit limitations and non-clinical-use boundaries.'
  }
];

const modelMetrics = [
  { label: 'Run ID', value: 'Benchmark Phase4_shock_20260618_121556', note: 'reproducible benchmark reference' },
  { label: 'Model family', value: 'Temporal transformer classifier', note: 'sequence benchmark candidate' },
  { label: 'Prediction target', value: 'Opportunity shock', note: 'public-data temporal target' },
  { label: 'Window / horizon', value: '24 / 3', note: 'temporal framing' },
  { label: 'Seeds', value: '7 seeds', note: 'seed stability check' },
  { label: 'Feature count', value: '213', note: 'mart-derived feature space' },
  { label: 'Best ROC-AUC', value: '0.6030', note: 'exploratory signal only' },
  { label: 'Best PR-AUC', value: '0.6230', note: 'class-imbalance aware metric' },
  { label: 'Balanced accuracy', value: '0.5318', note: 'weak/moderate benchmark' },
  { label: 'Public posture', value: 'Research only', note: 'not validated forecasting' }
];

const dataRows: DataRow[] = [
  {
    source: 'NPPES',
    role: 'Provider identity, taxonomy, and organization context.',
    rows: 'sample + mart rows',
    refresh: 'Public source pull',
    phiRisk: 'No PHI in source',
    limitation: 'Registry identity context, not utilization or outcomes.',
    certification: 'bounded'
  },
  {
    source: 'CMS utilization/payment',
    role: 'Aggregate reimbursement and service-line context.',
    rows: 'mart-level aggregate',
    refresh: 'Public CMS release',
    phiRisk: 'No PHI in source',
    limitation: 'No negotiated rates or patient-level economics.',
    certification: 'bounded'
  },
  {
    source: 'openFDA / MAUDE',
    role: 'Device-event and passive safety-pressure context.',
    rows: 'public event summaries',
    refresh: 'Public API extract',
    phiRisk: 'No PHI in source',
    limitation: 'Passive reports cannot establish causality/incidence.',
    certification: 'bounded'
  },
  {
    source: 'ClinicalTrials.gov',
    role: 'Innovation and trial activity context.',
    rows: 'public registry sample',
    refresh: 'Public registry pull',
    phiRisk: 'No PHI in source',
    limitation: 'Trial presence does not prove effectiveness.',
    certification: 'bounded'
  },
  {
    source: 'CMS Open Payments',
    role: 'Relationship-context diligence signal.',
    rows: 'public disclosure context',
    refresh: 'Public CMS release',
    phiRisk: 'No PHI in source',
    limitation: 'Disclosure does not imply misconduct or endorsement.',
    certification: 'bounded'
  },
  {
    source: 'Derived model marts',
    role: 'Temporal features for benchmark experiments.',
    rows: '188,634 mart rows',
    refresh: 'Pipeline-derived',
    phiRisk: 'No PHI in source',
    limitation: 'Feature marts support research benchmarks only.',
    certification: 'pending raw certification'
  }
];

const architectureLayers = [
  {
    layer: 'Public source ingestion',
    icon: ServerCog,
    detail: 'Adapters pull public healthcare data from NPPES, CMS, openFDA, trial registries, and related sources.'
  },
  {
    layer: 'Normalization and marts',
    icon: Layers3,
    detail: 'Source-specific records are shaped into bounded analytical marts with role-specific limitations.'
  },
  {
    layer: 'Evidence spine',
    icon: GitBranch,
    detail: 'Claims are connected to evidence, caveats, does-not-prove fields, and healthcare-data boundaries.'
  },
  {
    layer: 'Temporal features',
    icon: Activity,
    detail: 'Marts become time-aware feature windows for reproducible benchmark experiments.'
  },
  {
    layer: 'Deep learning lab',
    icon: BrainCircuit,
    detail: 'Temporal models are compared using ROC/PR metrics, baseline pressure, seeds, and failure notes.'
  },
  {
    layer: 'Public interface',
    icon: Workflow,
    detail: 'A public-source workspace explains HIT maturity, model evaluation, and safe claim posture.'
  }
];

const caseStudy = [
  {
    title: 'Problem',
    detail: 'Healthcare market intelligence often mixes useful signals with unsafe claims. This project explores how to build a public-source diligence system that remains clear about evidence boundaries.'
  },
  {
    title: 'Constraints',
    detail: 'No PHI, no patient-level data, no clinical decision support, no causality claims from passive safety reports, and no inflated model claims.'
  },
  {
    title: 'Build',
    detail: 'React/Vite frontend, Cloudflare Worker deployment, public healthcare marts, evidence ledger, model-lab summaries, and validation scripts.'
  },
  {
    title: 'Modeling approach',
    detail: 'Temporal benchmark experiments test whether public healthcare signals contain weak but usable structure. Metrics are framed as research evidence only.'
  },
  {
    title: 'Operational takeaway',
    detail: 'The system connects public data, evidence boundaries, model benchmarks, and deployment controls in one operational workspace.'
  }
];

function copyText(text: string) {
  navigator.clipboard?.writeText(text).catch(() => undefined);
}

function IconCard({ icon: Icon, title, detail }: { icon: LucideIcon; title: string; detail: string }) {
  return (
    <article className="iconCard">
      <Icon size={20} />
      <strong>{title}</strong>
      <p>{detail}</p>
    </article>
  );
}

function StatCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <article className="statCard">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function SectionIntro({
  icon: Icon,
  eyebrow,
  title,
  children
}: {
  icon: LucideIcon;
  eyebrow: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="sectionIntro">
      <span className="eyebrow"><Icon size={15} /> {eyebrow}</span>
      <h2>{title}</h2>
      <p>{children}</p>
    </section>
  );
}

function MetricGrid() {
  return (
    <section className="statGrid">
      {systemStats.map((stat) => <StatCard key={stat.label} {...stat} />)}
    </section>
  );
}

function MarketBrief() {
  return (
    <div className="pageStack">
      <section className="heroGrid">
        <article className="heroPanel heroPrimary">
          <span className="eyebrow"><Stethoscope size={15} /> Healthcare intelligence workspace</span>
          <h1>A public-source workspace for healthcare market analysis, evidence-linked claims, and transparent model benchmarking.</h1>
          <p>
            Pokala HealthIntel OS organizes public healthcare datasets, source-linked evidence, benchmark outputs, and claim boundaries inside a deployed intelligence workspace.
          </p>

          <div className="chipRow">
            {['Public-source only', 'No PHI', 'Claim-boundary controls', 'Model limits disclosed', 'Non-clinical use'].map((item) => (
              <span key={item}><CheckCircle2 size={14} /> {item}</span>
            ))}
          </div>

          <div className="actionRow">
            <button
              type="button"
              onClick={() =>
                copyText(
                  'Built a deployed public-source Healthcare intelligence workspace workspace combining React/Vite, Cloudflare Workers, healthcare data lineage, evidence-boundary governance, and transparent temporal model benchmarking. No PHI. Not clinical decision support.'
                )
              }
            >
              <Clipboard size={16} />
              Copy system summary
            </button>
            <button type="button" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
              View posture
              <ArrowRight size={16} />
            </button>
          </div>
        </article>

        <aside className="advancedPanel">
          <span>Governance posture</span>
          <strong>Evidence governance / data lineage / model benchmarking</strong>
          <p>
            Built for source-bound analysis: public-data boundaries, lineage visibility,
            transparent model benchmarking, and explicit claim boundaries.
          </p>
          <div className="pulseLine"><i /> Deployed public workspace</div>
        </aside>
      </section>

      <MetricGrid />

      <SectionIntro icon={Sparkles} eyebrow="System capabilities" title="Evidence-linked healthcare intelligence.">
        The interface is designed so technical technical stakeholders can quickly see the engineering, healthcare-data,
        modeling, and communication judgment behind the project.
      </SectionIntro>

      <section className="skillsGrid">
        {demoSkills.map((skill) => <IconCard key={skill.title} {...skill} />)}
      </section>
    </div>
  );
}

function EvidenceLedger() {
  const [active, setActive] = useState(evidenceRows[0].domain);
  const row = useMemo(() => evidenceRows.find((item) => item.domain === active) ?? evidenceRows[0], [active]);

  return (
    <div className="pageStack">
      <SectionIntro icon={FileSearch} eyebrow="Evidence Governance" title="Claim-boundary controls is the trust layer.">
        Real healthcare intelligence is not just collecting sources. It is knowing what a source supports,
        what it cannot prove, and where the claim boundary belongs.
      </SectionIntro>

      <section className="ledgerShell">
        <aside className="ledgerRail">
          {evidenceRows.map((item) => (
            <button key={item.domain} type="button" className={item.domain === active ? 'active' : ''} onClick={() => setActive(item.domain)}>
              {item.domain}
            </button>
          ))}
        </aside>

        <article className="ledgerDetail">
          <span>{row.domain}</span>
          <h2>{row.claim}</h2>

          <div className="claimMatrix">
            <section><Microscope size={18} /><div><strong>Source</strong><p>{row.source}</p></div></section>
            <section><CheckCircle2 size={18} /><div><strong>Supports</strong><p>{row.supports}</p></div></section>
            <section><ShieldAlert size={18} /><div><strong>Does not prove</strong><p>{row.doesNotProve}</p></div></section>
            <section><Lock size={18} /><div><strong>Boundary</strong><p>{row.boundary}</p></div></section>
            <section><Zap size={18} /><div><strong>Operational takeaway</strong><p>{row.takeaway}</p></div></section>
          </div>
        </article>
      </section>

      <section className="evidenceTable">
        {evidenceRows.map((item) => (
          <article key={item.domain}>
            <span>{item.domain}</span>
            <strong>{item.claim}</strong>
            <p>{item.takeaway}</p>
          </article>
        ))}
      </section>
    </div>
  );
}

function ModelLab() {
  const benchmark = modelBenchmark as any;
  const baselineRows = benchmark?.benchmark_results ?? [];
  const deepRows = benchmark?.deep_results ?? [];
  const plannedRows = benchmark?.planned_deep_models ?? [];
  const overnightRows = overnightModels();
  const overnightBest = bestOvernightModel();
  const overnightCompleted = overnightRows.reduce((sum: number, row: any) => sum + completedSeeds(row), 0);
  const overnightFailed = overnightRows.reduce((sum: number, row: any) => sum + failedSeeds(row), 0);

  return (
    <div className="pageStack">
      <SectionIntro icon={BrainCircuit} eyebrow="Benchmark Lab" title="Transparent benchmark outputs are connected to the public interface.">
        Benchmark Phase 7 syncs actual Benchmark Phase 6 baseline results into the frontend and adds a initial MLP baseline run with early stopping.
        The model layer remains a research benchmark, not validated forecasting.
      </SectionIntro>


      <section className="benchmarkPanel">
        <div className="benchmarkHeader">
          <div>
            <span className="eyebrow"><BrainCircuit size={15} /> Overnight Core DL Benchmark</span>
            <h2>210 completed multi-seed model runs</h2>
            <p>
              Dataset: <strong>{overnightBenchmark?.source_dataset ?? 'not available'}</strong> / Target:{' '}
              <strong>{overnightBenchmark?.target_column ?? 'not available'}</strong>
            </p>
          </div>
          <aside>
            <span>Best mean ROC-AUC</span>
            <strong>{metricMean(overnightBest, 'roc_auc')}</strong>
          </aside>
        </div>

        <section className="modelGrid">
          <article className="modelCard">
            <span>Model families</span>
            <strong>{overnightRows.length}</strong>
            <p>sklearn MLP, PyTorch MLP variants, LSTM, GRU, TCN, Transformer, CNN hybrid, and gated MLP.</p>
          </article>
          <article className="modelCard">
            <span>Completed seed runs</span>
            <strong>{overnightCompleted}</strong>
            <p>21 seeds per model family, committed as a reproducible benchmark artifact.</p>
          </article>
          <article className="modelCard">
            <span>Failed seed runs</span>
            <strong>{overnightFailed}</strong>
            <p>Failure count from the overnight benchmark summary.</p>
          </article>
          <article className="modelCard">
            <span>Best model</span>
            <strong>{overnightBest?.model_id ?? '-'}</strong>
            <p>Best model selected by mean ROC-AUC across completed seeds.</p>
          </article>
        </section>

        <div className="benchmarkTable">
          <div className="benchmarkRow benchmarkHead">
            <span>Model</span><span>Family</span><span>Seeds</span><span>ROC-AUC</span><span>PR-AUC</span><span>F1 macro</span><span>Balanced acc.</span>
          </div>
          {overnightRows.map((row: any) => (
            <div className="benchmarkRow" key={row.model_id}>
              <strong>{row.model_id}</strong>
              <span>{row.model_family}</span>
              <span>{completedSeeds(row)} / 21</span>
              <span>{metricMean(row, 'roc_auc')}</span>
              <span>{metricMean(row, 'pr_auc')}</span>
              <span>{metricMean(row, 'f1_macro')}</span>
              <span>{metricMean(row, 'balanced_accuracy')}</span>
            </div>
          ))}
        </div>

        <div className="leaderboardNote">
          Boundary: benchmark signals only. No PHI. Not clinical decision support. No patient-level prediction claim.
          Sequence-family models are architecture benchmarks over single-step tabular tensors until a future phase constructs true temporal tensors.
        </div>
      </section>

      <section className="modelGrid">
        {modelMetrics.map((metric) => (
          <article className="modelCard" key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <p>{metric.note}</p>
          </article>
        ))}
      </section>

      <section className="benchmarkPanel">
        <div className="benchmarkHeader">
          <div>
            <span className="eyebrow"><BarChart3 size={15} /> Synced benchmark table</span>
            <h2>Benchmark results</h2>
            <p>
              Dataset: <strong>{benchmark?.dataset_used ?? 'not available'}</strong> / Target:{' '}
              <strong>{benchmark?.target_used ?? 'not available'}</strong>
            </p>
          </div>
          <aside>
            <span>Run</span>
            <strong>{benchmark?.run_id ?? 'Benchmark Phase 7_model_lab_sync'}</strong>
          </aside>
        </div>

        <div className="benchmarkTable">
          <div className="benchmarkRow benchmarkHead">
            <span>Model</span><span>Status</span><span>ROC-AUC</span><span>PR-AUC</span><span>Balanced acc.</span><span>F1</span><span>Notes</span>
          </div>
          {[...baselineRows, ...deepRows].map((row: any) => {
            const m = row.metrics ?? {};
            return (
              <div className="benchmarkRow" key={`${row.model}-${row.status}`}>
                <strong>{row.model}</strong>
                <span>{row.status}</span>
                <span>{formatMetric(m.roc_auc)}</span>
                <span>{formatMetric(m.pr_auc)}</span>
                <span>{formatMetric(m.balanced_accuracy)}</span>
                <span>{formatMetric(m.f1)}</span>
                <p>{row.notes}</p>
              </div>
            );
          })}
        </div>
      </section>

      <section className="twoPanel">
        <article>
          <span className="eyebrow"><BrainCircuit size={15} /> Planned model extensions</span>
          <h2>Sequence and transformer benchmarks</h2>
          <p>{plannedRows.join(' / ')}</p>
        </article>
        <article className="warningPanel">
          <span className="eyebrow"><ShieldAlert size={15} /> Boundary</span>
          <h2>Research benchmark only</h2>
          <p>{benchmark?.claim_boundary ?? 'No PHI. Not clinical decision support. No patient-level prediction.'}</p>
        </article>
      </section>
    </div>
  );
}

function formatMetric(value: unknown) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '-';
  return value.toFixed(3);
}


function overnightModels() {
  return Array.isArray(overnightBenchmark?.models) ? overnightBenchmark.models : [];
}

function metricMean(row: any, key: string) {
  const value = row?.summary?.[key]?.mean;
  if (typeof value !== 'number' || Number.isNaN(value)) return '-';
  return value.toFixed(4);
}

function completedSeeds(row: any) {
  return Number(row?.summary?.completed_seeds ?? 0);
}

function failedSeeds(row: any) {
  return Number(row?.summary?.failed_seeds ?? 0);
}

function bestOvernightModel() {
  return overnightModels()
    .filter((row: any) => typeof row?.summary?.roc_auc?.mean === 'number')
    .sort((a: any, b: any) => b.summary.roc_auc.mean - a.summary.roc_auc.mean)[0] ?? {};
}



function DataHealth() {
  return (
    <div className="pageStack">
      <SectionIntro icon={Database} eyebrow="Data Lineage" title="Healthcare data engineering is visible, not buried.">
        Data Lineage shows source roles, row posture, PHI risk, limitations, and certification state so technical stakeholders can
        evaluate the system like a real HIT artifact.
      </SectionIntro>

      <MetricGrid />

      <section className="dataTable">
        <div className="tableHeader">
          <span>Source</span><span>Role</span><span>Rows</span><span>PHI risk</span><span>Limitation</span><span>Status</span>
        </div>
        {dataRows.map((row) => (
          <article key={row.source}>
            <strong>{row.source}</strong>
            <p>{row.role}</p>
            <p>{row.rows}</p>
            <p>{row.phiRisk}</p>
            <p>{row.limitation}</p>
            <p>{row.certification}</p>
          </article>
        ))}
      </section>
    </div>
  );
}

function Architecture() {
  return (
    <div className="pageStack">
      <SectionIntro icon={Network} eyebrow="System Architecture" title="A system walkthrough for technical interviews.">
        This page explains the build as a healthcare IT system: ingestion, normalization, evidence governance,
        temporal feature construction, model evaluation, and public deployment.
      </SectionIntro>

      <section className="architectureFlow">
        {architectureLayers.map((layer, index) => {
          const Icon = layer.icon;
          return (
            <article key={layer.layer}>
              <div className="stepNumber">{String(index + 1).padStart(2, '0')}</div>
              <Icon size={21} />
              <strong>{layer.layer}</strong>
              <p>{layer.detail}</p>
            </article>
          );
        })}
      </section>
    </div>
  );
}

function CaseStudy() {
  return (
    <div className="pageStack">
      <SectionIntro icon={FileSearch} eyebrow="Implementation brief" title="From public healthcare data to a deployed intelligence workspace.">
        This case-study page frames the project for technical technical stakeholders: problem, constraints, design,
        model evaluation, deployment, and next improvements.
      </SectionIntro>

      <section className="caseGrid">
        {caseStudy.map((item) => (
          <article key={item.title}>
            <span>{item.title}</span>
            <strong>{item.title}</strong>
            <p>{item.detail}</p>
          </article>
        ))}
      </section>

      <section className="twoPanel">
        <article>
          <span className="eyebrow"><CheckCircle2 size={15} /> Strongest signal</span>
          <h2>Governed analysis under constraints</h2>
          <p>
            The core value is the system design:
            useful public-data intelligence while refusing unsafe healthcare claims.
          </p>
        </article>
        <article>
          <span className="eyebrow"><Workflow size={15} /> Next improvement</span>
          <h2>Next system hardening step</h2>
          <p>
            The next layer would add deeper evidence-row browsing, source freshness metadata,
            model run comparison, screenshots, and a README-driven review package.
          </p>
        </article>
      </section>
    </div>
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
              <button key={item.key} type="button" className={item.key === tab ? 'active' : ''} onClick={() => setTab(item.key)}>
                <Icon size={16} />
                <span>{item.short}</span>
              </button>
            );
          })}
        </nav>

        <div className="trustPills" aria-label="Project posture">
          <span><ShieldCheck size={14} /> Public-source</span>
          <span><Lock size={14} /> No PHI</span>
          <span><Zap size={14} /> Deployed workspace</span>
        </div>
      </header>

      <main className="mainSurface">
        <section className="workspaceIntro">
          <div>
            <span className="eyebrow"><Sparkles size={15} /> {activeTab.label}</span>
            <h1>Healthcare intelligence workspace for evidence governance, data lineage, and model benchmarking.</h1>
          </div>
          <aside>
            <span>System overview</span>
            <strong>Public data / claim boundaries / transparent model benchmarks</strong>
          </aside>
        </section>

        {tab === 'market' && <MarketBrief />}
        {tab === 'evidence' && <EvidenceLedger />}
        {tab === 'model' && <ModelLab />}
        {tab === 'data' && <DataHealth />}
        {tab === 'architecture' && <Architecture />}
        {tab === 'case' && <CaseStudy />}
      </main>
    </div>
  );
}

