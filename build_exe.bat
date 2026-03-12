@echo off
echo 🚀 Fast GeoChallenge.exe Builder
echo.

REM Check if PyInstaller is already installed (faster)
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 📦 Installing PyInstaller...
    pip install pyinstaller
) else (
    echo ✅ PyInstaller already installed
)

REM Go to game directory
cd p3d

REM Fast build with optimizations
echo ⚡ Creating optimized executable...
pyinstaller ^
    --onefile ^
    --noconsole ^
    --optimize=2 ^
    --strip ^
    --noupx ^
    --clean ^
    --distpath=../dist ^
    --workpath=../build ^
    --specpath=../build ^
    --name="GeoChallenge" ^
    globe_launcher.py

REM Move exe to root (faster path)
if exist ..\dist\GeoChallenge.exe (
    move ..\dist\GeoChallenge.exe ..\GeoChallenge.exe
    echo ✅ Built GeoChallenge.exe
    echo 🎮 Ready to run: GeoChallenge.exe
) else (
    echo ❌ Build failed - check for errors above
)
