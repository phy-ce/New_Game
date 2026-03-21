import { useState } from 'react';
import { useGame } from '../context/GameContext';
import '../styles/Card.css';

export default function Card({ card, onClick, isPlayable, faceDown, isNew }) {
  const [showInspector, setShowInspector] = useState(false);
  const { cardTemplates } = useGame();

  if (faceDown) {
    return <div className="card card-back" />;
  }

  const template = cardTemplates[card.name] || {};
  const typeClass = template.type === 'treasure' ? 'card-treasure' : 'card-action';

  return (
    <div
      className={`card ${typeClass} ${isPlayable ? 'playable' : ''} ${isNew ? 'card-entering' : ''}`}
      onClick={isPlayable ? () => onClick(card.id) : undefined}
      onMouseEnter={() => setShowInspector(true)}
      onMouseLeave={() => setShowInspector(false)}
    >
      <div className="card-cost">{template.energy_cost}</div>
      <div className="card-image-placeholder">
        {card.name.charAt(0)}
      </div>
      <div className="card-name">{card.name}</div>
      <div className="card-effect">{template.effect}</div>

      {showInspector && (
        <div className="card-inspector">
          <div className="inspector-name">{card.name}</div>
          <div className="inspector-type">{template.type}</div>
          <div className="inspector-cost">Buy cost: {template.cost} ◈ · Play cost: {template.energy_cost} ◆</div>
          <div className="inspector-effect">{template.effect}</div>
        </div>
      )}
    </div>
  );
}
