import { useEffect, useRef } from 'react';
import '../styles/GameLog.css';

export default function GameLog({ log }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [log]);

  return (
    <div className="game-log">
      <div className="gl-header">Log</div>
      <div className="gl-entries">
        {log.map((entry, i) => (
          <div key={i} className="gl-entry">{entry}</div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
