import type { IntelligenceSnapshot, ScoreCardModel } from '../types/intelligence';
import { clampScore } from './format';

export function buildScoreCards(snapshot: IntelligenceSnapshot): ScoreCardModel[] {
  const { scores } = snapshot;

  return [
    {
      label: 'Market Attractiveness',
      value: clampScore(scores.market),
      delta: '+12.4%',
      tone: 'cyan',
      explanation: 'Provider concentration and utilization momentum are strong.'
    },
    {
      label: 'Safety Momentum Risk',
      value: clampScore(scores.safety),
      delta: '+6.8%',
      tone: 'amber',
      explanation: 'Event momentum requires governance review before action.'
    },
    {
      label: 'Reimbursement Signal',
      value: clampScore(scores.reimbursement),
      delta: '+9.1%',
      tone: 'green',
      explanation: 'Payment patterns support workflow ROI with payer caveats.'
    },
    {
      label: 'Provider Density',
      value: clampScore(scores.providerDensity),
      delta: '+4.6%',
      tone: 'cyan',
      explanation: 'Specialty supply supports targeted regional segmentation.'
    }
  ];
}

export function computeCompositeOpportunity(snapshot: IntelligenceSnapshot): number {
  const s = snapshot.scores;
  return clampScore((s.market * 0.36) + (s.reimbursement * 0.28) + (s.providerDensity * 0.22) + ((100 - s.safety) * 0.14));
}

export function classifySignal(value: number): 'low' | 'moderate' | 'high' {
  if (value >= 75) return 'high';
  if (value >= 50) return 'moderate';
  return 'low';
}

