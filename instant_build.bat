@echo off
setlocal enabledelayedexpansion
echo 🚀 Instant GeoChallenge Builder
echo.

REM Check timestamps for incremental build
set need_build=0
if not exist GeoChallenge.exe set need_build=1

if %need_build%==0 (
    REM Check if source is newer than exe
    for %%f in (p3d\*.py) do (
        if "%%~tf" gtr "GeoChallenge.exe" set need_build=1
    )
)

if %need_build%==0 (
    echo ⚡ Exe is up-to-date: GeoChallenge.exe
    echo 🎮 Starting game...
    start GeoChallenge.exe
    exit /b 0
)

echo 📦 Source changed - rebuilding...

REM Fastest possible build
python -c "import PyInstaller" 2>nul || pip install pyinstaller --quiet --no-cache-dir

cd p3d
pyinstaller --onefile --noconsole --optimize=2 --strip --noconfirm --distpath=.. --workpath=../temp --specpath=../temp --name="GeoChallenge" globe_launcher.py 2>nul

if exist ..\GeoChallenge.exe (
    echo ✅ Lightning build complete!
    cd ..
    echo 🎮 Auto-starting...
    start GeoChallenge.exe
) else (
    echo ❌ Build error
    pause
)
