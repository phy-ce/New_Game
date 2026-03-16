import { useGame } from '../context/GameContext';
import { useSocket } from '../hooks/useSocket';
import PlayerInfo from '../components/PlayerInfo';
import Hand from '../components/Hand';
import PlayArea from '../components/PlayArea';
import Market from '../components/Market';
import GameLog from '../components/GameLog';
import ChoiceModal from '../components/ChoiceModal';
import '../styles/GamePage.css';

export default function GamePage() {
  const { gameState, error, resetToLobby } = useGame();
  const { playCard, buyCard, resolveChoice, endTurn } = useSocket();

  if (!gameState) return null;

  const {
    lobby_code, status, turn, is_my_turn, winner, winner_name,
    log, market, turn_state, pending_choice, me, opponent,
  } = gameState;

  const canPlayCards = is_my_turn && status === 'playing' && turn_state.actions > 0 && !pending_choice;
  const canBuy = is_my_turn && status === 'playing' && turn_state.buys > 0 && !pending_choice;

  const handlePlayCard = (cardId) => {
    playCard(lobby_code, cardId);
  };

  const handleBuy = (cardName) => {
    buyCard(lobby_code, cardName);
  };

  const handleEndTurn = () => {
    endTurn(lobby_code);
  };

  const handleResolve = (choice) => {
    resolveChoice(lobby_code, choice);
  };

  return (
    <div className="game-page">
      <div className="game-main">
        {/* Opponent section */}
        <div className="opponent-section">
          <PlayerInfo player={opponent} isMe={false} />
          <Hand faceDown count={opponent.hand_count} />
        </div>

        {/* Center: play area + market */}
        <div className="center-section">
          <PlayArea turnState={turn_state} isMyTurn={is_my_turn} turn={turn} />
          <Market
            market={market}
            onBuy={handleBuy}
            canBuy={canBuy}
            currentGold={turn_state.gold}
          />
        </div>

        {/* Player section */}
        <div className="player-section">
          <Hand
            cards={me.hand}
            onPlayCard={handlePlayCard}
            isPlayable={canPlayCards}
          />
          <div className="player-controls">
            <PlayerInfo player={me} isMe />
            {is_my_turn && status === 'playing' && (
              <button className="btn-end-turn" onClick={handleEndTurn}>
                End Turn
              </button>
            )}
          </div>
        </div>

        {error && <div className="game-error">{error}</div>}
      </div>

      {/* Log panel on the right */}
      <GameLog log={log || []} />

      {/* Game over overlay */}
      {status === 'finished' && (
        <div className="game-over-overlay">
          <div className={`game-over-box ${winner_name === me.name ? 'go-win' : 'go-loss'}`}>
            <h2>{winner_name === me.name ? 'Victory!' : 'Defeat'}</h2>
            <p className="go-detail">{winner_name} wins!</p>
            <button className="go-lobby-btn" onClick={resetToLobby}>
              Back to Lobby
            </button>
          </div>
        </div>
      )}

      {/* Choice modal */}
      <ChoiceModal pendingChoice={pending_choice} onResolve={handleResolve} />
    </div>
  );
}
