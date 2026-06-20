import type { LucideIcon } from 'lucide-react';
import { BrainCircuit, Building2, Database, ShieldCheck } from 'lucide-react';
import type { IntelligenceView } from '../types/intelligence';

type NavItem = {
  id: IntelligenceView;
  label: string;
  icon: LucideIcon;
};

export const navItems: NavItem[] = [
  { id: 'market', label: 'Market Brief', icon: Building2 },
  { id: 'evidence', label: 'Evidence Ledger', icon: ShieldCheck },
  { id: 'model', label: 'Model Lab', icon: BrainCircuit },
  { id: 'data', label: 'Data Health', icon: Database },
];
