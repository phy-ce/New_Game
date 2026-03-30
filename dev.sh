#!/bin/bash
# Start both backend and frontend in one command
# Usage: ./dev.sh

# Kill previous instances
pkill -f "uv run python run.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 0.5

trap 'kill 0' EXIT

(cd backend && uv run python run.py) &
(cd frontend && npm run dev) &

wait
