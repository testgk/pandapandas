@echo off
echo 🌍 GeoChallenge Game Launcher
echo ================================
echo.
echo Choose your game mode:
echo 1. 3D Interactive Globe (Recommended)
echo 2. Text-based with coordinates
echo 3. Web-based with clickable map
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo 🚀 Starting 3D Globe Game...
    cd /d "D:\geopandas\p3d"
    python globe_launcher.py
) else if "%choice%"=="2" (
    echo 📝 Starting text-based game...
    cd /d "D:\geopandas"
    python run_geo_challenge.py
) else if "%choice%"=="3" (
    echo 🌐 Starting web-based game...
    cd /d "D:\geopandas"
    python run_web_game.py
) else (
    echo Invalid choice. Starting 3D Globe Game by default...
    cd /d "D:\geopandas\p3d"
    python globe_launcher.py
)

pause
