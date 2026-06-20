import { useMemo, useState } from 'react';
import type { LucideIcon } from 'lucide-react';
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
  Workflow,
  Zap
} from 'lucide-react';
import rawSnapshot from '../data/intelligence.json';

type TabKey = 'market' | 'evidence' | 'model' | 'data' | 'architecture';

type Tab = {
  key: TabKey;
  label: string;
  short: string;
  icon: LucideIcon;
};

type Claim = {
  family: string;
  title: string;
  evidence: string;
  supports: string;
  doesNotProve: string;
  boundary: string;
};

const snapshot = rawSnapshot as any;

const tabs: Tab[] = [
  { key: 'market', label: 'Market Brief', short: 'Market', icon: Building2 },
  { key: 'evidence', label: 'Evidence Ledger', short: 'Evidence', icon: ShieldCheck },
  { key: 'model', label: 'Model Lab', short: 'Model', icon: BrainCircuit },
  { key: 'data', label: 'Data Health', short: 'Data', icon: Database },
  { key: 'architecture', label: 'HIT Architecture', short: 'Architecture', icon: Network }
];

const systemStats = [
  { label: 'Claim-linked evidence rows', value: '172,228', detail: 'public-source evidence spine' },
  { label: 'Dataset mart rows', value: '188,634', detail: 'bounded analytical marts' },
  { label: 'Dataset marts', value: '6', detail: 'source-family coverage' },
  { label: 'PHI posture', value: '0', detail: 'no patient-level data' }
];

const hitSignals = [
  'Public-source only',
  'No PHI processing',
  'Claim-boundary governance',
  'Source lineage visible',
  'Model limitations disclosed',
  'Not clinical decision support'
];

const evidenceClaims: Claim[] = [
  {
    family: 'Provider network',
    title: 'Texas radiology market context is grounded in public provider and organizational signals.',
    evidence: 'NPPES provider identity, specialty context, and public entity metadata.',
    supports: 'Market structure, specialty density, diligence prioritization, and entity-level context.',
    doesNotProve: 'Revenue, buyer intent, private contracts, patient demand, or adoption readiness.',
    boundary: 'Public provider/entity context only. No PHI, no patient-level inference.'
  },
  {
    family: 'Reimbursement',
    title: 'CMS utilization and payment context can frame diligence pressure, but not economics.',
    evidence: 'CMS public utilization/payment aggregates and derived mart-level summaries.',
    supports: 'Aggregate reimbursement context, volume pressure, and service-line framing.',
    doesNotProve: 'Profitability, negotiated rates, payer contracts, or patient-level economics.',
    boundary: 'Aggregate public data only. Not a financial forecast.'
  },
  {
    family: 'Safety signal',
    title: 'openFDA / MAUDE reports are treated as safety-pressure context, not incidence.',
    evidence: 'Passive adverse-event reports and device-event summaries.',
    supports: 'Operational safety posture, reporting attention, and category-level caveat tracking.',
    doesNotProve: 'Causality, incidence, comparative safety rate, or clinical risk.',
    boundary: 'Passive reports are incomplete and cannot establish causation.'
  },
  {
    family: 'Deep learning',
    title: 'The temporal model benchmark shows exploratory signal, not validated forecasting.',
    evidence: 'Temporal benchmark runs, model cards, baseline pressure, ROC/PR metrics, and failure notes.',
    supports: 'Reproducible experiment design, benchmark comparison, and transparent limitation disclosure.',
    doesNotProve: 'Clinical utility, production readiness, causality, or patient-level prediction.',
    boundary: 'Research benchmark only. Not CDS. Not deployed for care decisions.'
  }
];

const modelRows = [
  { label: 'Best ROC-AUC', value: '0.6030', note: 'exploratory signal strength' },
  { label: 'Best PR-AUC', value: '0.6230', note: 'class-imbalance aware metric' },
  { label: 'Balanced accuracy', value: '0.5318', note: 'weak/moderate benchmark' },
  { label: 'Benchmark posture', value: 'Research only', note: 'not validated forecasting' }
];

const dataSources = [
  { name: 'NPPES', role: 'Provider identity and taxonomy context', posture: 'Public provider registry' },
  { name: 'CMS utilization/payment', role: 'Aggregate reimbursement and service context', posture: 'Public CMS aggregate' },
  { name: 'openFDA / MAUDE', role: 'Device-event and safety-pressure context', posture: 'Passive reports; not causal' },
  { name: 'ClinicalTrials.gov', role: 'Innovation and research activity context', posture: 'Public trial registry' },
  { name: 'CMS Open Payments', role: 'Industry-payment relationship context', posture: 'Public aggregate disclosure' },
  { name: 'CDC / public demand signals', role: 'Population and regional pressure context', posture: 'Public population data' }
];

