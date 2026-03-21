@echo off
REM Launch desktop app with LOCAL database
REM Connects to PostgreSQL running on localhost (docker-compose)

echo ================================
echo GeoChallenge Desktop App (LOCAL)
echo ================================
echo.

REM Set environment variables for local database
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=geochallenge_db
set DB_USER=geochallenge
set DB_PASSWORD=geochallenge_secret

echo Database Configuration:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   Database: %DB_NAME%
echo.

echo Starting desktop app...
echo.

REM Launch the app
cd p3d
python globe_launcher.py %*