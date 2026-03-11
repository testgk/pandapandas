#!/bin/bash
# GeoPandas Globe - Linux PyInstaller Build Script

set -e  # Exit on any error

echo "========================================"
echo "🏗️ GeoPandas Globe PyInstaller Build"
echo "🐧 Linux Standalone Executable"
echo "========================================"
echo

echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.8+"
    exit 1
fi

python3 --version
echo "✅ Python is available"
echo

echo "📦 Installing PyInstaller if not already installed..."
python3 -m pip install pyinstaller
if [ $? -ne 0 ]; then
    echo "❌ Failed to install PyInstaller!"
    exit 1
fi

echo
echo "📦 Installing required dependencies..."
python3 -m pip install panda3d geopandas shapely pandas matplotlib requests numpy pillow fiona pyproj rtree

echo
echo "🧹 Cleaning previous builds..."
rm -rf dist build

echo
echo "🏗️ Building Linux executable..."
echo "This may take several minutes..."
python3 -m PyInstaller globe_linux.spec

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    echo "Check the output above for errors"
    exit 1
fi

echo
echo "✅ Build completed successfully!"
echo

echo "📋 Build Results:"
if [ -f "dist/geopandas-globe-linux" ]; then
    echo "✅ Linux executable created: dist/geopandas-globe-linux"
    ls -lh dist/geopandas-globe-linux
    chmod +x dist/geopandas-globe-linux
else
    echo "❌ Executable not found in expected location"
    ls -la dist/
fi

echo
echo "🚀 Testing the executable..."
cd dist
if [ -f "geopandas-globe-linux" ]; then
    echo "Starting GeoPandas Globe..."
    ./geopandas-globe-linux
else
    echo "Executable not found for testing"
fi

echo
echo "========================================"
echo "🎯 Linux Build Complete!"
echo "========================================"
echo
echo "📁 Executable location: dist/geopandas-globe-linux"
echo "💡 You can distribute this file without requiring Python installation"
echo
