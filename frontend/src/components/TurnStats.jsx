import '../styles/TurnStats.css';

export default function TurnStats({ turnState, isMyTurn, turn }) {
  return (
    <div className="turn-stats">
      <div className="ts-turn">Turn {turn}</div>
      <div className="ts-indicator">
        {isMyTurn ? 'Your Turn' : "Opponent's Turn"}
      </div>
      <div className="ts-resources">
        <span className="ts-res ts-played">Played: {turnState.cards_played}</span>
      </div>
    </div>
  );
}
