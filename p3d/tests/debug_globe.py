"""
Debug version of the globe application with file logging
"""
import sys
from pathlib import Path

# Create a log file
log_file = Path(__file__).parent / "debug.log"

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Redirect output to both terminal and file
sys.stdout = Logger(log_file)

print("🚀 Debug Globe Application Starting...")
print("📝 Output is being logged to debug.log")

try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import *
    from math import sin, cos, pi
    print("✅ Imports successful")

    class DebugGlobe(ShowBase):
        def __init__(self):
            print("🔧 Initializing Panda3D...")
            ShowBase.__init__(self)
            print("✅ Panda3D initialized")

            # Setup
            self.setBackgroundColor(0, 0, 0.2)  # Dark blue instead of black
            print("✅ Background color set")

            # Create a simple test sphere
            self.create_test_sphere()
            print("✅ Test sphere created")

            # Setup camera
            self.camera.setPos(0, -10, 0)
            self.camera.lookAt(0, 0, 0)
            print("✅ Camera positioned")

        def create_test_sphere(self):
            """Create a simple colored sphere to test rendering"""
            # Create sphere geometry
            geom = self.loader.loadModel("environment")  # Try to load a model
            if geom:
                geom.reparentTo(self.render)
                geom.setColor(1, 0, 0, 1)  # Red
                print("✅ Environment model loaded")
            else:
                # Fallback: create a simple colored card
                from panda3d.core import CardMaker
                cm = CardMaker("sphere")
                cm.setFrame(-2, 2, -2, 2)
                sphere = self.render.attachNewNode(cm.generate())
                sphere.setColor(0, 1, 0, 1)  # Green
                sphere.setPos(0, 5, 0)
                print("✅ Fallback card created")

    print("🎯 Creating globe application...")
    app = DebugGlobe()
    print("🚀 Starting main loop...")
    print("💡 Look for a window with colored geometry!")
    app.run()

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("📝 Check debug.log for full output")
