import '../styles/Pile.css';

export default function DeckPile({ count }) {
  return (
    <div className="pile deck-pile">
      <div className="pile-card pile-facedown" />
      <div className="pile-count">{count}</div>
    </div>
  );
}
