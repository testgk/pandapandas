#!/usr/bin/env bash
# start_all.sh — Start everything: database, API, and game
#
# Usage: ./start_all.sh [OPTIONS]
#   -p, --panda3d    Launch Panda3D Desktop App
#   -w, --web        Launch Web App (browser)
#   -h, --help       Show this help message
#
# Without options, shows interactive menu.

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
FRONTEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Default values
FRONTEND=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--panda3d)
            FRONTEND="panda3d"
            shift
            ;;
        -w|--web)
            FRONTEND="web"
            shift
            ;;
        -h|--help)
            echo "Usage: ./start_all.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -p, --panda3d    Launch Panda3D Desktop App"
            echo "  -w, --web        Launch Web App (browser)"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Without options, shows interactive menu."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage."
            exit 1
            ;;
    esac
done

echo "🌍 GeoChallenge Full Stack Launcher"
echo "===================================="

# Show frontend menu if not specified via command line
if [ -z "$FRONTEND" ]; then
    echo ""
    echo "Select frontend:"
    echo "  1) Panda3D Desktop App"
    echo "  2) Web App (browser)"
    echo ""
    read -p "Enter choice [1-2]: " choice

    case $choice in
        1) FRONTEND="panda3d" ;;
        2) FRONTEND="web" ;;
        *) echo "Invalid choice. Defaulting to Panda3D."; FRONTEND="panda3d" ;;
    esac
fi

# Start database
echo ""
echo "📦 Starting database..."
cd "$PROJECT_ROOT/geochallenge-backend"
./start_db.sh

# Wait for database
echo "⏳ Waiting for database..."
sleep 3

# Activate virtual environment
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Install backend dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Start API in background
echo "🚀 Starting API server in background..."
# Kill any existing process on port 8000
lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "   API running at http://localhost:8000 (PID: $API_PID)"
sleep 2

# Start selected frontend
echo ""
if [ "$FRONTEND" = "web" ]; then
    echo "🌐 Starting Web App..."
    WEB_DIR="$FRONTEND_DIR/web"
    echo "   Opening browser at http://localhost:8081"
    
    # Kill any existing process on port 8081
    lsof -ti:8081 | xargs -r kill -9 2>/dev/null || true
    
    # Start simple HTTP server for web frontend
    cd "$WEB_DIR"
    python -m http.server 8081 &
    WEB_PID=$!
    
    # Open browser
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:8081" 2>/dev/null
    elif command -v open &> /dev/null; then
        open "http://localhost:8081"
    fi
    
    echo ""
    echo "Press Enter to stop servers..."
    read
    
    # Stop web server
    kill $WEB_PID 2>/dev/null || true
else
    echo "🎮 Starting Panda3D App..."
    cd "$FRONTEND_DIR/launch"
    ./start_game.sh
fi

# Stop API server
echo ""
echo "🛑 Stopping API server..."
kill $API_PID 2>/dev/null || true
echo "Done!"
