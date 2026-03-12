@echo off
setlocal enabledelayedexpansion

echo ====================================================
echo 🌍 GeoChallenge Game - Windows Deployment Script
echo ====================================================
echo.
echo This script will:
echo - Clone the GeoChallenge repository
echo - Install Python dependencies
echo - Create executable with PyInstaller
echo - Launch the 3D Interactive Globe Game
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
)

echo ✅ Python and Git detected
echo.

REM Create deployment directory
set DEPLOY_DIR=%cd%\geochallenge-game
set REPO_URL=https://github.com/testgk/pandapandas.git

echo 📁 Creating deployment directory: %DEPLOY_DIR%
if exist "%DEPLOY_DIR%" (
    echo 🔄 Directory exists, updating repository...
    cd /d "%DEPLOY_DIR%"
    git pull origin master
    if errorlevel 1 (
        echo ❌ Failed to update repository
        pause
        exit /b 1
    )
) else (
    echo 📥 Cloning repository...
    git clone "%REPO_URL%" "%DEPLOY_DIR%"
    if errorlevel 1 (
        echo ❌ Failed to clone repository
        pause
        exit /b 1
    )
    cd /d "%DEPLOY_DIR%"
)

echo ✅ Repository ready
echo.

REM Create virtual environment
echo 🐍 Setting up Python virtual environment...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install core dependencies
echo 📦 Installing core dependencies...
pip install pandas numpy shapely matplotlib

REM Install GeoPandas (may require additional setup)
echo 📦 Installing GeoPandas...
pip install geopandas
if errorlevel 1 (
    echo ⚠️  GeoPandas installation failed, trying alternative method...
    pip install --no-deps geopandas
    pip install fiona pyproj rtree
)

REM Install 3D visualization dependencies
echo 📦 Installing 3D visualization dependencies...
pip install panda3d

REM Install web dependencies
echo 📦 Installing web dependencies...
pip install folium

REM Install PyInstaller for executable creation
echo 📦 Installing PyInstaller...
pip install pyinstaller

echo ✅ All dependencies installed
echo.

REM Create PyInstaller executable
echo 🏗️  Creating executable with PyInstaller...
cd p3d

REM Create spec file for better control
echo 📝 Creating PyInstaller spec file...
cat > geochallenge.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['globe_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('world_data', 'world_data'),
        ('gui', 'gui'),
        ('interfaces', 'interfaces'),
        ('settings', 'settings'),
        ('*.py', '.'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'geopandas',
        'shapely',
        'panda3d',
        'direct.showbase.ShowBase',
        'direct.gui.DirectGui',
        'panda3d.core',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GeoChallenge-3D-Globe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
EOF

REM Build executable
echo 🔨 Building executable...
pyinstaller --clean geochallenge.spec
if errorlevel 1 (
    echo ⚠️  PyInstaller build failed, creating simple executable...
    pyinstaller --onefile --name "GeoChallenge-3D-Globe" globe_launcher.py
)

echo ✅ Executable created
echo.

REM Create run script for easy access
cd ..
echo 📝 Creating run scripts...

REM Windows run script
cat > run_geochallenge.bat << 'EOF'
@echo off
echo 🌍 Starting GeoChallenge 3D Globe Game...
echo.

REM Try to run from dist directory first
if exist "p3d\dist\GeoChallenge-3D-Globe.exe" (
    echo 🚀 Running executable version...
    p3d\dist\GeoChallenge-3D-Globe.exe
) else if exist "p3d\dist\globe_launcher\globe_launcher.exe" (
    echo 🚀 Running executable version...
    p3d\dist\globe_launcher\globe_launcher.exe
) else (
    echo 🐍 Running Python version...
    call venv\Scripts\activate.bat
    cd p3d
    python globe_launcher.py
)

echo.
echo Game finished. Press any key to exit...
pause >nul
EOF

REM Make run script executable
attrib +x run_geochallenge.bat

echo ✅ Deployment complete!
echo.
echo 🎮 To run GeoChallenge:
echo    Double-click: run_geochallenge.bat
echo    Or manually: cd "%DEPLOY_DIR%" && run_geochallenge.bat
echo.
echo 🌍 Game Features:
echo    - 135+ cities across 4 difficulty levels
echo    - 3D Interactive Globe with click-to-guess
echo    - Real continent data from GeoPandas
echo    - Professional analytics with Pandas
echo.

REM Ask if user wants to run now
set /p run_now="🚀 Run GeoChallenge now? (y/n): "
if /i "%run_now%"=="y" (
    echo.
    echo 🌍 Starting GeoChallenge 3D Globe Game...
    call run_geochallenge.bat
)

echo.
echo 📁 Installation location: %DEPLOY_DIR%
echo 👋 Thank you for playing GeoChallenge!
pause
