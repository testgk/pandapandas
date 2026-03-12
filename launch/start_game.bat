@echo off
setlocal EnableDelayedExpansion
set "REPO=https://github.com/testgk/pandapandas.git"
set "DEST=%~dp0game"

REM ── Clone if not already present ─────────────────────────────
if not exist "%DEST%\p3d" (
    echo Downloading game files...
    git clone --depth 1 --progress %REPO% "%DEST%"
    if errorlevel 1 ( echo ERROR: Download failed. & pause & exit /b 1 )
)

REM ── Create and activate venv ──────────────────────────────────
if not exist "%DEST%\venv" (
    echo Creating virtual environment...
    python -m venv "%DEST%\venv"
)
call "%DEST%\venv\Scripts\activate.bat"

REM ── Install deps ─────────────────────────────────────────────
echo Checking dependencies...
pip install panda3d geopandas numpy shapely matplotlib --quiet

REM ── Launch ───────────────────────────────────────────────────
echo Launching GeoChallenge 3D Globe...
cd /d "%DEST%\p3d"
python globe_launcher.py
