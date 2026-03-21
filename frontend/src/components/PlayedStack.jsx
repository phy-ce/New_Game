import { useState } from 'react';
import Card from './Card';
import '../styles/PlayedStack.css';

export default function PlayedStack({ playedThisTurn, cardsPlayed }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="played-stack">
      <div className="ps-label">Played this turn ({cardsPlayed})</div>
      {playedThisTurn.length > 0 ? (
        <div className="ps-cards" onClick={() => setOpen(true)}>
          <Card card={playedThisTurn[0]} />
        </div>
      ) : (
        <div className="ps-empty">None</div>
      )}

      {open && (
        <div className="ps-overlay" onClick={() => setOpen(false)}>
          <div className="ps-modal" onClick={e => e.stopPropagation()}>
            <div className="ps-modal-header">
              <span>Played this turn ({cardsPlayed})</span>
              <button className="ps-close" onClick={() => setOpen(false)}>✕</button>
            </div>
            <div className="ps-modal-cards">
              {playedThisTurn.map((card, i) => (
                <Card key={i} card={card} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
