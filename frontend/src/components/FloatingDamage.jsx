import { useState, useEffect, useRef } from 'react';
import '../styles/FloatingDamage.css';

export default function FloatingDamage({ hp, direction }) {
  const [floats, setFloats] = useState([]);
  const prevHpRef = useRef(null);
  const idRef = useRef(0);

  useEffect(() => {
    if (prevHpRef.current !== null && hp !== undefined && hp < prevHpRef.current) {
      const dmg = prevHpRef.current - hp;
      const id = ++idRef.current;
      let angle;
      if (direction === 'down') {
        angle = 70 + Math.random() * 40;  // 70~110 (downward toward center)
      } else if (direction === 'up') {
        angle = 250 + Math.random() * 40; // 250~290 (upward toward center)
      } else {
        angle = Math.random() * 360;      // random 360
      }
      const rad = angle * Math.PI / 180;
      const dist = 40 + Math.random() * 20;
      const tx = Math.cos(rad) * dist;
      const ty = Math.sin(rad) * dist;
      const size = dmg >= 10 ? 2.0 : dmg >= 5 ? 1.6 : 1.2;
      setFloats(prev => [...prev, { id, dmg, tx, ty, size }]);
      setTimeout(() => setFloats(prev => prev.filter(f => f.id !== id)), 800);
    }
    prevHpRef.current = hp ?? null;
  }, [hp]);

  if (floats.length === 0) return null;

  return (
    <>
      {floats.map(f => (
        <span
          key={f.id}
          className="floating-damage"
          style={{ '--float-x': `${f.tx}px`, '--float-y': `${f.ty}px`, fontSize: `${f.size}rem` }}
        >
          -{f.dmg}
        </span>
      ))}
    </>
  );
}
