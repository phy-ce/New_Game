import Card from './Card';
import TurnStats from './TurnStats';
import '../styles/PlayArea.css';

export default function PlayArea({ turnState, isMyTurn, turn }) {
  return (
    <div className="play-area">
      <div className="play-area-card">
        {turnState.last_played ? (
          <>
            <div className="pa-label">Last Played</div>
            <Card card={turnState.last_played} />
          </>
        ) : (
          <div className="pa-empty">No cards played yet</div>
        )}
      </div>
      <TurnStats turnState={turnState} isMyTurn={isMyTurn} turn={turn} />
    </div>
  );
}
