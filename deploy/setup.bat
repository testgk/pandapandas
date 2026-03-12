@echo off
setlocal EnableDelayedExpansion
title 🌍 GeoChallenge Setup
echo.
echo  ==========================================
echo   🌍 GeoChallenge Game - Full Setup
echo  ==========================================
echo.

REM ── 1. Create destination folder ──────────────────────────────
echo 📁 Creating folder geopanda3d...
if exist geopanda3d (
    echo    Folder already exists, using it.
) else (
    mkdir geopanda3d
)
cd geopanda3d

REM ── 2. Check requirements ─────────────────────────────────────
echo.
echo 🔍 Checking requirements...

where git >nul 2>&1
if errorlevel 1 (
    echo ❌ Git not found. Please install git from https://git-scm.com
    pause & exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python from https://python.org
    pause & exit /b 1
)

REM ── 3. Install dependencies ───────────────────────────────────
echo.
echo 📦 Installing dependencies...
pip install pandas geopandas panda3d pyinstaller --quiet
if errorlevel 1 (
    echo ❌ pip install failed.
    pause & exit /b 1
)
echo    ✅ Dependencies installed.

REM ── 4. Clone repository ───────────────────────────────────────
echo.
echo 📥 Downloading game source...
if exist geochallenge-game (
    echo    Repo already cloned, pulling latest...
    cd geochallenge-game
    git pull --quiet
    cd ..
) else (
    git clone --quiet https://github.com/testgk/pandapandas.git geochallenge-game
)
if errorlevel 1 (
    echo ❌ Git clone failed.
    pause & exit /b 1
)
echo    ✅ Source downloaded.

REM ── 5. Build executable ───────────────────────────────────────
echo.
echo 🔨 Building GeoChallenge.exe...
cd geochallenge-game\p3d
pyinstaller --onefile --noconsole --name GeoChallenge globe_launcher.py --distpath ..\..\dist >nul 2>&1
if errorlevel 1 (
    echo ❌ Build failed.
    cd ..\..
    pause & exit /b 1
)
cd ..\..
echo    ✅ Build complete.

REM ── 6. Launch game ────────────────────────────────────────────
echo.
echo 🚀 Launching GeoChallenge...
if exist dist\GeoChallenge.exe (
    start "" "dist\GeoChallenge.exe"
    echo    ✅ Game launched!
) else (
    echo ❌ GeoChallenge.exe not found in dist\
    pause & exit /b 1
)

echo.
echo  ==========================================
echo   ✅ Setup complete! Enjoy the game 🌍
echo  ==========================================
echo.
pause

