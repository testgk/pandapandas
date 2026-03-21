@echo off
REM Launch desktop app with REMOTE database
REM Configured for Render.com PostgreSQL

echo =================================
echo GeoChallenge Desktop App (REMOTE)
echo =================================
echo.

REM Render.com PostgreSQL configuration
set DB_HOST=dpg-d6s6bokhg0os73f15t4g-a.oregon-postgres.render.com
set DB_PORT=5432
set DB_NAME=geochallenge_db
set DB_USER=geochallenge
set DB_PASSWORD=lbPJgqX2dLkJWQHTn3jYTwxkmjFBRN4H

echo Database Configuration:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   Database: %DB_NAME%
echo   User: %DB_USER%
echo.
echo Connected to Render.com PostgreSQL
echo.

echo Starting desktop app...
echo.

REM Launch the app
cd p3d
python globe_launcher.py %*