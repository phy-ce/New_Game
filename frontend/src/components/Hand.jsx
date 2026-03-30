import { useRef, useEffect, useState } from 'react';
import Card from './Card';
import '../styles/Hand.css';

function getFanStyle(index, total) {
  if (total <= 1) return {};
  const mid = (total - 1) / 2;
  const offset = index - mid;
  const maxAngle = Math.min(total * 2, 30);
  const angle = (offset / mid) * maxAngle;
  const lift = Math.pow(offset, 2) * 1.5;
  return {
    transform: `rotate(${angle}deg) translateY(${lift}px)`,
    zIndex: index,
  };
}

export default function Hand({ cards, onPlayCard, isPlayable, faceDown, count }) {
  const prevIdsRef = useRef(new Set());
  const [newIds, setNewIds] = useState(new Set());

  useEffect(() => {
    if (!cards) return;
    const currentIds = new Set(cards.map(c => c.id));
    const added = new Set([...currentIds].filter(id => !prevIdsRef.current.has(id)));
    if (added.size > 0) {
      setNewIds(added);
      const timer = setTimeout(() => setNewIds(new Set()), 400);
      prevIdsRef.current = currentIds;
      return () => clearTimeout(timer);
    }
    prevIdsRef.current = currentIds;
  }, [cards]);

  if (faceDown) {
    return (
      <div className="hand hand-opponent">
        {Array.from({ length: count }, (_, i) => (
          <Card key={i} faceDown />
        ))}
      </div>
    );
  }

  const total = cards.length;

  return (
    <div className="hand">
      {cards.map((card, i) => (
        <div key={card.id} className="hand-card-wrapper" style={getFanStyle(i, total)}>
          <Card
            card={card}
            onClick={onPlayCard}
            isPlayable={isPlayable}
            isNew={newIds.has(card.id)}
          />
        </div>
      ))}
    </div>
  );
}
