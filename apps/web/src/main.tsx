import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, AlertTriangle, BarChart3, BrainCircuit, Database, FileText, GitBranch, Lock, Map, Radar, Search, ShieldCheck, Terminal, Zap } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar as RadarShape } from 'recharts';
import './styles/global.css';
import intelligence from './data/intelligence.json';

type View = 'command' | 'investigations' | 'graph' | 'safety' | 'reimbursement' | 'model' | 'data' | 'brief';

const nav = [
  ['command', 'Command Center', Terminal],
  ['investigations', 'Investigations', Search],
  ['graph', 'Entity Graph', GitBranch],
  ['safety', 'Safety Radar', Radar],
  ['reimbursement', 'Reimbursement', BarChart3],
  ['model', 'Model Lab', BrainCircuit],
  ['data', 'Data Health', Database],
  ['brief', 'Executive Brief', FileText],
] as const;

const scoreCards = [
  { label: 'Market Attractiveness', value: intelligence.scores.market, delta: '+12.4%', tone: 'cyan' },
  { label: 'Safety Momentum Risk', value: intelligence.scores.safety, delta: '+6.8%', tone: 'amber' },
  { label: 'Reimbursement Signal', value: intelligence.scores.reimbursement, delta: '+9.1%', tone: 'green' },
  { label: 'Provider Density', value: intelligence.scores.providerDensity, delta: '+4.6%', tone: 'cyan' },
];

function App() {
  const [view, setView] = useState<View>('command');
  const [workspace, setWorkspace] = useState('Texas Radiology AI Market');
  return <div className="shell">
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
        <input value={workspace} onChange={e=>setWorkspace(e.target.value)} />
      </div>
      <nav>
        {nav.map(([id,label,Icon]) => <button key={id} className={view===id?'active':''} onClick={()=>setView(id as View)}><Icon size={17}/>{label}</button>)}
      </nav>
      <div className="opsCard">
        <ShieldCheck size={20}/>
        <div>
          <strong>No PHI runtime</strong>
          <span>Public snapshots · Browser compute · Evidence lineage</span>
        </div>
      </div>
    </aside>
    <main>
      <Header />
      {view==='command' && <CommandCenter />}
      {view==='investigations' && <Investigations />}
      {view==='graph' && <EntityGraph />}
      {view==='safety' && <SafetyRadar />}
      {view==='reimbursement' && <Reimbursement />}
      {view==='model' && <ModelLab />}
      {view==='data' && <DataHealth />}
      {view==='brief' && <ExecutiveBrief />}
    </main>
  </div>
}

function Header(){ return <header className="topbar">
  <div>
    <div className="eyebrow">Browser-native healthcare intelligence SaaS</div>
    <h2>Temporal market-risk intelligence for AI healthcare commercialization.</h2>
  </div>
  <div className="topActions">
    <button className="ghost"><Lock size={16}/> No Login</button>
    <button className="primary"><Zap size={16}/> Generate Memo</button>
  </div>
</header> }

