import { BarChart3, BrainCircuit, Database, FileText, GitBranch, Radar, Search, Terminal, Building2 } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { IntelligenceView } from '../types/intelligence';

export interface NavItem {
  id: IntelligenceView;
  label: string;
  icon: LucideIcon;
}

export const navItems: NavItem[] = [
  
  { id: 'market', label: 'Market Brief', icon: Building2 },
  { id: 'graph', label: 'Entity Graph', icon: GitBranch },
  { id: 'safety', label: 'Safety Radar', icon: Radar },
  { id: 'reimbursement', label: 'Reimbursement', icon: BarChart3 },
  { id: 'model', label: 'Model Lab', icon: BrainCircuit },
  { id: 'data', label: 'Data Health', icon: Database },
  { id: 'brief', label: 'Executive Brief', icon: FileText }
];
