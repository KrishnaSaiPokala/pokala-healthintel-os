import type { ScoreCardModel } from '../types/intelligence';
import { formatScore } from '../lib/format';

export function ScoreCard({ card }: { card: ScoreCardModel }) {
  return (
    <article className={`panel score ${card.tone}`}>
      <span>{card.label}</span>
      <strong>{formatScore(card.value)}</strong>
      <em>{card.delta} trend</em>
      <p>{card.explanation}</p>
    </article>
  );
}
