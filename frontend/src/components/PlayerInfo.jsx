import '../styles/PlayerInfo.css';

export default function PlayerInfo({ player, isMe, onTarget }) {
  const hpPercent = Math.max(0, (player.hp / player.max_hp) * 100);

  return (
    <div
      className={`player-info ${isMe ? 'player-me' : 'player-opponent'} ${onTarget ? 'targetable' : ''}`}
      onClick={onTarget || undefined}
    >
      <span className="pi-name">{player.name}</span>
      <div className="pi-hp-bar">
        <div className="pi-hp-fill" style={{ width: `${hpPercent}%` }} />
        <span className="pi-hp-text">{player.hp}/{player.max_hp}</span>
      </div>
      {!isMe && <span className="pi-stat">Hand: {player.hand_count}</span>}
    </div>
  );
}
