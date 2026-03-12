@echo off
echo Checking dependencies...
pip install panda3d geopandas numpy shapely matplotlib --quiet
echo.
echo Launching GeoChallenge 3D Globe...
cd /d "%~dp0..\p3d"
python globe_launcher.py
