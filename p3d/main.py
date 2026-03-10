"""
Simple runner for the 3D globe application
"""
from globe_app import GlobeApp

if __name__ == "__main__":
    print("Starting 3D Globe with GeoPandas world data...")
    print("Controls:")
    print("- Mouse drag: Orbit camera")
    print("- Mouse wheel: Zoom in/out")
    print("- Auto-rotation when not dragging")

    app = GlobeApp()
    app.run()
