export type IntelligenceView =
  | 'market'
  | 'command'
  | 'investigations'
  | 'graph'
  | 'safety'
  | 'reimbursement'
  | 'model'
  | 'evidence'
  | 'data';


export interface IntelligenceMeta {
  runId: string;
  status: string;
  refresh: string;
  evidenceRows: number;
  sources: number;
}

export interface IntelligenceScores {
  market: number;
  safety: number;
  reimbursement: number;
  providerDensity: number;
}

export interface TemporalPoint {
  period: string;
  market: number;
  safety: number;
  reimbursement: number;
}

export interface RadarPoint {
  axis: string;
  value: number;
}

export interface GraphNode {
  id: string;
  label: string;
}

export type GraphEdge = [string, string];

export interface EntityGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface DatasetHealth {
  name: string;
  rows: number;
  status: string;
}

export interface EvidenceItem {
  id: string;
  claim: string;
  source: string;
  freshness: string;
  rows: number;
}

export interface IntelligenceSnapshot {
  meta: IntelligenceMeta;
  scores: IntelligenceScores;
  temporal: TemporalPoint[];
  radar: RadarPoint[];
  graph: EntityGraph;
  datasets: DatasetHealth[];
  evidence: EvidenceItem[];
}

export interface ScoreCardModel {
  label: string;
  value: number;
  delta: string;
  tone: 'cyan' | 'green' | 'amber' | 'red';
  explanation: string;
}
