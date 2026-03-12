#!/usr/bin/env python3
"""
🌍 GeoChallenge Game - Universal Cross-Platform Installer
Automatically detects OS and runs appropriate deployment script
"""

import os
import sys
import platform
import subprocess
import urllib.request
import stat

def detect_os():
    """Detect the operating system"""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system in ['linux', 'darwin']:  # darwin is macOS
        return 'linux'  # Use Linux script for both Linux and macOS
    else:
        return 'unknown'

def download_file(url, filename):
    """Download a file from URL"""
    print(f"📥 Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        return True
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False

def make_executable(filename):
    """Make a file executable (Unix-like systems)"""
    try:
        current = stat.S_IMODE(os.lstat(filename).st_mode)
        os.chmod(filename, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return True
    except Exception as e:
        print(f"⚠️  Could not make {filename} executable: {e}")
        return False

def run_installer(script_name):
    """Run the deployment script"""
    print(f"🚀 Running {script_name}...")
    
    try:
        if script_name.endswith('.bat'):
            # Windows batch file
            result = subprocess.run([script_name], shell=True, capture_output=False)
        else:
            # Unix shell script
            result = subprocess.run([f'./{script_name}'], capture_output=False)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run installer: {e}")
        return False

def main():
    """Main installer function"""
    print("=" * 60)
    print("🌍 GeoChallenge Game - Universal Installer")
    print("=" * 60)
    print("")
    
    # Detect OS
    os_type = detect_os()
    print(f"🖥️  Detected OS: {platform.system()} ({platform.machine()})")
    
    if os_type == 'unknown':
        print(f"❌ Unsupported operating system: {platform.system()}")
        print("Supported systems: Windows, Linux, macOS")
        sys.exit(1)
    
    # Set up URLs and filenames
    base_url = "https://raw.githubusercontent.com/testgk/pandapandas/master/deploy/"
    
    if os_type == 'windows':
        script_name = "deploy_windows.bat"
        script_url = f"{base_url}deploy_windows.bat"
    else:
        script_name = "deploy_linux.sh"
        script_url = f"{base_url}deploy_linux.sh"
    
    print(f"📋 Will use: {script_name}")
    print("")
    
    # Check if script already exists
    if os.path.exists(script_name):
        print(f"📁 Found existing {script_name}")
        response = input(f"🔄 Re-download {script_name}? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            os.remove(script_name)
        else:
            print(f"✅ Using existing {script_name}")
    
    # Download script if needed
    if not os.path.exists(script_name):
        if not download_file(script_url, script_name):
            print(f"❌ Could not download deployment script")
            print(f"Please manually download: {script_url}")
            sys.exit(1)
    
    # Make executable on Unix-like systems
    if os_type != 'windows':
        make_executable(script_name)
    
    print("✅ Deployment script ready")
    print("")
    
    # Ask user if they want to run now
    response = input(f"🚀 Run GeoChallenge installer now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        print("")
        success = run_installer(script_name)
        
        if success:
            print("")
            print("🎉 Installation completed successfully!")
            print("🌍 GeoChallenge is ready to play!")
        else:
            print("")
            print("⚠️  Installation completed with some issues")
            print(f"💡 You can try running {script_name} manually")
    else:
        print("")
        print(f"📝 To install later, run: {script_name}")
        print("🌍 GeoChallenge deployment script is ready!")
    
    print("")
    print("🎮 Game Features:")
    print("   • 135+ cities across 4 difficulty levels")
    print("   • 3D Interactive Globe with click-to-guess")
    print("   • Real continent data from GeoPandas")
    print("   • Professional analytics with Pandas")
    print("")
    print("📁 GitHub: https://github.com/testgk/pandapandas")
    print("👋 Thank you for choosing GeoChallenge!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
