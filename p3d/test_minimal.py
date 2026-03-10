"""
Minimal test for the globe application
"""
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *

class MinimalGlobe(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        print("✅ Panda3D initialized")

        # Black background
        self.setBackgroundColor(0, 0, 0)

        # Simple white sphere to test if rendering works
        from panda3d.core import CardMaker
        cm = CardMaker("test")
        cm.setFrame(-1, 1, -1, 1)
        card = self.render.attachNewNode(cm.generate())
        card.setColor(1, 1, 1, 1)  # White
        card.setPos(0, 10, 0)  # In front of camera

        print("✅ Created test geometry")
        print("🎯 You should see a white square on black background")
        print("💡 If you see this, Panda3D is working!")

if __name__ == "__main__":
    print("🧪 Testing minimal Panda3D setup...")
    try:
        app = MinimalGlobe()
        print("🚀 Starting Panda3D...")
        app.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