const architectureLayers = [
  { layer: 'Source ingestion', icon: ServerCog, detail: 'Public source adapters, bounded ingestion, and raw-source certification tracking.' },
  { layer: 'Evidence spine', icon: GitBranch, detail: 'Claim-linked rows with support, caveat, does-not-prove, and boundary fields.' },
  { layer: 'Analytical marts', icon: Layers3, detail: 'Provider, utilization, safety, trial, and population marts for diligence workflows.' },
  { layer: 'Model lab', icon: BrainCircuit, detail: 'Temporal benchmark runs with baselines, metrics, seed behavior, and failure disclosure.' },
  { layer: 'Public interface', icon: Workflow, detail: 'Recruiter-facing React workspace focused on HIT maturity and DL evaluation judgment.' }
];

function copyText(text: string) {
  navigator.clipboard?.writeText(text).catch(() => undefined);
}

function StatCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <article className="statCard"><span>{label}</span><strong>{value}</strong><p>{detail}</p></article>;
}

function SectionIntro({ icon: Icon, eyebrow, title, children }: { icon: LucideIcon; eyebrow: string; title: string; children: React.ReactNode }) {
  return <section className="sectionIntro"><span className="eyebrow"><Icon size={15} /> {eyebrow}</span><h2>{title}</h2><p>{children}</p></section>;
}

function MarketBrief() {
  return <div className="pageStack">
    <section className="heroGrid">
      <article className="heroPanel heroPrimary">
        <span className="eyebrow"><Stethoscope size={15} /> Healthcare IT intelligence</span>
        <h1>Public healthcare intelligence for market diligence, evidence tracking, and model transparency.</h1>
        <p>Pokala HealthIntel OS demonstrates healthcare data engineering, claim-boundary governance, and transparent deep learning evaluation using bounded public datasets only.</p>
        <div className="chipRow">{hitSignals.map((item) => <span key={item}><CheckCircle2 size={14} /> {item}</span>)}</div>
        <div className="actionRow">
          <button type="button" onClick={() => copyText('Pokala HealthIntel OS: public-source Healthcare IT intelligence workspace for evidence-linked diligence, data lineage, and transparent model benchmarking. No PHI. Not clinical decision support.')}><Clipboard size={16} />Copy project summary</button>
          <button type="button" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>View system posture<ArrowRight size={16} /></button>
        </div>
      </article>
      <aside className="summitPanel"><span>System posture</span><strong>HIT + DL portfolio artifact</strong><p>Built to show practical judgment: public data boundaries, lineage visibility, model transparency, and professional restraint.</p><div className="pulseLine"><i /> Deployed public workspace</div></aside>
    </section>
    <section className="statGrid">{systemStats.map((stat) => <StatCard key={stat.label} {...stat} />)}</section>
    <section className="bentoGrid">
      <article className="bentoTile large"><span className="eyebrow"><Gauge size={15} /> Recruiter-readable signal</span><h2>Complex healthcare data, presented with discipline.</h2><p>The site is designed to make the engineering maturity visible: source boundaries, evidence governance, no PHI, and model results that do not overclaim.</p><div className="meter"><i style={{ width: '84%' }} /></div></article>
      <article className="bentoTile"><span>Healthcare IT</span><strong>Evidence governance</strong><p>Claims are tied to support, limitations, and source boundaries.</p></article>
      <article className="bentoTile"><span>Deep learning</span><strong>Transparent evaluation</strong><p>Model metrics are shown with baseline pressure and caveats.</p></article>
      <article className="bentoTile dark"><span>Boundary</span><strong>No PHI. No CDS.</strong><p>Public-source diligence only; not used for patient care decisions.</p></article>
      <article className="bentoTile amber"><span>Professional judgment</span><strong>Honest limits</strong><p>The interface is built to prevent unsupported clinical or causal claims.</p></article>
    </section>
  </div>;
}

function EvidenceLedger() {
  const [active, setActive] = useState(evidenceClaims[0].family);
  const claim = useMemo(() => evidenceClaims.find((item) => item.family === active) ?? evidenceClaims[0], [active]);
  return <div className="pageStack">
    <SectionIntro icon={FileSearch} eyebrow="Evidence Ledger" title="Claim-boundary governance is the center of the system.">Every public-facing claim is separated into evidence, what it supports, what it does not prove, and the applicable healthcare data boundary.</SectionIntro>
    <section className="ledgerShell">
      <aside className="ledgerRail">{evidenceClaims.map((item) => <button key={item.family} type="button" className={item.family === active ? 'active' : ''} onClick={() => setActive(item.family)}>{item.family}</button>)}</aside>
      <article className="ledgerDetail"><span>{claim.family}</span><h2>{claim.title}</h2><div className="claimMatrix">
        <section><Microscope size={18} /><div><strong>Evidence</strong><p>{claim.evidence}</p></div></section>
        <section><CheckCircle2 size={18} /><div><strong>Supports</strong><p>{claim.supports}</p></div></section>
        <section><ShieldAlert size={18} /><div><strong>Does not prove</strong><p>{claim.doesNotProve}</p></div></section>
        <section><Lock size={18} /><div><strong>Boundary</strong><p>{claim.boundary}</p></div></section>
      </div></article>
    </section>
  </div>;
}

