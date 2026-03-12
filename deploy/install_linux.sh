#!/bin/bash
# 🌍 GeoChallenge - Quick Linux/macOS Installer
echo "🌍 GeoChallenge Game - Quick Installer"
echo ""

echo "📁 Creating destination folder..."
mkdir -p geopanda3d
cd geopanda3d

echo "📦 Installing dependencies..."
pip3 install pandas geopandas panda3d pyinstaller --quiet

echo "📥 Cloning repository..."
git clone https://github.com/testgk/pandapandas.git geochallenge-game

echo "🔨 Building executable..."
cd geochallenge-game/p3d
pyinstaller --onefile --name GeoChallenge globe_launcher.py

echo "🚀 Starting game..."
./dist/GeoChallenge
