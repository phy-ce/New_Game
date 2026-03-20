import { useGame } from '../context/GameContext';
import '../styles/Market.css';

export default function Market({ market, onBuy, canBuy, currentGold }) {
  const { cardTemplates } = useGame();
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
            >
              <div className="mp-cost">{template.cost}</div>
              <div className="mp-image">{name.charAt(0)}</div>
              <div className="mp-name">{name}</div>
              <div className="mp-effect">{template.effect}</div>
              <div className="mp-count">x{pile.count}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
