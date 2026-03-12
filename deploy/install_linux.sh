#!/bin/bash
# 🌍 GeoChallenge - One-Line Linux/macOS Installer
echo "🌍 GeoChallenge Game - Quick Installer"
echo "Downloading installer..."
wget --show-progress -O install.py https://raw.githubusercontent.com/testgk/pandapandas/master/deploy/install.py
echo "Running installer..."
python3 install.py
