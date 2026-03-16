import '../styles/Market.css';

export default function Market({ market, onBuy, canBuy, currentGold }) {
  const piles = Object.entries(market);

  return (
    <div className="market">
      <div className="market-label">Market</div>
      <div className="market-piles">
        {piles.map(([name, pile]) => {
          const affordable = canBuy && pile.count > 0 && currentGold >= pile.template.cost;
          return (
            <div
              key={name}
              className={`market-pile ${affordable ? 'affordable' : ''} ${pile.count === 0 ? 'sold-out' : ''}`}
              onClick={affordable ? () => onBuy(name) : undefined}
            >
              <div className="mp-cost">{pile.template.cost}</div>
              <div className="mp-image">{name.charAt(0)}</div>
              <div className="mp-name">{name}</div>
              <div className="mp-effect">{pile.template.effect}</div>
              <div className="mp-count">x{pile.count}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
