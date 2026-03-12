#!/bin/bash

# GeoChallenge Game - Linux Deployment Script
# This script handles cloning, dependency installation, PyInstaller packaging, and running

set -e  # Exit on any error

echo "===================================================="
echo "🌍 GeoChallenge Game - Linux Deployment Script"
echo "===================================================="
echo ""
echo "This script will:"
echo "- Clone the GeoChallenge repository"
echo "- Install Python dependencies"
echo "- Create executable with PyInstaller"
echo "- Launch the 3D Interactive Globe Game"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    echo "  macOS:         brew install python3"
    exit 1
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ ERROR: Git is not installed"
    echo "Please install Git using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install git"
    echo "  CentOS/RHEL:   sudo yum install git"
    echo "  Arch:          sudo pacman -S git"
    echo "  macOS:         brew install git"
    exit 1
fi

echo "✅ Python 3 and Git detected"
echo ""

# Set up variables
DEPLOY_DIR="$(pwd)/geochallenge-game"
REPO_URL="https://github.com/testgk/pandapandas.git"

echo "📁 Creating deployment directory: $DEPLOY_DIR"

# Clone or update repository
if [ -d "$DEPLOY_DIR" ]; then
    echo "🔄 Directory exists, updating repository..."
    cd "$DEPLOY_DIR"
    git pull origin master
else
    echo "📥 Cloning repository..."
    git clone "$REPO_URL" "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

echo "✅ Repository ready"
echo ""

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install system dependencies (Ubuntu/Debian)
echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    echo "🐧 Detected Debian/Ubuntu system"
    echo "Installing GDAL and other geospatial libraries..."

    # Check if we can run sudo commands
    if sudo -n true 2>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            python3-dev \
            libgdal-dev \
            libproj-dev \
            libgeos-dev \
            libspatialindex-dev \
            build-essential \
            pkg-config \
            libfreetype6-dev \
            libpng-dev \
            libjpeg-dev \
            libgl1-mesa-dev \
            libglu1-mesa-dev \
            freeglut3-dev
    else
        echo "⚠️  Cannot install system packages (no sudo access)"
        echo "You may need to install these packages manually:"
        echo "  sudo apt-get install python3-dev libgdal-dev libproj-dev libgeos-dev libspatialindex-dev"
    fi
elif command -v yum &> /dev/null; then
    echo "🐧 Detected RedHat/CentOS system"
    if sudo -n true 2>/dev/null; then
        sudo yum install -y \
            python3-devel \
            gdal-devel \
            proj-devel \
            geos-devel \
            spatialindex-devel \
            gcc-c++ \
            pkgconfig \
            freetype-devel \
            libpng-devel \
            libjpeg-devel \
            mesa-libGL-devel \
            mesa-libGLU-devel \
            freeglut-devel
    fi
elif command -v pacman &> /dev/null; then
    echo "🐧 Detected Arch Linux system"
    if sudo -n true 2>/dev/null; then
        sudo pacman -S --needed --noconfirm \
            base-devel \
            gdal \
            proj \
            geos \
            spatialindex \
            freetype2 \
            libpng \
            libjpeg-turbo \
            mesa \
            freeglut
    fi
fi

# Install core Python dependencies
echo "📦 Installing core dependencies..."
pip install wheel setuptools

# Install numerical and data science packages
echo "📦 Installing pandas and numpy..."
pip install pandas numpy

# Install geospatial dependencies
echo "📦 Installing geospatial packages..."
pip install shapely pyproj

# Try to install GeoPandas with multiple methods
echo "📦 Installing GeoPandas..."
if ! pip install geopandas; then
    echo "⚠️  Direct GeoPandas installation failed, trying alternative methods..."

    # Method 1: Install from conda-forge if available
    if command -v conda &> /dev/null; then
        echo "🐍 Trying conda installation..."
        conda install -c conda-forge geopandas -y || true
    fi

    # Method 2: Install individual components
    echo "🔧 Installing individual components..."
    pip install fiona rtree || true
    pip install --no-deps geopandas || true
fi

# Install visualization dependencies
echo "📦 Installing visualization packages..."
pip install matplotlib

# Install 3D engine
echo "📦 Installing Panda3D..."
pip install panda3d

# Install web dependencies
echo "📦 Installing web packages..."
pip install folium

# Install PyInstaller
echo "📦 Installing PyInstaller..."
pip install pyinstaller

echo "✅ All dependencies installed"
echo ""

# Create PyInstaller executable
echo "🏗️  Creating executable with PyInstaller..."
cd p3d

# Create spec file for better executable control
echo "📝 Creating PyInstaller spec file..."
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
)
EOF

# Build executable
echo "🔨 Building executable..."
if ! pyinstaller --clean geochallenge.spec; then
    echo "⚠️  PyInstaller build failed, creating simple executable..."
    pyinstaller --onefile --name "GeoChallenge-3D-Globe" globe_launcher.py || true
fi

echo "✅ Executable created"
echo ""

# Create run scripts
cd ..
echo "📝 Creating run scripts..."

# Linux run script
cat > run_geochallenge.sh << 'EOF'
#!/bin/bash

echo "🌍 Starting GeoChallenge 3D Globe Game..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Try to run executable first, fall back to Python
if [ -f "p3d/dist/GeoChallenge-3D-Globe" ]; then
    echo "🚀 Running executable version..."
    ./p3d/dist/GeoChallenge-3D-Globe
elif [ -f "p3d/dist/globe_launcher/globe_launcher" ]; then
    echo "🚀 Running executable version..."
    ./p3d/dist/globe_launcher/globe_launcher
else
    echo "🐍 Running Python version..."
    source venv/bin/activate
    cd p3d
    python3 globe_launcher.py
fi

echo ""
echo "Game finished. Press Enter to exit..."
read
EOF

# Make run script executable
chmod +x run_geochallenge.sh

# Create desktop entry (Linux)
if command -v desktop-file-install &> /dev/null || [ -d "$HOME/.local/share/applications" ]; then
    echo "📝 Creating desktop entry..."

    DESKTOP_FILE="$HOME/.local/share/applications/geochallenge.desktop"
    mkdir -p "$(dirname "$DESKTOP_FILE")"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=GeoChallenge 3D Globe
Comment=Interactive geography game with 3D globe
Exec=$DEPLOY_DIR/run_geochallenge.sh
Icon=applications-games
Terminal=true
Categories=Game;Education;Geography;
StartupNotify=true
EOF

    # Make desktop file executable
    chmod +x "$DESKTOP_FILE"

    echo "✅ Desktop entry created: $DESKTOP_FILE"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🎮 To run GeoChallenge:"
echo "   Command line: $DEPLOY_DIR/run_geochallenge.sh"
echo "   Or from file manager: double-click run_geochallenge.sh"
if [ -f "$HOME/.local/share/applications/geochallenge.desktop" ]; then
    echo "   Or from applications menu: GeoChallenge 3D Globe"
fi
echo ""
echo "🌍 Game Features:"
echo "   - 135+ cities across 4 difficulty levels"
echo "   - 3D Interactive Globe with click-to-guess"
echo "   - Real continent data from GeoPandas"
echo "   - Professional analytics with Pandas"
echo ""

# Ask if user wants to run now
echo -n "🚀 Run GeoChallenge now? (y/n): "
read run_now
if [[ "$run_now" =~ ^[Yy]$ ]]; then
    echo ""
    echo "🌍 Starting GeoChallenge 3D Globe Game..."
    ./run_geochallenge.sh
fi

echo ""
echo "📁 Installation location: $DEPLOY_DIR"
echo "👋 Thank you for playing GeoChallenge!"
