@echo off
REM 🌍 GeoChallenge - One-Line Windows Installer
echo 🌍 GeoChallenge Game - Quick Installer
echo Downloading and running installer...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/testgk/pandapandas/master/deploy/install.py' -OutFile 'install.py'; python install.py"
pause
