import { useEffect, useRef, useCallback, createContext, useContext } from 'react';
import { io } from 'socket.io-client';
import { useGame } from '../context/GameContext';

const SocketContext = createContext(null);

export function SocketProvider({ children }) {
  const socketRef = useRef(null);
  const {
    setGameState, setLobbyCode, setError, setLobbyPlayers,
  } = useGame();

  useEffect(() => {
    const socket = io('/', { transports: ['websocket', 'polling'] });
    socketRef.current = socket;

    socket.on('game_created', (data) => {
      setLobbyCode(data.lobby_code);
      setError(null);
    });

    socket.on('game_joined', (data) => {
      setLobbyCode(data.lobby_code);
      setError(null);
    });

    socket.on('lobby_ready', (data) => {
      setLobbyPlayers(data.players);
    });

    let gotDirectState = false;

    socket.on('game_state', (state) => {
      gotDirectState = true;
      setGameState(state);
      setError(null);
    });

    // Fallback: if we get a room-level notification but didn't receive
    // our per-SID game_state (stale SID), re-request it via reconnect
    socket.on('state_updated', (data) => {
      if (gotDirectState) {
        gotDirectState = false;
        return;
      }
      const savedName = localStorage.getItem('playerName');
      if (data.lobby_code && savedName) {
        socket.emit('reconnect_game', {
          lobby_code: data.lobby_code,
          player_name: savedName,
        });
      }
    });

    socket.on('error', (data) => {
      setError(data.message);
      // If reconnect failed (e.g. server restarted), clear stale session
      if (data.message === 'Game not found' || data.message === 'Player not found in this game') {
        localStorage.removeItem('lobbyCode');
        localStorage.removeItem('playerName');
        setLobbyCode(null);
      }
    });

    // Auto-reconnect if localStorage has saved session
    socket.on('connect', () => {
      const savedCode = localStorage.getItem('lobbyCode');
      const savedName = localStorage.getItem('playerName');
      if (savedCode && savedName) {
        socket.emit('reconnect_game', {
          lobby_code: savedCode,
          player_name: savedName,
        });
      }
    });

    return () => socket.disconnect();
  }, [setGameState, setLobbyCode, setError, setLobbyPlayers]);

  const createGame = useCallback((playerName) => {
    socketRef.current?.emit('create_game', { player_name: playerName });
  }, []);

  const joinGame = useCallback((lobbyCode, playerName) => {
    socketRef.current?.emit('join_game', {
      lobby_code: lobbyCode,
      player_name: playerName,
    });
  }, []);

  const reconnectGame = useCallback((lobbyCode, playerName) => {
    socketRef.current?.emit('reconnect_game', {
      lobby_code: lobbyCode,
      player_name: playerName,
    });
  }, []);

  const startGame = useCallback((lobbyCode) => {
    socketRef.current?.emit('start_game', { lobby_code: lobbyCode });
  }, []);

  const playCard = useCallback((lobbyCode, cardId, target = null) => {
    const payload = { lobby_code: lobbyCode, card_id: cardId };
    if (target) payload.target = target;
    socketRef.current?.emit('play_card', payload);
  }, []);

  const buyCard = useCallback((lobbyCode, cardName) => {
    socketRef.current?.emit('buy_card', {
      lobby_code: lobbyCode,
      card_name: cardName,
    });
  }, []);

  const resolveChoice = useCallback((lobbyCode, choice) => {
    socketRef.current?.emit('resolve_choice', {
      lobby_code: lobbyCode,
      choice: choice,
    });
  }, []);

  const endTurn = useCallback((lobbyCode) => {
    socketRef.current?.emit('end_turn', { lobby_code: lobbyCode });
  }, []);

  const actions = {
    createGame, joinGame, reconnectGame, startGame,
    playCard, buyCard, resolveChoice, endTurn,
  };

  return (
    <SocketContext.Provider value={actions}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  return useContext(SocketContext);
}
