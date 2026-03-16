import Card from './Card';
import '../styles/Hand.css';

export default function Hand({ cards, onPlayCard, isPlayable, faceDown, count }) {
  // If face down, render 'count' card backs
  if (faceDown) {
    return (
      <div className="hand hand-opponent">
        {Array.from({ length: count }, (_, i) => (
          <Card key={i} faceDown />
        ))}
      </div>
    );
  }

  return (
    <div className="hand">
      {cards.map((card) => (
        <Card
          key={card.id}
          card={card}
          onClick={onPlayCard}
          isPlayable={isPlayable}
        />
      ))}
    </div>
  );
}
