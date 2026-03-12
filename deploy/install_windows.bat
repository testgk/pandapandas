@echo off
REM 🌍 GeoChallenge - One-Line Windows Installer
echo 🌍 GeoChallenge Game - Quick Installer
echo Downloading installer...
wget --show-progress -O install.py https://raw.githubusercontent.com/testgk/pandapandas/master/deploy/install.py
echo Running installer...
python install.py
pause
