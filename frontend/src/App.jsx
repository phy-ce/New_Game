import { GameProvider, useGame } from './context/GameContext';
import { SocketProvider } from './hooks/useSocket';
import LobbyPage from './pages/LobbyPage';
import GamePage from './pages/GamePage';

function AppContent() {
  const { gameState } = useGame();

  if (gameState) {
    return <GamePage />;
  }

  return <LobbyPage />;
}

function App() {
  return (
    <GameProvider>
      <SocketProvider>
        <AppContent />
      </SocketProvider>
    </GameProvider>
  );
}

export default App;
