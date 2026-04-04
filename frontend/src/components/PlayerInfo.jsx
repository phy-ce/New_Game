import { useState } from 'react';
import { useGame } from '../context/GameContext';
import FloatingDamage from './FloatingDamage';
import '../styles/PlayerInfo.css';

export default function PlayerInfo({ player, isMe, onTarget, isSelected }) {
  const { passiveInfo, relicTemplates } = useGame();
  const [showPassives, setShowPassives] = useState(false);
  const [expandedPassive, setExpandedPassive] = useState(null);
  const [relicTooltip, setRelicTooltip] = useState(null);
  const hpPercent = Math.max(0, (player.hp / player.max_hp) * 100);
  const passives = player.passives || [];
  const relics = player.relics || [];

  return (
    <div
      className={`player-info ${isMe ? 'player-me' : 'player-opponent'} ${onTarget ? 'targetable' : ''} ${isSelected ? 'target-selected' : ''}`}
      onClick={onTarget ? (e) => { e.stopPropagation(); onTarget(); } : undefined}
    >
      <FloatingDamage hp={player.hp} direction={isMe ? 'up' : 'down'} />
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

      {relics.length > 0 && (
        <div className="pi-relics-row">
          {relics.map((r, i) => {
            const tmpl = relicTemplates[r.rid] || {};
            return (
              <div
                key={i}
                className="pi-relic-icon"
                onMouseEnter={() => setRelicTooltip(r.rid)}
                onMouseLeave={() => setRelicTooltip(null)}
              >
                {r.name?.charAt(0)}
                {relicTooltip === r.rid && (
                  <div className="pi-relic-tooltip">
                    <div className="pi-relic-tooltip-name">{tmpl.name}</div>
                    <div className="pi-relic-tooltip-desc">{tmpl.description}</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {showPassives && (
        <div className="ps-overlay" onClick={() => { setShowPassives(false); setExpandedPassive(null); }}>
          <div className="ps-modal" onClick={e => e.stopPropagation()}>
            <div className="ps-modal-header">
              <span>{player.name}'s Passives</span>
              <button className="ps-close" onClick={() => { setShowPassives(false); setExpandedPassive(null); }}>✕</button>
            </div>
            <div className="pi-passive-list">
              {passives.map((p, i) => (
                <div key={i}>
                  <div
                    className={`pi-passive-row ${expandedPassive === p.name ? 'pi-passive-expanded' : ''}`}
                    onClick={() => setExpandedPassive(expandedPassive === p.name ? null : p.name)}
                  >
                    <span className="pi-passive-name">{p.name}</span>
                    <span className="pi-passive-stacks">x{p.stacks}</span>
                  </div>
                  {expandedPassive === p.name && passiveInfo[p.name] && (
                    <div className="pi-passive-desc">{passiveInfo[p.name].description}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
