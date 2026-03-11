"""
Quick test to verify the improved continent shapes with proper Mediterranean Sea
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from world_data_manager import WorldDataManager
from main_fixed import ProperGlobe

def test_continents():
    print("🧪 Testing improved continent shapes...")

    # Test the WorldDataManager
    manager = WorldDataManager()
    continents = manager.get_continents()

    print(f"\n📊 Loaded continents: {list(continents.keys())}")

    # Check Europe specifically
    if 'Europe' in continents:
        europe = continents['Europe']
        print(f"\n🇪🇺 Europe analysis:")
        print(f"   - Type: {type(europe)}")

        if hasattr(europe, 'bounds'):
            bounds = europe.bounds
            print(f"   - Bounds: {bounds}")
            print(f"   - West-East: {bounds[0]:.1f}° to {bounds[2]:.1f}°")
            print(f"   - South-North: {bounds[1]:.1f}° to {bounds[3]:.1f}°")

            # Check if Mediterranean region is included
            if bounds[1] < 40 and bounds[3] > 60:  # Spans from Mediterranean to Northern Europe
                print("   ✅ Europe spans from Mediterranean to Northern regions")
            else:
                print("   ⚠️ Europe bounds might not include full Mediterranean region")

    print(f"\n🌍 Starting 3D globe to visualize...")
    return continents

def run_globe():
    print("🚀 Launching 3D Globe with improved continent shapes...")
    print("📍 Camera positioned to show Europe and Mediterranean Sea")
    print("🎯 Look for:")
    print("   - Red colored Europe")
    print("   - Mediterranean Sea gap between Europe and Africa")
    print("   - North at top, South at bottom")
    print("   - Mouse drag to orbit, wheel to zoom")

    try:
        app = ProperGlobe()
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # First test the data
    continents = test_continents()

    if continents:
        # Then run the 3D visualization
        run_globe()
    else:
        print("❌ No continent data loaded, cannot run 3D globe")
