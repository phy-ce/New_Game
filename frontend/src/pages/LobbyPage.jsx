import { useState } from 'react';
import { useGame } from '../context/GameContext';
import { useSocket } from '../hooks/useSocket';
import '../styles/LobbyPage.css';

export default function LobbyPage() {
  const { lobbyCode, error, lobbyPlayers, playerName, setPlayerName, resetToLobby } = useGame();
  const { createGame, joinGame, reconnectGame, startGame } = useSocket();

  const [joinCode, setJoinCode] = useState('');
  const [nameInput, setNameInput] = useState('');
  const [mode, setMode] = useState(null); // null, 'create', 'join', 'reconnect'

  const handleCreate = (e) => {
    e.preventDefault();
    if (!nameInput.trim()) return;
    setPlayerName(nameInput.trim());
    createGame(nameInput.trim());
  };

  const handleJoin = (e) => {
    e.preventDefault();
    if (!nameInput.trim() || !joinCode.trim()) return;
    setPlayerName(nameInput.trim());
    joinGame(joinCode.trim(), nameInput.trim());
  };

  const handleReconnect = (e) => {
    e.preventDefault();
    if (!nameInput.trim() || !joinCode.trim()) return;
    setPlayerName(nameInput.trim());
    reconnectGame(joinCode.trim(), nameInput.trim());
  };

  const handleStart = () => {
    if (lobbyCode) startGame(lobbyCode);
  };

  // Waiting in lobby after creating/joining
  if (lobbyCode && !lobbyPlayers) {
    return (
      <div className="lobby-page">
        <div className="lobby-waiting">
          <h2>Lobby Created</h2>
          <p className="lobby-code">Code: <strong>{lobbyCode}</strong></p>
          <p>Share this code with your opponent.</p>
          <p className="waiting-text">Waiting for opponent to join...</p>
          <button className="btn-back" onClick={resetToLobby}>Back</button>
        </div>
        {error && <p className="error-msg">{error}</p>}
      </div>
    );
  }

  // Both players connected, ready to start
  if (lobbyCode && lobbyPlayers) {
    return (
      <div className="lobby-page">
        <div className="lobby-ready">
          <h2>Ready to Play</h2>
          <p className="lobby-code">Lobby: <strong>{lobbyCode}</strong></p>
          <div className="player-list">
            {lobbyPlayers.map((name, i) => (
              <p key={i} className="player-name">{name}</p>
            ))}
          </div>
          <button className="btn-start" onClick={handleStart}>Start Game</button>
        </div>
        {error && <p className="error-msg">{error}</p>}
      </div>
    );
  }

  // Initial lobby screen - pick create/join/reconnect
  return (
    <div className="lobby-page">
      <h1>Card Game</h1>

      {!mode && (
        <div className="lobby-menu">
          <button onClick={() => setMode('create')}>Create Game</button>
          <button onClick={() => setMode('join')}>Join Game</button>
          <button onClick={() => setMode('reconnect')}>Reconnect</button>
        </div>
      )}

      {mode === 'create' && (
        <form className="lobby-form" onSubmit={handleCreate}>
          <h2>Create Game</h2>
          <input
            type="text"
            placeholder="Your Name"
            value={nameInput}
            onChange={(e) => setNameInput(e.target.value)}
            autoFocus
          />
          <button type="submit">Create</button>
          <button type="button" className="btn-back" onClick={() => setMode(null)}>Back</button>
        </form>
      )}

      {mode === 'join' && (
        <form className="lobby-form" onSubmit={handleJoin}>
          <h2>Join Game</h2>
          <input
            type="text"
            placeholder="Your Name"
            value={nameInput}
            onChange={(e) => setNameInput(e.target.value)}
            autoFocus
          />
          <input
            type="text"
            placeholder="Lobby Code"
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
            maxLength={6}
          />
          <button type="submit">Join</button>
          <button type="button" className="btn-back" onClick={() => setMode(null)}>Back</button>
        </form>
      )}

      {mode === 'reconnect' && (
        <form className="lobby-form" onSubmit={handleReconnect}>
          <h2>Reconnect to Game</h2>
          <input
            type="text"
            placeholder="Your Name"
            value={nameInput}
            onChange={(e) => setNameInput(e.target.value)}
            autoFocus
          />
          <input
            type="text"
            placeholder="Lobby Code"
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
            maxLength={6}
          />
          <button type="submit">Reconnect</button>
          <button type="button" className="btn-back" onClick={() => setMode(null)}>Back</button>
        </form>
      )}

      {error && <p className="error-msg">{error}</p>}
    </div>
  );
}
