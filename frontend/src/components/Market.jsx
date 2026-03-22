import { useState, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useGame } from '../context/GameContext';
import '../styles/Market.css';

const TOOLTIP_WIDTH = 170;
const GAP = 8;

function getTooltipStyle(rect) {
  const left = Math.max(8, Math.min(
    rect.left + rect.width / 2 - TOOLTIP_WIDTH / 2,
    window.innerWidth - TOOLTIP_WIDTH - 8
  ));
  if (rect.top < 160) {
    return { top: rect.bottom + GAP, left };
  }
  return { top: rect.top - GAP, left, transform: 'translateY(-100%)' };
}

export default function Market({ market, onBuy, canBuy, currentGold }) {
  const { cardTemplates } = useGame();
  const [tooltip, setTooltip] = useState(null); // { name, style }
  const piles = Object.entries(market);

  const handleMouseEnter = useCallback((e, name) => {
    setTooltip({ name, style: getTooltipStyle(e.currentTarget.getBoundingClientRect()) });
  }, []);

  const handleMouseLeave = useCallback(() => setTooltip(null), []);

  return (
    <div className="market">
      <div className="market-label">Market</div>
      <div className="market-piles">
        {piles.map(([name, pile]) => {
          const template = cardTemplates[name] || {};
          const affordable = canBuy && pile.count > 0 && currentGold >= template.cost;
          return (
            <div
              key={name}
              className={`market-pile ${affordable ? 'affordable' : ''} ${pile.count === 0 ? 'sold-out' : ''}`}
              onClick={affordable ? () => onBuy(name) : undefined}
              onMouseEnter={(e) => handleMouseEnter(e, name)}
              onMouseLeave={handleMouseLeave}
            >
              <div className="mp-gold-cost">◈ {template.cost}</div>
              <div className="mp-image">{name.charAt(0)}</div>
              <div className="mp-name">{name}</div>
              <div className="mp-effect">{template.effect}</div>
              <div className="mp-energy-cost">◆ {template.energy_cost}</div>
              <div className="mp-count">x{pile.count}</div>
            </div>
          );
        })}
      </div>

      {tooltip && createPortal(
        <div className="mp-inspector mp-inspector-portal" style={tooltip.style}>
          <div className="mpi-name">{tooltip.name}</div>
          <div className="mpi-type">{cardTemplates[tooltip.name]?.type}</div>
          <div className="mpi-costs">
            <span className="mpi-gold">◈ {cardTemplates[tooltip.name]?.cost}</span>
            <span className="mpi-energy">◆ {cardTemplates[tooltip.name]?.energy_cost} to play</span>
          </div>
          <div className="mpi-effect">{cardTemplates[tooltip.name]?.effect}</div>
        </div>,
        document.body
      )}
    </div>
  );
}