function CommandCenter(){ return <section className="gridPage">
  <div className="heroPanel span8">
    <div className="eyebrow">Flagship investigation</div>
    <h3>Should an AI imaging workflow company enter the Texas radiology market?</h3>
    <p>Cross-source evidence from provider density, Medicare utilization, FDA device-event momentum, clinical trials, public payment signals, and breach exposure.</p>
    <div className="heroStats">
      <Metric label="Evidence rows" value={intelligence.meta.evidenceRows.toLocaleString()} />
      <Metric label="Sources" value={String(intelligence.meta.sources)} />
      <Metric label="Refresh" value={intelligence.meta.refresh} />
    </div>
  </div>
  <div className="panel span4 terminalPanel">
    <div className="eyebrow">Pipeline status</div>
    <pre>{`run: ${intelligence.meta.runId}\nmode: CPU-first\nmodel: temporal-transformer-lite\nstatus: ${intelligence.meta.status}\nlineage: verified`}</pre>
  </div>
  {scoreCards.map(c => <ScoreCard key={c.label} {...c}/>) }
  <div className="panel span7"><PanelTitle icon={Activity} title="Temporal signal track"/><ResponsiveContainer height={260}><LineChart data={intelligence.temporal}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)"/><XAxis dataKey="period" stroke="#7d8aa5"/><YAxis stroke="#7d8aa5"/><Tooltip contentStyle={{background:'#0a1020', border:'1px solid rgba(255,255,255,.14)', color:'#fff'}}/><Line type="monotone" dataKey="market" strokeWidth={3}/><Line type="monotone" dataKey="safety" strokeWidth={3}/><Line type="monotone" dataKey="reimbursement" strokeWidth={3}/></LineChart></ResponsiveContainer></div>
  <div className="panel span5"><PanelTitle icon={Radar} title="Opportunity / risk radar"/><ResponsiveContainer height={260}><RadarChart data={intelligence.radar}><PolarGrid stroke="rgba(255,255,255,.12)"/><PolarAngleAxis dataKey="axis" stroke="#9aa6c0"/><PolarRadiusAxis stroke="#64708a"/><RadarShape dataKey="value" fillOpacity={0.32}/></RadarChart></ResponsiveContainer></div>
</section> }

function Investigations(){ return <section className="gridPage">
  <div className="panel span12"><PanelTitle icon={Search} title="Investigation Builder"/><div className="builder"><Field label="Region" value="Texas"/><Field label="Specialty" value="Radiology"/><Field label="Product thesis" value="AI imaging workflow automation"/><button className="primary">Run Public Evidence Dossier</button></div></div>
  <div className="panel span6"><PanelTitle icon={FileText} title="Generated executive memo"/><Memo /></div>
  <div className="panel span6"><PanelTitle icon={Database} title="Evidence drawer"/><Evidence /></div>
</section> }

function EntityGraph(){ return <section className="gridPage">
  <div className="panel span12 graphPanel"><PanelTitle icon={GitBranch} title="Healthcare Entity Graph"/><div className="graphCanvas">{intelligence.graph.nodes.map((n:any,i:number)=><div key={n.id} className={`node n${i}`}>{n.label}</div>)}{intelligence.graph.edges.map((e:any,i:number)=><div key={i} className={`edge e${i}`}/>)}</div></div>
</section> }

function SafetyRadar(){ return <section className="gridPage">
  <div className="panel span8"><PanelTitle icon={AlertTriangle} title="FDA device-event momentum"/><ResponsiveContainer height={300}><BarChart data={intelligence.temporal}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)"/><XAxis dataKey="period" stroke="#7d8aa5"/><YAxis stroke="#7d8aa5"/><Tooltip contentStyle={{background:'#0a1020', border:'1px solid rgba(255,255,255,.14)', color:'#fff'}}/><Bar dataKey="safety" radius={[8,8,0,0]}/></BarChart></ResponsiveContainer></div>
  <div className="panel span4"><PanelTitle icon={ShieldCheck} title="Safety interpretation"/><p className="largeText">Safety momentum is elevated but not disqualifying. The platform flags acceleration rather than absolute event count, so reviewers can inspect underlying evidence before acting.</p></div>
</section> }

function Reimbursement(){ return <section className="gridPage">
  <div className="panel span7"><PanelTitle icon={BarChart3} title="Reimbursement variability"/><ResponsiveContainer height={280}><LineChart data={intelligence.temporal}><CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.08)"/><XAxis dataKey="period" stroke="#7d8aa5"/><YAxis stroke="#7d8aa5"/><Tooltip contentStyle={{background:'#0a1020', border:'1px solid rgba(255,255,255,.14)', color:'#fff'}}/><Line type="monotone" dataKey="reimbursement" strokeWidth={3}/></LineChart></ResponsiveContainer></div>
  <div className="panel span5"><PanelTitle icon={Map} title="Market signal"/><p className="largeText">Reimbursement volatility is treated as both opportunity and risk: high spread may suggest monetizable workflow gaps, but also payer friction and implementation variability.</p></div>