function ModelLab() {
  return <div className="pageStack">
    <SectionIntro icon={BrainCircuit} eyebrow="Model Lab" title="Deep learning maturity means showing the limitation, not hiding it.">The model layer evaluates whether public healthcare signals contain usable temporal structure. Results are framed as an experimental benchmark, not clinical utility or validated forecasting.</SectionIntro>
    <section className="statGrid">{modelRows.map((metric) => <article className="statCard" key={metric.label}><span>{metric.label}</span><strong>{metric.value}</strong><p>{metric.note}</p></article>)}</section>
    <section className="modelNarrative"><article><span className="eyebrow"><Activity size={15} /> Evaluation posture</span><h2>What this proves</h2><p>Reproducible temporal benchmark construction, metric tracking, baseline awareness, and the ability to communicate weak-to-moderate model signal without overstating it.</p></article><article><span className="eyebrow"><ShieldAlert size={15} /> What it does not prove</span><h2>What this does not prove</h2><p>It does not prove clinical value, patient-level prediction, causality, incidence, or production forecasting readiness.</p></article></section>
  </div>;
}

function DataHealth() {
  return <div className="pageStack">
    <SectionIntro icon={Database} eyebrow="Data Health" title="Healthcare data engineering is visible, not buried.">The workspace surfaces source roles, lineage posture, row counts, and caveats so reviewers can see how the public-data system is constructed.</SectionIntro>
    <section className="sourceGrid">{dataSources.map((source) => <article className="sourceCard" key={source.name}><span>{source.posture}</span><strong>{source.name}</strong><p>{source.role}</p></article>)}</section>
    <section className="bentoGrid compact"><article className="bentoTile dark"><span>Data posture</span><strong>Bounded public workspace</strong><p>No PHI. No patient-level identifiers. Public-source diligence only.</p></article><article className="bentoTile"><span>Lineage</span><strong>Explicit source roles</strong><p>Each source has a defined role and limitation in the workflow.</p></article><article className="bentoTile amber"><span>Certification</span><strong>Raw source certification pending</strong><p>Current artifact is bounded; it does not pretend to be a full raw data lake.</p></article></section>
  </div>;
}

function Architecture() {
  return <div className="pageStack">
    <SectionIntro icon={Network} eyebrow="HIT Architecture" title="A compact architecture view for technical reviewers.">This page explains the system as a healthcare IT artifact: source ingestion, evidence governance, marts, model lab, and a public interface designed around safe boundaries.</SectionIntro>
    <section className="architectureFlow">{architectureLayers.map((layer, index) => { const Icon = layer.icon; return <article key={layer.layer}><div className="stepNumber">{String(index + 1).padStart(2, '0')}</div><Icon size={21} /><strong>{layer.layer}</strong><p>{layer.detail}</p></article>; })}</section>
  </div>;
}

export function App() {
  const [tab, setTab] = useState<TabKey>('market');
  const activeTab = tabs.find((item) => item.key === tab) ?? tabs[0];
  return <div className="appShell">
    <header className="topbar"><div className="brand"><div className="brandMark">P</div><div><span>Pokala HealthIntel OS</span><strong>Healthcare IT + deep learning evaluation workspace</strong></div></div><nav className="navPills" aria-label="Main navigation">{tabs.map((item) => { const Icon = item.icon; return <button key={item.key} type="button" className={item.key === tab ? 'active' : ''} onClick={() => setTab(item.key)}><Icon size={16} /><span>{item.short}</span></button>; })}</nav><div className="trustPills" aria-label="Project posture"><span><ShieldCheck size={14} /> Public-source</span><span><Lock size={14} /> No PHI</span><span><Zap size={14} /> Deployed demo</span></div></header>
    <main className="mainSurface"><section className="workspaceIntro"><div><span className="eyebrow"><Sparkles size={15} /> {activeTab.label}</span><h1>Healthcare IT intelligence with evidence governance and transparent model evaluation.</h1></div><aside><span>Reviewer summary</span><strong>Public data · HIT boundaries · DL benchmark transparency</strong></aside></section>{tab === 'market' && <MarketBrief />}{tab === 'evidence' && <EvidenceLedger />}{tab === 'model' && <ModelLab />}{tab === 'data' && <DataHealth />}{tab === 'architecture' && <Architecture />}</main>
  </div>;
}
