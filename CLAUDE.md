# New Game — Architecture Overview

2-player Dominion-inspired web card game.

## Tech Stack

- **Backend:** Python, Flask + flask-socketio + eventlet
- **Frontend:** Vite + React + socket.io-client
- **Game state:** In-memory Python dict (no database)
- **Communication:** WebSocket — full state broadcast after every action

## Project Structure

```
backend/
  run.py                          # Entry point — runs Flask on port 5000
  pyproject.toml                  # uv-managed dependencies
  app/
    __init__.py                   # App factory, serves frontend SPA (catch-all 404 → index.html)
    models/cards.py               # Card templates, deck/market creation
    services/game_manager.py      # Create/join/reconnect, lobby codes, global games dict
    services/game_logic.py        # start_game, play_card, buy_card, resolve_choice, end_turn
    services/serializer.py        # Per-player state filtering (hides opponent hand/deck)
    sockets/__init__.py           # Handler registration
    sockets/lobby.py              # create_game, join_game, reconnect_game events
    sockets/game.py               # start_game, play_card, buy_card, resolve_choice, end_turn + broadcast_state

frontend/
  vite.config.js                  # Proxies /socket.io → Flask in dev
  src/
    App.jsx                       # GameProvider > SocketProvider > LobbyPage or GamePage
    context/GameContext.jsx        # State: lobbyCode, playerName, gameState, error, lobbyPlayers
    hooks/useSocket.jsx            # SocketProvider + useSocket hook (single connection, all emit wrappers)
    pages/LobbyPage.jsx            # Create/join/reconnect forms, waiting screen, ready screen
    pages/GamePage.jsx             # Game board assembly
    components/Card.jsx            # Card with hover inspector
    components/Hand.jsx            # Horizontal card row (face-up or face-down)
    components/Market.jsx          # Supply piles to buy from
    components/PlayArea.jsx        # Last played card + TurnStats
    components/TurnStats.jsx       # Gold/Actions/Buys counters
    components/PlayerInfo.jsx      # Name, HP bar, deck/discard counts
    components/GameLog.jsx         # Scrollable side panel
    components/ChoiceModal.jsx     # Modal for pending card choices
```

## Running Locally (Dev)

프로젝트 루트에서 `./dev.sh`를 실행하면 백엔드(Flask :5000)와 프론트엔드(Vite :5173)가 동시에 뜬다.

```bash
./dev.sh
```

기존에 실행 중인 백엔드/프론트엔드가 있으면 자동으로 종료 후 재시작한다. 코드 수정 후 다시 `./dev.sh`만 실행하면 된다.

Open `http://localhost:5173`. Vite proxies WebSocket traffic to Flask at `:5000`.

수동으로 띄우려면 터미널 두 개:

```bash
# Terminal 1 — backend
cd backend
uv run python run.py

# Terminal 2 — frontend (hot reload)
cd frontend
npm run dev
```

## Production

Build the frontend, then Flask serves everything:

```bash
cd frontend && npm run build
cd backend && uv run python run.py
```

Open `http://localhost:5000`.

## WebSocket Events

| Direction | Events |
|-----------|--------|
| Client → Server | `create_game`, `join_game`, `reconnect_game`, `start_game`, `play_card`, `buy_card`, `resolve_choice`, `end_turn` |
| Server → Client | `game_created`, `game_joined`, `lobby_ready`, `game_state`, `state_updated`, `error` |

## Key Design Decisions

- **Full state broadcast** — server sends complete filtered state after every action (no diffs)
- **Per-player serialization** — state shape is `{ me, opponent, market, turn_state, log }`. Client never knows player index.
- **Socket rooms** — used for lobby events; direct SID + room fallback for game state broadcast (handles SID mismatch)
- **Auto-reconnect** — via `localStorage` (lobbyCode + playerName)
- **No auth** — players identified by name + lobby code only
- **pending_choice system** — implemented in game logic, not yet used by any cards

## Game Model (Dominion-style)

- **Cards:** played from hand → effect resolves → goes to discard
- **Turn:** auto-draw 5 → play action cards (costs actions) → buy from market (costs gold + buys) → end turn
- **Deck cycle:** deck → hand → play → discard → reshuffle when deck empty
- **Win condition:** opponent reaches 0 HP
- **Card types:** Copper/Silver/Gold (treasure), Village/Smithy/Militia/Market/Witch (action)

## Testing

```bash
cd backend
uv run pytest tests/ -v
```

Tests live in `backend/tests/`. Focus on `game_logic.py` and `serializer.py` — pure functions with no socket dependencies.
