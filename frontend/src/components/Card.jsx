import { useState } from 'react';
import '../styles/Card.css';

export default function Card({ card, onClick, isPlayable, faceDown }) {
  const [showInspector, setShowInspector] = useState(false);

  if (faceDown) {
    return <div className="card card-back" />;
  }

  const typeClass = card.type === 'treasure' ? 'card-treasure' : 'card-action';

  return (
    <div
      className={`card ${typeClass} ${isPlayable ? 'playable' : ''}`}
      onClick={isPlayable ? () => onClick(card.id) : undefined}
      onMouseEnter={() => setShowInspector(true)}
      onMouseLeave={() => setShowInspector(false)}
    >
      <div className="card-cost">{card.cost}</div>
      <div className="card-image-placeholder">
        {card.name.charAt(0)}
      </div>
      <div className="card-name">{card.name}</div>
      <div className="card-effect">{card.effect}</div>

      {showInspector && (
        <div className="card-inspector">
          <div className="inspector-name">{card.name}</div>
          <div className="inspector-type">{card.type}</div>
          <div className="inspector-cost">Cost: {card.cost}</div>
          <div className="inspector-effect">{card.effect}</div>
        </div>
      )}
    </div>
  );
}
