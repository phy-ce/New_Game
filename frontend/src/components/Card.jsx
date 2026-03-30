import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useGame } from '../context/GameContext';
import '../styles/Card.css';

function getTooltipStyle(anchorRect, tooltipWidth) {
  const GAP = 8;
  const left = Math.max(8, Math.min(
    anchorRect.left + anchorRect.width / 2 - tooltipWidth / 2,
    window.innerWidth - tooltipWidth - 8
  ));
  if (anchorRect.top < 160) {
    return { top: anchorRect.bottom + GAP, left };
  }
  return { top: anchorRect.top - GAP, left, transform: 'translateY(-100%)' };
}

export default function Card({ card, onClick, isPlayable, faceDown, isNew }) {
  const [tooltipStyle, setTooltipStyle] = useState(null);
  const cardRef = useRef(null);
  const { cardTemplates } = useGame();

  const handleMouseEnter = () => {
    if (!cardRef.current) return;
    setTooltipStyle(getTooltipStyle(cardRef.current.getBoundingClientRect(), 160));
  };

  const handleMouseLeave = () => setTooltipStyle(null);

  useEffect(() => () => setTooltipStyle(null), []);

  if (faceDown) {
    return <div className="card card-back" />;
  }

  const template = cardTemplates[card.cid] || {};
  const typeClass = template.type === 'treasure' ? 'card-treasure' : 'card-action';

  return (
    <div
      ref={cardRef}
      className={`card ${typeClass} ${isPlayable ? 'playable' : ''} ${isNew ? 'card-entering' : ''}`}
      onClick={isPlayable ? () => onClick(card.id) : undefined}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="card-cost">{template.energy_cost}</div>
      <div className="card-image-placeholder">
        {card.name.charAt(0)}
      </div>
      <div className="card-name">{card.name}</div>
      <div className="card-effect">{template.effect}</div>

      {tooltipStyle && createPortal(
        <div className="card-inspector card-inspector-portal" style={tooltipStyle}>
          <div className="inspector-name">{card.name}</div>
          <div className="inspector-type">{template.type}</div>
          <div className="inspector-cost">Buy cost: {template.cost} ◈ · Play cost: {template.energy_cost} ◆</div>
          <div className="inspector-effect">{template.effect}</div>
        </div>,
        document.body
      )}
    </div>
  );
}
