@echo off
REM GeoPandas Globe - Windows PyInstaller Build Script

title Building GeoPandas Globe for Windows

echo ========================================
echo 🏗️ GeoPandas Globe PyInstaller Build
echo 🖥️ Windows Standalone Executable
echo ========================================
echo.

echo 🔍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python is available
echo.

echo 📦 Installing PyInstaller if not already installed...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo ❌ Failed to install PyInstaller!
    pause
    exit /b 1
)

echo.
echo 📦 Installing core dependencies first...
pip install -r requirements_pyinstaller.txt

echo.
echo 📦 Installing GeoPandas and spatial dependencies (may take longer)...
echo Note: If this fails, the executable will still work with cached data
pip install geopandas --no-deps
pip install shapely pyproj --force-reinstall

echo 🔧 Using existing spatial libraries if available...
python -c "try: import geopandas; print('✅ GeoPandas available')" except: print('⚠️ GeoPandas not available - will use cached data')"

echo.
echo 🧹 Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo.
echo 🏗️ Building Windows executable...
echo This may take several minutes...
pyinstaller globe_windows.spec

if %errorlevel% neq 0 (
    echo ❌ Build failed!
    echo Check the output above for errors
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo.
echo 📋 Build Results:
if exist "dist\GeoPandas-Globe-Windows.exe" (
    echo ✅ Windows executable created: dist\GeoPandas-Globe-Windows.exe
    dir dist\GeoPandas-Globe-Windows.exe
) else (
    echo ❌ Executable not found in expected location
)

echo.
echo 🚀 Testing the executable...
cd dist
if exist "GeoPandas-Globe-Windows.exe" (
    echo Starting GeoPandas Globe...
    GeoPandas-Globe-Windows.exe
) else (
    echo Executable not found for testing
)

echo.
echo ========================================
echo 🎯 Windows Build Complete!
echo ========================================
echo.
echo 📁 Executable location: dist\GeoPandas-Globe-Windows.exe
echo 💡 You can distribute this file without requiring Python installation
echo.
pause
