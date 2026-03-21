import { useState } from 'react';
import { useGame } from '../context/GameContext';
import '../styles/Pile.css';

export default function DiscardPile({ discard }) {
  const { cardTemplates } = useGame();
  const [showList, setShowList] = useState(false);
  const top = discard[discard.length - 1];

  return (
    <div
      className="pile discard-pile"
      onMouseEnter={() => setShowList(true)}
      onMouseLeave={() => setShowList(false)}
    >
      {top ? (
        <div className="pile-card pile-faceup">
          <div className="pile-card-name">{top.name}</div>
          <div className="pile-card-type">{cardTemplates[top.name]?.type}</div>
        </div>
      ) : (
        <div className="pile-card pile-empty" />
      )}
      <div className="pile-count">{discard.length}</div>

      {showList && discard.length > 0 && (
        <div className="pile-popup">
          {[...discard].reverse().map((card, i) => (
            <div key={i} className="pile-popup-row">{card.name}</div>
          ))}
        </div>
      )}
    </div>
  );
}
