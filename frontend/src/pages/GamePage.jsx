import { useState, useEffect, useRef } from 'react';
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
  const [selectedTargetIdx, setSelectedTargetIdx] = useState(0);
  const targetIdxRef = useRef(0);
  const targetingCardRef = useRef(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [shake, setShake] = useState('');
  const prevHpRef = useRef(null);

  const turn = gameState?.turn;
  const status = gameState?.status;

  // Screen shake on HP loss
  const myHp = gameState?.me?.hp;
  useEffect(() => {
    if (prevHpRef.current !== null && myHp !== undefined && myHp < prevHpRef.current) {
      const dmg = prevHpRef.current - myHp;
      const intensity = dmg >= 10 ? 'shake-heavy' : dmg >= 5 ? 'shake-medium' : 'shake-light';
      setShake(intensity);
      const timer = setTimeout(() => setShake(''), 400);
      return () => clearTimeout(timer);
    }
    prevHpRef.current = myHp ?? null;
  }, [myHp]);

  // Clear targeting when turn changes or game ends
  useEffect(() => { setTargetingCard(null); }, [turn, status]);
  // Reset selection when entering targeting mode
  useEffect(() => { setSelectedTargetIdx(0); targetIdxRef.current = 0; }, [targetingCard]);
  targetingCardRef.current = targetingCard;

  // Keyboard shortcuts
  const gameRef = useRef();
  const targetList = targetingCard
    ? ['opponent', ...(gameState?.opponent?.field?.map(u => u.id) || [])]
    : [];
  gameRef.current = {
    lobby_code: gameState?.lobby_code, is_my_turn: gameState?.is_my_turn,
    status: gameState?.status, pending_choice: gameState?.pending_choice,
    hand: gameState?.me?.hand, cardTemplates, targetList,
  };
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'Escape') { setTargetingCard(null); return; }
      const g = gameRef.current;
      const canPlay = g.is_my_turn && g.status === 'playing' && !g.pending_choice;

      // Target selection with arrow keys + enter
      if (g.targetList.length > 0) {
        const isUp = e.code === 'ArrowUp' || e.code === 'Numpad8';
        const isDown = e.code === 'ArrowDown' || e.code === 'Numpad2';
        const isLeft = e.code === 'ArrowLeft' || e.code === 'Numpad4';
        const isRight = e.code === 'ArrowRight' || e.code === 'Numpad6';
        const isConfirm = e.code === 'Enter' || e.code === 'NumpadEnter';
        if (isUp || isLeft) {
          e.preventDefault();
          const next = (targetIdxRef.current - 1 + g.targetList.length) % g.targetList.length;
          targetIdxRef.current = next;
          setSelectedTargetIdx(next);
          return;
        }
        if (isDown || isRight) {
          e.preventDefault();
          const next = (targetIdxRef.current + 1) % g.targetList.length;
          targetIdxRef.current = next;
          setSelectedTargetIdx(next);
          return;
        }
        if (isConfirm) {
          e.preventDefault();
          const targetId = g.targetList[targetIdxRef.current];
          if (targetId && targetingCardRef.current) {
            playCard(g.lobby_code, targetingCardRef.current, targetId);
            setTargetingCard(null);
          }
          return;
        }
      }

      if (g.targetList.length > 0) return;

      if (e.key === 'E' && e.shiftKey && canPlay) {
        endTurn(g.lobby_code);
      }
      if (e.key >= '1' && e.key <= '9' && !e.shiftKey && !e.ctrlKey && !e.altKey && canPlay && g.hand) {
        const card = g.hand[parseInt(e.key) - 1];
        if (!card) return;
        if (g.cardTemplates[card.cid]?.needs_target) {
          setTargetingCard(card.id);
        } else {
          playCard(g.lobby_code, card.id);
        }
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  if (!gameState) return null;

  const {
    lobby_code, is_my_turn, winner_name,
    log, market, turn_state, pending_choice, me, opponent,
  } = gameState;

  const canPlayCards = is_my_turn && status === 'playing' && !pending_choice && !targetingCard;
  const canBuy = is_my_turn && status === 'playing' && !pending_choice && !targetingCard;
  const isTargeting = !!targetingCard;
  const selectedTargetId = isTargeting ? targetList[selectedTargetIdx] : null;

  const handlePlayCard = (cardId) => {
    const card = me.hand.find(c => c.id === cardId);
    if (card && cardTemplates[card.cid]?.needs_target) {
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
    <div className={`game-page ${shake}`} onClick={isTargeting ? () => setTargetingCard(null) : undefined}>

      {/* Top bar */}
      <div className="top-bar">
        <button className="btn-menu" onClick={() => setMenuOpen(o => !o)}>☰</button>
        <div className="turn-info">
          Turn {turn} — {is_my_turn ? 'Your Turn' : "Opponent's Turn"}
        </div>
      </div>

      {/* Main board */}
      <div className="game-main">

        <div className={`opponent-section ${isTargeting ? 'targeting-active' : ''}`}>
          <div className="player-controls">
            <PlayerInfo player={opponent} isMe={false} onTarget={isTargeting ? () => handleTarget('opponent') : undefined} isSelected={selectedTargetId === 'opponent'} />
            <div className="resource-bar">
              <span className="rb-res rb-energy">◆ {opponent.energy}/{opponent.max_energy}</span>
              <span className="rb-res rb-gold">◈ {opponent.gold}</span>
            </div>
          </div>
          <div className="hand-row">
            <DeckPile count={opponent.deck_count} />
            <Hand faceDown count={opponent.hand_count} />
            <DiscardPile discard={opponent.discard} />
          </div>
        </div>

        <div className="battle-field">
          <Field units={opponent.field} isMe={false} onTargetUnit={isTargeting ? handleTarget : undefined} selectedTargetId={selectedTargetId} />
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
          onBuy={(cid) => buyCard(lobby_code, cid)}
          canBuy={canBuy}
          currentGold={me.gold}
        />
      </div>

      {error && <div className="game-error">{error}</div>}

      {status === 'finished' && (
        <div className={`game-over-overlay ${winner_name === me.name ? 'go-win-overlay' : 'go-loss-overlay'}`}>
          <div className={`game-over-box ${winner_name === me.name ? 'go-win' : 'go-loss'}`}>
            <h2>{winner_name === me.name ? 'Victory!' : 'Defeat'}</h2>
            <p className="go-detail">{winner_name} wins!</p>
            <button className="go-lobby-btn" onClick={resetToLobby}>Back to Lobby</button>
          </div>
        </div>
      )}

      <ChoiceModal pendingChoice={pending_choice} onResolve={(choice) => resolveChoice(lobby_code, choice)} />

      {menuOpen && (
        <div className="menu-overlay" onClick={() => setMenuOpen(false)}>
          <div className="menu-modal" onClick={e => e.stopPropagation()}>
            <div className="menu-room-code">Room: {lobby_code}</div>
            <button className="menu-item" onClick={() => { setMenuOpen(false); resetToLobby(); }}>Leave Game</button>
            <button className="menu-item menu-close" onClick={() => setMenuOpen(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
