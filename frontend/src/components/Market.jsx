import { useState } from 'react';
import { useGame } from '../context/GameContext';
import '../styles/Market.css';

export default function Market({ market, onBuy, canBuy, currentGold }) {
  const { cardTemplates } = useGame();
  const [hoveredPile, setHoveredPile] = useState(null);
  const piles = Object.entries(market);

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
              onMouseEnter={() => setHoveredPile(name)}
              onMouseLeave={() => setHoveredPile(null)}
            >
              <div className="mp-gold-cost">◈ {template.cost}</div>
              <div className="mp-image">{name.charAt(0)}</div>
              <div className="mp-name">{name}</div>
              <div className="mp-effect">{template.effect}</div>
              <div className="mp-energy-cost">◆ {template.energy_cost}</div>
              <div className="mp-count">x{pile.count}</div>

              {hoveredPile === name && (
                <div className="mp-inspector">
                  <div className="mpi-name">{name}</div>
                  <div className="mpi-type">{template.type}</div>
                  <div className="mpi-costs">
                    <span className="mpi-gold">◈ {template.cost} to buy</span>
                    <span className="mpi-energy">◆ {template.energy_cost} to play</span>
                  </div>
                  <div className="mpi-effect">{template.effect}</div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
