@echo off
setlocal EnableDelayedExpansion
echo ⚡ Super Fast GeoChallenge Builder
echo.

REM Store starting directory
set "START_DIR=%CD%"

REM Check if exe already exists and is recent
if exist GeoChallenge.exe (
    echo 📁 Found existing GeoChallenge.exe
    set /p rebuild="🔄 Rebuild anyway? (y/N): "
    if /i not "!rebuild!"=="y" (
        echo 🚀 Using existing exe: GeoChallenge.exe
        goto :run_exe
    )
)

REM Ultra-fast conditional install
python -c "import PyInstaller" 2>nul || pip install pyinstaller --quiet

REM Fast build with maximum optimization
cd p3d
echo ⚡ Lightning-fast build...
pyinstaller --onefile --noconsole --optimize=2 --strip --clean --distpath=.. --name="GeoChallenge" globe_launcher.py >nul 2>&1

cd "%START_DIR%"

if exist GeoChallenge.exe (
    echo ✅ Built in seconds: GeoChallenge.exe
) else (
    echo ❌ Build failed
    exit /b 1
)

:run_exe
cd "%START_DIR%"
echo 🎮 Starting game...
start "" "GeoChallenge.exe"
