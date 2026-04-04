import { createContext, useState, useEffect, useContext } from 'react';

const GameContext = createContext();

export function GameProvider({ children }) {
  const [lobbyCode, setLobbyCode] = useState(
    () => localStorage.getItem('lobbyCode') || null
  );
  const [playerName, setPlayerName] = useState(
    () => localStorage.getItem('playerName') || ''
  );
  const [gameState, setGameState] = useState(null);
  const [error, setError] = useState(null);
  const [lobbyPlayers, setLobbyPlayers] = useState(null);
  const [cardTemplates, setCardTemplates] = useState({});
  const [unitTemplates, setUnitTemplates] = useState({});
  const [passiveInfo, setPassiveInfo] = useState({});
  const [relicTemplates, setRelicTemplates] = useState({});

  useEffect(() => {
    fetch('/api/card-templates').then(r => r.json()).then(setCardTemplates);
    fetch('/api/unit-templates').then(r => r.json()).then(setUnitTemplates);
    fetch('/api/passive-info').then(r => r.json()).then(setPassiveInfo);
    fetch('/api/relic-templates').then(r => r.json()).then(setRelicTemplates);
  }, []);

  // Persist to localStorage so refresh can reconnect
  useEffect(() => {
    if (lobbyCode) {
      localStorage.setItem('lobbyCode', lobbyCode);
    } else {
      localStorage.removeItem('lobbyCode');
    }
  }, [lobbyCode]);

  useEffect(() => {
    if (playerName) {
      localStorage.setItem('playerName', playerName);
    } else {
      localStorage.removeItem('playerName');
    }
  }, [playerName]);

  // Auto-clear errors after 4 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const resetToLobby = () => {
    setGameState(null);
    setLobbyCode(null);
    setLobbyPlayers(null);
    setPlayerName('');
    setError(null);
  };

  const value = {
    lobbyCode, setLobbyCode,
    playerName, setPlayerName,
    gameState, setGameState,
    error, setError,
    lobbyPlayers, setLobbyPlayers,
    cardTemplates,
    unitTemplates,
    passiveInfo,
    relicTemplates,
    resetToLobby,
  };

  return (
    <GameContext.Provider value={value}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  return useContext(GameContext);
}
