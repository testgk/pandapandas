#!/usr/bin/env python3
"""
Simple 3D Globe Launcher - Shows challenge on screen and allows clicking on globe
"""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def launch_globe_game():
    """Launch the 3D globe with clear challenge display"""
    print("🌍 Launching Interactive 3D Globe Challenge Game...")
    print("=" * 60)
    print("🎯 How to Play:")
    print("   1. Read the challenge question that appears on screen")
    print("   2. Click directly on the 3D globe where you think the location is")
    print("   3. Get instant feedback with your score and accuracy")
    print("   4. Use the GUI buttons to start new challenges")
    print("=" * 60)
    
    try:
        # Import and run the globe application
        from globe_app import RealGlobeApplication
        
        print("🚀 Starting 3D Globe Application...")
        print("📍 The challenge question will appear in the game window")
        print("🖱️  Click anywhere on the 3D Earth to make your guess!")
        
        # Create and run the application
        app = RealGlobeApplication()
        app.run()
        
    except Exception as e:
        print(f"❌ Error starting globe game: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Troubleshooting:")
        print("   • Make sure you're in the p3d directory")
        print("   • Check that Panda3D is installed: pip install panda3d")
        print("   • Try: cd D:\\geopandas\\p3d && python globe_launcher.py")

if __name__ == "__main__":
    launch_globe_game()
