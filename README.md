# New Game — Online 2-Player Card Battler

**English** · [日本語](README.ja.md) · [한국어](README.ko.md)

A real-time, two-player web card game inspired by [Dominion](https://en.wikipedia.org/wiki/Dominion_(card_game)).
Two players join the same lobby in their browsers and battle in real time: build a deck,
spend energy to play cards, buy from shared markets, summon units, and reduce your
opponent's HP to zero.

> ⚠️ **Status:** A two-person hobby project, developed in 2026 and paused in April 2026.
> It is a working prototype, **not** a production-hardened service (no authentication,
> in-memory state only).

---

## ✨ Features

- **Real-time 1v1 battles** over WebSocket — every action is broadcast to both players instantly.
- **Deck-building gameplay** — start with a small deck and buy new cards each turn.
- **Tactical combat layer** — energy costs, block, strength, and damage-over-time
  status effects (*burn, plate armour, thorn, growth, arson*).
- **Field units & champions** — persistent units that attack every turn; some absorb damage.
- **Three supply sources** — a base market, a rotating **rare** market, and a **relic** market
  for passive upgrades.
- **Lobby system** — create a game to get a 6-character code, share it, and your opponent joins.
- **Auto-reconnect** — refresh or drop your connection and rejoin the same game (name + code,
  persisted in `localStorage`).
- **Per-player state** — the server only sends each player what they're allowed to see
  (your hand is hidden from your opponent).

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12+, [Flask](https://flask.palletsprojects.com/) 3.1, [Flask-SocketIO](https://flask-socketio.readthedocs.io/) 5.6, [eventlet](https://eventlet.readthedocs.io/) |
| **Frontend** | JavaScript, [React](https://react.dev/) 19, [Vite](https://vite.dev/) 8, [socket.io-client](https://socket.io/) 4.8 |
| **Transport** | WebSocket (real-time, bidirectional) |
| **State** | In-memory Python dict (no database) |
| **Tooling** | [uv](https://docs.astral.sh/uv/) (Python deps), npm (frontend) |

---

## 🏗️ Architecture

The server keeps the full game state in memory and **broadcasts the complete (per-player
filtered) state after every action** — there are no diffs. The React client renders whatever
the latest state says. This keeps the client thin and the server authoritative.

```
┌───────────┐   WebSocket    ┌──────────────────┐
│ Browser A │ ◀────────────▶ │  Flask +         │
└───────────┘   game_state   │  Flask-SocketIO  │   in-memory
┌───────────┐   broadcast    │  (eventlet)      │   games = { CODE: {...} }
│ Browser B │ ◀────────────▶ │                  │
└───────────┘                └──────────────────┘
```

### Project structure

```
backend/
  run.py                       # Entry point — socketio.run on port 5000
  pyproject.toml               # uv-managed dependencies
  app/
    __init__.py                # App factory; serves built SPA; REST endpoints for templates
    models/
      cards.py                 # Card templates, starter deck & market creation
      units.py                 # Field unit templates
      relics.py                # Relic templates & relic market
    services/
      game_manager.py          # Lobbies: create/join/reconnect, in-memory games dict
      game_logic.py            # start_game, play_card, buy_card/rare/relic, resolve_choice, end_turn
      effects.py               # Card/relic effects, damage & status-effect resolution
      serializer.py            # Per-player state filtering (hides opponent hand/deck)
    sockets/
      __init__.py              # Handler registration
      lobby.py                 # create_game, join_game, reconnect_game
      game.py                  # gameplay events + broadcast_state
      debug.py                 # debug-only events

frontend/
  vite.config.js               # Dev proxy: /socket.io (ws) and /api → Flask :5000
  index.html
  src/
    main.jsx, App.jsx
    context/GameContext.jsx    # Lobby code, player name, game state, errors
    hooks/useSocket.jsx        # Single socket connection + all emit wrappers
    pages/
      LobbyPage.jsx            # Create / join / reconnect / waiting screens
      GamePage.jsx             # Game board assembly
    components/                # Card, Hand, Market, Field, UnitCard, PlayArea,
                               # TurnStats, PlayerInfo, DeckPile, DiscardPile,
                               # GameLog, ChoiceModal, FloatingDamage, ...
    styles/                    # Per-component CSS

dev.sh                         # Convenience script: start backend + frontend together
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** and [**uv**](https://docs.astral.sh/uv/getting-started/installation/)
- **Node.js** (with npm)

### Option A — one command (recommended)

From the project root:

```bash
./dev.sh
```

This starts the backend (Flask on `:5000`) and the frontend (Vite on `:5173`) together,
killing any previous instances first. Re-run it after code changes.

> `dev.sh` is a Bash script — run it from Linux, macOS, WSL, or Git Bash.

### Option B — two terminals (manual)

```bash
# Terminal 1 — backend
cd backend
uv run python run.py

# Terminal 2 — frontend (hot reload)
cd frontend
npm install      # first time only
npm run dev
```

Open **http://localhost:5173**. Vite proxies WebSocket and `/api` traffic to Flask at `:5000`.

### Production

Build the frontend, then let Flask serve everything from one port:

```bash
cd frontend && npm run build      # outputs frontend/dist
cd ../backend && uv run python run.py
```

Open **http://localhost:5000**. Flask serves the built SPA and the WebSocket from the same origin.

> Configurable via environment variables: `PORT` (default `5000`) and `FLASK_DEBUG` (`true`/`false`).

---

## 🎮 How to Play

1. **Player 1** opens the app and creates a game → receives a **6-character lobby code**.
2. **Player 2** enters that code and the same screen to join.
3. Either player starts the game once both are present.
4. On your turn: gain energy, draw a hand, **play cards** (spend energy), **buy** from the
   markets (spend gold), then **end your turn**.
5. First to bring the opponent's HP to **0** wins.

### Game mechanics (at a glance)

- **HP & win condition** — each player starts at 80 HP; reduce your opponent to 0 to win.
- **Energy** — refreshes each turn; most action cards cost energy to play.
- **Gold & buys** — treasure cards (Copper / Silver / Gold) generate gold to buy new cards and relics.
- **Status effects** — block, strength, burn, plate armour, thorn, growth, arson.
- **Field units & champions** — persistent units that attack each turn; some absorb incoming damage.
- **Markets** — base market, rare market, and relic (passive upgrade) market.
- **Deck cycle** — deck → hand → play → discard, reshuffled when the deck runs out.

---

## 🔌 WebSocket API

| Direction | Events |
|-----------|--------|
| Client → Server | `create_game`, `join_game`, `reconnect_game`, `start_game`, `play_card`, `buy_card`, `buy_rare_card`, `buy_relic`, `resolve_choice`, `end_turn` |
| Server → Client | `game_created`, `game_joined`, `lobby_ready`, `game_state`, `state_updated`, `error` |

The server also exposes a few read-only REST endpoints used by the client to load card art and
metadata: `/api/card-templates`, `/api/unit-templates`, `/api/relic-templates`, `/api/passive-info`.

---

## 👥 Authors & Notes

- Built by **[@phy-ce](https://github.com/phy-ce)** and **[@jather](https://github.com/jather)**.
- Developed with the help of **[Claude Code](https://claude.com/claude-code)** — repository
  conventions live in [`CLAUDE.md`](CLAUDE.md).
- Made public on **2026-06-22**.

---

**English** · [日本語](README.ja.md) · [한국어](README.ko.md)
