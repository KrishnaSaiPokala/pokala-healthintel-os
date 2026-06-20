import type { LucideIcon } from 'lucide-react';
import { BarChart3, BrainCircuit, Building2, Database, FileText, GitBranch, Radar, Search, Terminal } from 'lucide-react';
import type { IntelligenceView } from '../types/intelligence';

type NavItem = {
  id: IntelligenceView;
  label: string;
  icon: LucideIcon;
};

export const navItems: NavItem[] = [
  { id: 'market', label: 'Market Brief', icon: Building2 },
  { id: 'brief', label: 'Executive Brief', icon: FileText },
  { id: 'command', label: 'Command Center', icon: Terminal },
  { id: 'investigations', label: 'Investigations', icon: Search },
  { id: 'graph', label: 'Entity Graph', icon: GitBranch },
  { id: 'safety', label: 'Safety Radar', icon: Radar },
  { id: 'reimbursement', label: 'Reimbursement', icon: BarChart3 },
  { id: 'model', label: 'Model Lab', icon: BrainCircuit },
  { id: 'evidence', label: 'Evidence Ledger', icon: Database },
];
