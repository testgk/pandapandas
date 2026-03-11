#!/bin/bash
# GeoPandas Globe - Nuitka Build Script for Linux

set -e

echo "========================================"
echo "🚀 Building GeoPandas Globe with Nuitka"
echo "🐧 Linux Optimized Executable"
echo "========================================"
echo

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"

echo "🔍 Checking virtual environment..."
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "⚙️  Virtual environment not found. Creating one at $VENV_PATH ..."
    python3 -m venv "$VENV_PATH"
    echo "✅ Virtual environment created"
fi

source "$VENV_PATH/bin/activate"
echo "✅ Virtual environment activated: $VIRTUAL_ENV"
echo

echo "🔍 Checking Python installation..."
PYTHON="$VENV_PATH/bin/python3"
if [ ! -f "$PYTHON" ]; then
    echo "❌ Python3 not found in virtual environment!"
    exit 1
fi

$PYTHON --version
echo "✅ Python available"
echo

echo "📁 Navigating to application directory..."
cd "$PROJECT_ROOT/p3d"
echo "Current directory: $(pwd)"

echo
echo "📦 Checking patchelf (required by Nuitka on Linux)..."
if ! command -v patchelf &> /dev/null; then
    echo "⚙️  Installing patchelf..."
    sudo apt install -y patchelf
    echo "✅ patchelf installed"
else
    echo "✅ patchelf already installed"
fi

echo
echo "📦 Installing project requirements..."
$PYTHON -m pip install -r "$PROJECT_ROOT/p3d/requirements.txt"
$PYTHON -m pip install setuptools
echo "✅ Requirements installed"

echo
echo "📦 Installing Nuitka with onefile support..."
$PYTHON -m pip install "Nuitka[onefile]"
echo "✅ Nuitka installed"

echo
echo "🧹 Cleaning previous builds..."
rm -rf globe_app.dist globe_app.build globe_app.onefile-build
rm -f geopandas-globe-nuitka

echo
echo "🚀 Building with Nuitka (this may take 5-10 minutes)..."
echo "💡 Nuitka compiles Python to C++ for better performance"

$PYTHON -m nuitka \
    --onefile \
    --follow-imports \
    --output-filename=geopandas-globe-nuitka \
    \
    --include-data-dir=world_data=world_data \
    --include-data-dir=settings=settings \
    \
    --include-package=panda3d \
    --include-package=direct \
    --include-package=geopandas \
    --include-package=shapely \
    --include-package=numpy \
    --include-package=matplotlib \
    --include-package=pandas \
    --include-package=pyproj \
    \
    --include-package-data=panda3d \
    --include-package-data=direct \
    --include-package-data=shapely \
    --include-package-data=pyproj \
    \
    --nofollow-import-to=tkinter \
    --nofollow-import-to=unittest \
    --nofollow-import-to=test \
    --nofollow-import-to=matplotlib \
    --nofollow-import-to=pandas \
    --jobs=4 \
    \
    globe_app.py

echo
if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    if [ -f "geopandas-globe-nuitka" ]; then
        echo "📁 Executable created: geopandas-globe-nuitka"
        ls -lh geopandas-globe-nuitka
        chmod +x geopandas-globe-nuitka
        echo
        echo "🚀 Testing the executable..."
        ./geopandas-globe-nuitka
    else
        echo "❌ Executable not found"
    fi
else
    echo "❌ Build failed! Check output above for errors."
fi

echo
echo "Press Enter to continue..."
read
