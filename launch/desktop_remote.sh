#!/bin/bash
# Launch desktop app with REMOTE database
# Configured for Render.com PostgreSQL

echo "🎮 Launching GeoChallenge Desktop App (REMOTE DATABASE)"
echo "=================================================="

# Render.com PostgreSQL configuration
export DB_HOST="dpg-d6s6bokhg0os73f15t4g-a.oregon-postgres.render.com"
export DB_PORT="5432"
export DB_NAME="geochallenge_db"
export DB_USER="geochallenge"
export DB_PASSWORD="lbPJgqX2dLkJWQHTn3jYTwxkmjFBRN4H"

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""
echo "✅ Connected to Render.com PostgreSQL"
echo ""

echo "Starting desktop app..."
echo ""

# Launch the app
cd "$(dirname "$0")/p3d"
python3 globe_launcher.py "$@"