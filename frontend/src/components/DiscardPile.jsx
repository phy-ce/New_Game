import { useState } from 'react';
import { useGame } from '../context/GameContext';
import Card from './Card';
import '../styles/Pile.css';

export default function DiscardPile({ discard }) {
  const { cardTemplates } = useGame();
  const [open, setOpen] = useState(false);
  const top = discard[discard.length - 1];

  return (
    <>
      <div
        className="pile discard-pile"
        onClick={() => discard.length > 0 && setOpen(true)}
      >
        {top ? (
          <div className="pile-card pile-faceup">
            <div className="pile-card-name">{top.name}</div>
            <div className="pile-card-type">{cardTemplates[top.cid]?.type}</div>
          </div>
        ) : (
          <div className="pile-card pile-empty" />
        )}
        <div className="pile-count">{discard.length}</div>
      </div>

      {open && (
        <div className="ps-overlay" onClick={() => setOpen(false)}>
          <div className="ps-modal" onClick={e => e.stopPropagation()}>
            <div className="ps-modal-header">
              <span>Discard ({discard.length})</span>
              <button className="ps-close" onClick={() => setOpen(false)}>✕</button>
            </div>
            <div className="ps-modal-cards">
              {[...discard].reverse().map((card, i) => (
                <Card key={i} card={card} />
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
