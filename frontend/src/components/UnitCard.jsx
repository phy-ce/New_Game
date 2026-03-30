import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useGame } from '../context/GameContext';
import FloatingDamage from './FloatingDamage';
import '../styles/UnitCard.css';

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

export default function UnitCard({ unit, stackCount, onTarget, isSelected }) {
  const { unitTemplates } = useGame();
  const [tooltipStyle, setTooltipStyle] = useState(null);
  const cardRef = useRef(null);
  const template = unitTemplates[unit.name] || {};

  const handleMouseEnter = () => {
    if (!cardRef.current) return;
    setTooltipStyle(getTooltipStyle(cardRef.current.getBoundingClientRect(), 140));
  };

  const handleMouseLeave = () => setTooltipStyle(null);

  useEffect(() => () => setTooltipStyle(null), []);

  return (
    <div
      ref={cardRef}
      className={`unit-card ${onTarget ? 'targetable' : ''} ${isSelected ? 'target-selected' : ''}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onTarget ? (e) => { e.stopPropagation(); onTarget(); } : undefined}
    >
      <FloatingDamage hp={unit.current_hp} />
      {stackCount > 1 && <div className="unit-stack-count">x{stackCount}</div>}
      <div className="unit-image">{unit.name.charAt(0)}</div>
      <div className="unit-name">{unit.name}</div>
      <div className="unit-stats">
        <span className="unit-hp">♥ {unit.current_hp}/{template.hp}</span>
        <span className="unit-attack">⚔ {template.attack}</span>
      </div>

      {tooltipStyle && createPortal(
        <div className="unit-inspector unit-inspector-portal" style={tooltipStyle}>
          <div className="ui-name">{unit.name}</div>
          <div className="ui-stat">HP: {unit.current_hp}/{template.hp}</div>
          <div className="ui-stat">ATK: {template.attack}</div>
          <div className="ui-desc">{template.description}</div>
        </div>,
        document.body
      )}
    </div>
  );
}
