#!/bin/bash
# GeoChallenge Game Launcher

echo "Checking dependencies..."
pip3 install panda3d geopandas numpy shapely matplotlib --quiet
echo ""
echo "Launching GeoChallenge 3D Globe..."
cd "$(dirname "$0")/../p3d"
python3 globe_launcher.py
