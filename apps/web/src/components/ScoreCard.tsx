import type { ScoreCardModel } from '../types/intelligence';

const toneLabel: Record<ScoreCardModel['tone'], string> = {
  cyan: 'Market',
  green: 'Economic',
  amber: 'Governance',
  red: 'Risk'
};

export function ScoreCard({ card }: { card: ScoreCardModel }) {
  const value = Math.max(0, Math.min(100, Math.round(card.value)));

  return (
    <article className={`signalTile ${card.tone}`}>
      <div className="signalTileHeader">
        <span>{card.label}</span>
        <em>{toneLabel[card.tone]}</em>
      </div>

      <div className="signalTileBody">
        <div className="signalNumber">
          <strong>{value}</strong>
          <small>/100</small>
        </div>
        <div className="signalDelta">{card.delta}</div>
      </div>

      <div className="signalRail" aria-hidden="true">
        <i style={{ width: Math.max(8, value) + '%' }} />
      </div>

      <p>{card.explanation}</p>
    </article>
  );
}

