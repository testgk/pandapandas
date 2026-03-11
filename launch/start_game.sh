#!/bin/bash
# GeoChallenge Game Launcher

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Virtual environment not found. Run a build script first."
    exit 1
fi

echo "🌍 GeoChallenge Game Launcher"
echo "================================"
echo ""
echo "Choose your game mode:"
echo "1. 3D Interactive Globe (Recommended)"
echo "2. Text-based with coordinates"
echo "3. Web-based with clickable map"
echo ""
read -p "Enter your choice (1-3): " choice

case "$choice" in
    1)
        echo "🚀 Starting 3D Globe Game..."
        cd "$PROJECT_ROOT/p3d"
        "$VENV_PYTHON" globe_launcher.py
        ;;
    2)
        echo "📝 Starting text-based game..."
        cd "$PROJECT_ROOT"
        "$VENV_PYTHON" -c "import sys; sys.path.insert(0, 'p3d'); exec(open('p3d/geo_challenge_game.py').read())"
        ;;
    3)
        echo "🌐 Starting web-based game..."
        cd "$PROJECT_ROOT/p3d"
        "$VENV_PYTHON" demo_geochallenge.py
        ;;
    *)
        echo "Invalid choice. Starting 3D Globe Game by default..."
        cd "$PROJECT_ROOT/p3d"
        "$VENV_PYTHON" globe_launcher.py
        ;;
esac

