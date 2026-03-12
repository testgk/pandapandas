#!/bin/bash
# GeoChallenge Game Launcher

REPO="https://github.com/testgk/pandapandas.git"
DEST="$(dirname "$0")/game"

# ── Clone if not already present ─────────────────────────────
if [ ! -d "$DEST/p3d" ]; then
    echo "Downloading game files..."
    git clone --depth 1 --progress "$REPO" "$DEST"
    if [ $? -ne 0 ]; then echo "ERROR: Download failed."; exit 1; fi
fi

# ── Create venv if not present ────────────────────────────────
if [ ! -d "$DEST/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$DEST/venv"
fi

# ── Activate venv ─────────────────────────────────────────────
source "$DEST/venv/bin/activate"

# ── Install deps ──────────────────────────────────────────────
echo "Checking dependencies..."
pip install panda3d geopandas numpy shapely matplotlib requests --quiet

# ── Launch ────────────────────────────────────────────────────
echo "Launching GeoChallenge 3D Globe..."
cd "$DEST/p3d"
python globe_launcher.py
