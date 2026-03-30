import { useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useGame } from '../context/GameContext';
import '../styles/Pile.css';

const POPUP_WIDTH = 120;
const GAP = 8;

function getPopupStyle(rect) {
  const left = Math.max(8, Math.min(
    rect.left + rect.width / 2 - POPUP_WIDTH / 2,
    window.innerWidth - POPUP_WIDTH - 8
  ));
  if (rect.top < 220) {
    return { top: rect.bottom + GAP, left };
  }
  return { top: rect.top - GAP, left, transform: 'translateY(-100%)' };
}

export default function DiscardPile({ discard }) {
  const { cardTemplates } = useGame();
  const [popupStyle, setPopupStyle] = useState(null);
  const pileRef = useRef(null);
  const top = discard[discard.length - 1];

  const handleMouseEnter = () => {
    if (!pileRef.current) return;
    setPopupStyle(getPopupStyle(pileRef.current.getBoundingClientRect()));
  };

  return (
    <div
      ref={pileRef}
      className="pile discard-pile"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setPopupStyle(null)}
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

      {popupStyle && discard.length > 0 && createPortal(
        <div className="pile-popup pile-popup-portal" style={popupStyle}>
          {[...discard].reverse().map((card, i) => (
            <div key={i} className="pile-popup-row">{card.name}</div>
          ))}
        </div>,
        document.body
      )}
    </div>
  );
}
