#!/bin/bash
# ============================================================
# WMI Local Server Startup Script
# Starts both the Backend (FastAPI) and Frontend (Vite) servers
# ============================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load nvm
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    \. "$NVM_DIR/nvm.sh"
    nvm use 20
else
    echo "⚠️  nvm not found. Trying system node..."
fi

echo "🚀 Starting WMI servers..."
echo ""

# Run network discovery to find any PC IP changes
python3 "$PROJECT_DIR/discovery.py"
echo ""

# Start backend in background
echo "▶ Starting Backend (FastAPI) on http://localhost:8000 ..."
cd "$PROJECT_DIR"
./.venv/bin/python3 -m backend.app.main &
BACKEND_PID=$!

sleep 2

# Start frontend in foreground
echo "▶ Starting Frontend (Vite) on http://localhost:5173 ..."
cd "$PROJECT_DIR/dashboard"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are running!"
echo "   Backend  → http://localhost:8000"
echo "   Frontend → http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

# Wait and handle Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait
