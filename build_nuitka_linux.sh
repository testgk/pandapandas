#!/bin/bash
# GeoPandas Globe - Nuitka Build Script for Linux

set -e

echo "========================================"
echo "🚀 Building GeoPandas Globe with Nuitka"
echo "🐧 Linux Optimized Executable"
echo "========================================"
echo

echo "📁 Navigating to application directory..."
cd p3d
echo "Current directory: $(pwd)"

echo
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

python3 --version
echo "✅ Python available"
echo

echo "📦 Installing Nuitka if needed..."
python3 -m pip install nuitka

echo
echo "🧹 Cleaning previous builds..."
rm -rf globe_app.dist globe_app.build globe_app.onefile-build
rm -f geopandas-globe-nuitka

echo
echo "🚀 Building with Nuitka (this may take 5-10 minutes)..."
echo "💡 Nuitka compiles Python to C++ for better performance"

python3 -m nuitka \
    --onefile \
    --include-data-dir=world_data=world_data \
    --include-data-dir=gui=gui \
    --include-data-dir=interfaces=interfaces \
    --include-data-dir=settings=settings \
    --follow-imports \
    --output-filename=geopandas-globe-nuitka \
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
