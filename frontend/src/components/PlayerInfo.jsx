import '../styles/PlayerInfo.css';

export default function PlayerInfo({ player, isMe, onTarget }) {
  const hpPercent = Math.max(0, (player.hp / player.max_hp) * 100);

  return (
    <div
      className={`player-info ${isMe ? 'player-me' : 'player-opponent'} ${onTarget ? 'targetable' : ''}`}
      onClick={onTarget || undefined}
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
      {!isMe && <span className="pi-stat">Hand: {player.hand_count}</span>}
    </div>
  );
}
