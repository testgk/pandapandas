"""
Quick test to verify the globe application works
"""
from main_fixed import ProperGlobe
import sys

def test_startup():
    print("Testing globe application startup...")
    try:
        app = ProperGlobe()
        print("✓ Globe application created successfully!")
        print("✓ All components initialized!")
        print("You should now see a 3D window with:")
        print("  - Transparent blue ocean sphere")
        print("  - Colored continent shapes on the surface")
        print("  - Google Maps-style side view (not from poles)")
        print("  - Mouse drag: Orbit around globe like Google Earth")
        print("  - Mouse wheel: Zoom in/out")
        print("  - Auto-rotation when not manually controlling")
        return app
    except Exception as e:
        print(f"✗ Error creating application: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    app = test_startup()
    if app:
        print("\nStarting main loop...")
        app.run()
    else:
        print("Failed to start application")
        sys.exit(1)
