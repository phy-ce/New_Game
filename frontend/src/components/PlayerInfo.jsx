import { useState } from 'react';
import '../styles/PlayerInfo.css';

export default function PlayerInfo({ player, isMe, onTarget }) {
  const [showPassives, setShowPassives] = useState(false);
  const hpPercent = Math.max(0, (player.hp / player.max_hp) * 100);
  const passives = player.passives || [];

  return (
    <div
      className={`player-info ${isMe ? 'player-me' : 'player-opponent'} ${onTarget ? 'targetable' : ''}`}
      onClick={onTarget ? (e) => { e.stopPropagation(); onTarget(); } : undefined}
    >
      <span className="pi-name">{player.name}</span>
      <div className="pi-hp-row">
        <div className="pi-hp-bar">
          <div className="pi-hp-fill" style={{ width: `${hpPercent}%` }} />
          {player.block > 0 && (
            hpPercent >= 100
              ? <div className="pi-block-fill pi-block-overlay" />
              : <div className="pi-block-fill" style={{ left: `${hpPercent}%`, width: `${Math.min(100 - hpPercent, (player.block / player.max_hp) * 100)}%` }} />
          )}
          <span className="pi-hp-text">{player.hp}/{player.max_hp}</span>
        </div>
        <span className="pi-block" style={{ visibility: player.block > 0 ? 'visible' : 'hidden' }}>🛡 {player.block}</span>
      </div>
      <div className="pi-stats-row">
        {player.strength > 0 && <span className="pi-strength">⚔ {player.strength}</span>}
        {!isMe && <span className="pi-stat">Hand: {player.hand_count}</span>}
        {passives.length > 0 && (
          <span
            className="pi-passive-icon"
            onClick={(e) => { e.stopPropagation(); setShowPassives(true); }}
          >
            ★ {passives.length}
          </span>
        )}
      </div>

      {showPassives && (
        <div className="ps-overlay" onClick={() => setShowPassives(false)}>
          <div className="ps-modal" onClick={e => e.stopPropagation()}>
            <div className="ps-modal-header">
              <span>{player.name}'s Passives</span>
              <button className="ps-close" onClick={() => setShowPassives(false)}>✕</button>
            </div>
            <div className="pi-passive-list">
              {passives.map((p, i) => (
                <div key={i} className="pi-passive-row">
                  <span className="pi-passive-name">{p.name}</span>
                  <span className="pi-passive-stacks">x{p.stacks}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
