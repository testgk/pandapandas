#!/bin/bash
# Launch desktop app with LOCAL database
# Connects to PostgreSQL running on localhost (docker-compose)

echo "🎮 Launching GeoChallenge Desktop App (LOCAL DATABASE)"
echo "=================================================="

# Set environment variables for local database
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=geochallenge_db
export DB_USER=geochallenge
export DB_PASSWORD=geochallenge_secret

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo ""

# Check if docker is running
if ! docker ps &> /dev/null; then
    echo "⚠️  Warning: Docker is not running"
    echo "   Database features will not work"
    echo ""
fi

# Check if postgres container is running
if docker ps | grep -q geochallenge_postgres; then
    echo "✅ PostgreSQL container is running"
else
    echo "⚠️  PostgreSQL container is NOT running"
    echo ""
    echo "To start the database:"
    echo "  cd geochallenge-backend"
    echo "  docker-compose up -d"
    echo ""
    echo "The app will still work without database (no leaderboard)"
fi

echo ""
echo "Starting desktop app..."
echo ""

# Launch the app
cd "$(dirname "$0")/p3d"
python3 globe_launcher.py "$@"