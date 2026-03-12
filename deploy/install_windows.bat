@echo off
REM 🌍 GeoChallenge - Quick Windows Installer
echo 🌍 GeoChallenge Game - Quick Installer
echo.

echo 📁 Creating destination folder...
mkdir geopanda3d
cd geopanda3d

echo 📦 Installing dependencies...
pip install pandas geopandas panda3d pyinstaller --quiet

echo 📥 Cloning repository...
git clone https://github.com/testgk/pandapandas.git geochallenge-game

echo 🔨 Building executable...
cd geochallenge-game\p3d
pyinstaller --onefile --noconsole --name GeoChallenge globe_launcher.py

echo 🚀 Starting game...
cd ..\dist
start GeoChallenge.exe
pause
