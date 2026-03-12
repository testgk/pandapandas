@echo off
setlocal EnableDelayedExpansion

echo.
echo  ========================================
echo   GeoChallenge - Install and Build
echo  ========================================
echo.

REM ── Download (clone) ─────────────────────────────────────────
set "DEST=geochallenge"
echo [1/3] Downloading game files into %DEST%\...
echo ----------------------------------------
git clone --depth 1 --progress https://github.com/testgk/pandapandas.git %DEST%
if errorlevel 1 ( echo ERROR: Download failed. & pause & exit /b 1 )
echo ----------------------------------------
echo [1/3] Done.

REM ── Install deps ─────────────────────────────────────────────
echo.
echo [2/3] Installing dependencies...
echo ----------------------------------------
pip install panda3d pandas geopandas pyinstaller --progress-bar on
if errorlevel 1 ( echo ERROR: pip install failed. & pause & exit /b 1 )
echo ----------------------------------------
echo [2/3] Done.

REM ── Build EXE ────────────────────────────────────────────────
echo.
echo [3/3] Building GeoChallenge.exe...
echo ----------------------------------------
cd %DEST%\p3d
pyinstaller --onefile --name GeoChallenge --distpath ..\dist --add-data "world_data;world_data" --add-data "settings;settings" --add-data "gui;gui" --add-data "interfaces;interfaces" globe_launcher.py
if errorlevel 1 ( echo ERROR: Build failed. & cd ..\.. & pause & exit /b 1 )
cd ..\..
echo ----------------------------------------
echo [3/3] Done.

echo.
echo  ========================================
echo   Done! Run: %DEST%\dist\GeoChallenge.exe
echo  ========================================
echo.
pause
