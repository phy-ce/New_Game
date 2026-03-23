# New Game

2-player Dominion-inspired web card game.

## Dev (two terminals)

```bash
# Terminal 1 — backend
cd backend
uv run python run.py

# Terminal 2 — frontend
cd frontend
npm run dev
```

Open http://localhost:5173

## Production

```bash
cd frontend && npm run build
cd backend && uv run python run.py
```

Open http://localhost:5000

## Tests

```bash
cd backend
uv run pytest tests/ -v
```