</section> }

function ModelLab(){ return <section className="gridPage">
  <div className="panel span12"><PanelTitle icon={BrainCircuit} title="Temporal Transformer Intelligence Layer"/><div className="attentionGrid">
    {['UTILIZATION_VOLUME','MEDICARE_PAYMENT','PRICE_SPREAD','FDA_EVENT_RATE','TRIAL_DENSITY','BREACH_HISTORY','PROVIDER_DENSITY','AI_DEVICE_ACTIVITY'].map((t,i)=><div className="token" key={t}><span>{t}</span><b>{(0.42+i*0.06).toFixed(2)}</b></div>)}
  </div><p className="largeText">The production MVP uses deterministic scoring. The Model Lab adds a lightweight temporal transformer that studies monthly or quarterly signal sequences and classifies momentum, anomaly, and risk direction.</p></div>
  <div className="panel span6"><PanelTitle icon={Activity} title="Architecture"/><pre className="code">{`signal tokens\n  ↓\npositional encoding\n  ↓\nmulti-head self-attention\n  ↓\nfeed-forward block\n  ↓\nrisk / opportunity heads\n  ↓\nevidence-backed scores`}</pre></div>
  <div className="panel span6"><PanelTitle icon={Terminal} title="Baseline discipline"/><pre className="code">{`Baseline: rolling z-score + GRU\nPrimary: temporal transformer encoder\nDeployment: offline inference\nRuntime: static JSON/Parquet outputs\nGPU: optional GTX 1660 Ti local training`}</pre></div>
</section> }

function DataHealth(){ return <section className="gridPage">
  {intelligence.datasets.map((d:any)=><div className="panel span4" key={d.name}><div className="dataset"><Database size={18}/><strong>{d.name}</strong><span>{d.rows.toLocaleString()} rows</span><em>{d.status}</em></div></div>)}
</section> }

function ExecutiveBrief(){ return <section className="gridPage">
  <div className="panel span12"><PanelTitle icon={FileText} title="Executive Brief"/><h3>Pokala HealthIntel OS</h3><p className="largeText">A browser-native healthcare intelligence SaaS that converts public evidence into market, safety, reimbursement, and AI-risk dossiers. It is designed to demonstrate elite platform engineering, health data engineering, and applied AI architecture without PHI, paid APIs, or a hosted backend bill.</p><Memo /></div>
</section> }

function Metric({label,value}:{label:string,value:string}){return <div><span>{label}</span><strong>{value}</strong></div>}
function ScoreCard({label,value,delta,tone}:{label:string,value:number,delta:string,tone:string}){return <div className={`panel score ${tone}`}><span>{label}</span><strong>{value}</strong><em>{delta} trend</em></div>}
function PanelTitle({icon:Icon,title}:{icon:any,title:string}){return <div className="panelTitle"><Icon size={18}/><h3>{title}</h3></div>}
function Field({label,value}:{label:string,value:string}){return <label><span>{label}</span><input defaultValue={value}/></label>}
function Memo(){return <div className="memo"><p><b>Recommendation:</b> Proceed with targeted Texas radiology AI market exploration, but prioritize safety-governance messaging and payer-friction reduction.</p><p><b>Why:</b> Provider density and reimbursement activity are favorable, while FDA device-event momentum requires evidence-backed risk controls.</p><p><b>Next motion:</b> Position as workflow intelligence, not autonomous diagnosis. Lead with auditability, clinical review, and measurable operating leverage.</p></div>}
function Evidence(){return <ul className="evidence">{intelligence.evidence.map((e:any)=><li key={e.id}><b>{e.claim}</b><span>{e.source} · {e.freshness} · rows {e.rows.toLocaleString()}</span></li>)}</ul>}

createRoot(document.getElementById('root')!).render(<App />);
