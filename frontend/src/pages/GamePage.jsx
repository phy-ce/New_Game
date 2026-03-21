import { useState } from 'react';
import { useGame } from '../context/GameContext';
import { useSocket } from '../hooks/useSocket';
import PlayerInfo from '../components/PlayerInfo';
import Hand from '../components/Hand';
import DeckPile from '../components/DeckPile';
import DiscardPile from '../components/DiscardPile';
import Field from '../components/Field';
import PlayedStack from '../components/PlayedStack';
import Market from '../components/Market';
import GameLog from '../components/GameLog';
import ChoiceModal from '../components/ChoiceModal';
import '../styles/GamePage.css';

export default function GamePage() {
  const { gameState, error, resetToLobby, cardTemplates } = useGame();
  const { playCard, buyCard, resolveChoice, endTurn } = useSocket();
  const [targetingCard, setTargetingCard] = useState(null);

  if (!gameState) return null;

  const {
    lobby_code, status, turn, is_my_turn, winner_name,
    log, market, turn_state, pending_choice, me, opponent,
  } = gameState;

  const canPlayCards = is_my_turn && status === 'playing' && !pending_choice && !targetingCard;
  const canBuy = is_my_turn && status === 'playing' && turn_state.buys > 0 && !pending_choice && !targetingCard;
  const isTargeting = !!targetingCard;

  const handlePlayCard = (cardId) => {
    const card = me.hand.find(c => c.id === cardId);
    if (card && cardTemplates[card.name]?.needs_target) {
      setTargetingCard(cardId);
    } else {
      playCard(lobby_code, cardId);
    }
  };

  const handleTarget = (targetId) => {
    playCard(lobby_code, targetingCard, targetId);
    setTargetingCard(null);
  };

  return (
    <div className="game-page">

      {/* Turn info — top left */}
      <div className="turn-info">
        Turn {turn} — {is_my_turn ? 'Your Turn' : "Opponent's Turn"}
      </div>

      {/* Main board */}
      <div className="game-main">

        <div className={`opponent-section ${isTargeting ? 'targeting-active' : ''}`}>
          <div className="player-controls">
            <PlayerInfo player={opponent} isMe={false} onTarget={isTargeting ? () => handleTarget('opponent') : undefined} />
            <div className="resource-bar">
              <span className="rb-res rb-energy">◆ {opponent.energy}/{opponent.max_energy}</span>
              <span className="rb-res rb-gold">◈ {opponent.gold}</span>
              <span className="rb-res rb-buys">⊕ {!is_my_turn ? turn_state.buys : 0} buy{(!is_my_turn ? turn_state.buys : 0) !== 1 ? 's' : ''}</span>
            </div>
          </div>
          <div className="hand-row">
            <DeckPile count={opponent.deck_count} />
            <Hand faceDown count={opponent.hand_count} />
            <DiscardPile discard={opponent.discard} />
          </div>
        </div>

        <div className="battle-field">
          <Field units={opponent.field} isMe={false} onTargetUnit={isTargeting ? handleTarget : undefined} />
          <div className="field-divider" />
          <Field units={me.field} isMe={true} />
        </div>

        <div className="player-section">
          <div className="hand-row">
            <DeckPile count={me.deck_count} />
            <Hand
              cards={me.hand}
              onPlayCard={handlePlayCard}
              isPlayable={canPlayCards}
            />
            <DiscardPile discard={me.discard} />
          </div>
          <div className="player-controls">
            <PlayerInfo player={me} isMe />
            <div className="resource-bar">
              <span className="rb-res rb-energy">◆ {me.energy}/{me.max_energy}</span>
              <span className="rb-res rb-gold">◈ {me.gold}</span>
              <span className="rb-res rb-buys">⊕ {turn_state.buys} buy{turn_state.buys !== 1 ? 's' : ''}</span>
            </div>
            {is_my_turn && status === 'playing' && (
              <button className="btn-end-turn" onClick={() => endTurn(lobby_code)}>
                End Turn
              </button>
            )}
          </div>
        </div>

      </div>

      {/* Left sidebar: log + played stack */}
      <div className="left-sidebar">
        <div className="sidebar-played">
          <PlayedStack
            playedThisTurn={turn_state.played_this_turn}
            cardsPlayed={turn_state.cards_played}
          />
        </div>
        <div className="sidebar-log">
          <GameLog log={log || []} />
        </div>
      </div>

      {/* Right sidebar: market */}
      <div className="right-sidebar">
        <Market
          market={market}
          onBuy={(cardName) => buyCard(lobby_code, cardName)}
          canBuy={canBuy}
          currentGold={me.gold}
        />
      </div>

      {error && <div className="game-error">{error}</div>}

      {status === 'finished' && (
        <div className="game-over-overlay">
          <div className={`game-over-box ${winner_name === me.name ? 'go-win' : 'go-loss'}`}>
            <h2>{winner_name === me.name ? 'Victory!' : 'Defeat'}</h2>
            <p className="go-detail">{winner_name} wins!</p>
            <button className="go-lobby-btn" onClick={resetToLobby}>Back to Lobby</button>
          </div>
        </div>
      )}

      <ChoiceModal pendingChoice={pending_choice} onResolve={(choice) => resolveChoice(lobby_code, choice)} />
    </div>
  );
}
