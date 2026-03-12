#!/usr/bin/env python3
"""
🌍 GeoChallenge Game - Simple Installer
Download + Install + Run EXE
"""

import os
import subprocess
import urllib.request
import zipfile
import sys

def download_file(url, filename):
    print(f"📥 Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    
def main():
    print("🌍 GeoChallenge Game - Simple Install")
    print("=" * 40)
    
    # Step 1: Download
    exe_url = "https://github.com/testgk/pandapandas/releases/latest/download/GeoChallenge.exe"
    
    try:
        print("📥 Downloading GeoChallenge.exe...")
        download_file(exe_url, "GeoChallenge.exe")
        print("✅ Download complete!")
        
        # Step 2: Run
        print("🚀 Starting GeoChallenge...")
        subprocess.run(["GeoChallenge.exe"])
        
    except Exception as e:
        print(f"❌ Download failed. Creating from source...")
        
        # Fallback: Clone and build
        print("📥 Cloning repository...")
        subprocess.run(["git", "clone", "https://github.com/testgk/pandapandas.git", "geochallenge-game"])
        
        os.chdir("geochallenge-game")
        
        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pandas", "geopandas", "panda3d", "pyinstaller"])
        
        # Build exe
        print("🔨 Building executable...")
        os.chdir("p3d")
        subprocess.run(["pyinstaller", "--onefile", "--name", "GeoChallenge", "globe_launcher.py"])
        
        # Run exe
        print("🚀 Starting GeoChallenge...")
        subprocess.run(["dist/GeoChallenge.exe"])

if __name__ == "__main__":
    main()
